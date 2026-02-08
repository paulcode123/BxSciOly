import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d, CubicSpline
import matplotlib.pyplot as plt
import io
import base64

def get_interpolator(calibration_data, method):
    """
    Returns a function f(strain) -> force based on calibration data and method.
    """
    if not calibration_data:
        return lambda s: 0
    
    strains = [p['strain'] for p in calibration_data]
    forces = [p['force'] for p in calibration_data]
    
    # Sort by strain
    sorted_indices = np.argsort(strains)
    strains = np.array(strains)[sorted_indices]
    forces = np.array(forces)[sorted_indices]
    
    if method == 'linear':
        return interp1d(strains, forces, kind='linear', fill_value='extrapolate')
    elif method == 'spline' and len(strains) >= 4:
        return CubicSpline(strains, forces, bc_type='natural', extrapolate=True)
    elif method.startswith('polynomial'):
        degree = 3
        if method == 'polynomial2': degree = 2
        coeffs = np.polyfit(strains, forces, degree)
        poly = np.poly1d(coeffs)
        return poly
    else:
        # Fallback to linear
        return interp1d(strains, forces, kind='linear', fill_value='extrapolate')

def simulate_min_height(height_cm, mass_g, cord_length_cm, bottle_height_cm, gamma, force_fn, k_eff_fn):
    """Simulates the drop and returns the minimum height achieved by the bottle"""
    g = 9.8
    dt = 0.002
    mass_kg = mass_g / 1000.0
    y = height_cm - bottle_height_cm  # Bottle bottom height
    v = 0.0
    min_y = y
    
    # Calculate damping
    # We need k_eff at equilibrium strain
    # s_eq is strain where force_fn(s_eq) = mass_kg * g
    # We can find this by root finding or simple search since force is monotonic
    s_vals = np.linspace(0, 5.0, 500)
    f_vals = force_fn(s_vals)
    s_eq = np.interp(mass_kg * g, f_vals, s_vals)
    
    # dF/ds at s_eq
    ds = 0.01
    f1 = force_fn(s_eq)
    f2 = force_fn(s_eq + ds)
    k_eff_s = (f2 - f1) / ds # dF/ds
    
    k_eff_si = (k_eff_s / cord_length_cm) * 100.0 # N/m
    
    zeta = -np.log(max(0.01, gamma)) / np.pi
    damping_coeff = 2 * zeta * np.sqrt(mass_kg * k_eff_si)
    
    t = 0
    while t < 5.0:
        cord_top = height_cm
        bottle_top = y + bottle_height_cm
        total_dist = cord_top - bottle_top
        extension = max(0, total_dist - cord_length_cm)
        
        net_force = -mass_kg * g
        if extension > 0:
            strain = extension / cord_length_cm
            net_force += force_fn(strain)
            net_force -= damping_coeff * (v / 100.0)
            
        accel = (net_force / mass_kg) * 100.0
        v += accel * dt
        y += v * dt
        
        if y < min_y:
            min_y = y
        if t > 0.2 and v > 0:
            break
        t += dt
        
    return min_y

def calculate_l(m_g, h_m, force_fn, bottle_height, target_dist, gamma):
    height_cm = h_m * 100.0
    y_release = height_cm - bottle_height
    
    low = 1.0
    high = y_release - target_dist
    
    # Increase iterations for export precision
    for _ in range(25): 
        mid = (low + high) / 2.0
        min_h = simulate_min_height(height_cm, m_g, mid, bottle_height, gamma, force_fn, None)
        
        if min_h > target_dist:
            low = mid
        else:
            high = mid
            
    return (low + high) / 2.0

def fitted_model(X, *p):
    m, h = X
    # Bivariate quartic polynomial: 15 terms
    # 0:1, 1:m, 2:h, 3:m^2, 4:h^2, 5:mh, 6:m^3, 7:h^3, 8:m^2h, 9:mh^2, 10:m^4, 11:h^4, 12:m^3h, 13:m^2h^2, 14:mh^3
    return (p[0] + p[1]*m + p[2]*h + 
            p[3]*m**2 + p[4]*h**2 + p[5]*m*h + 
            p[6]*m**3 + p[7]*h**3 + p[8]*m**2*h + p[9]*m*h**2 +
            p[10]*m**4 + p[11]*h**4 + p[12]*m**3*h + p[13]*m**2*h**2 + p[14]*m*h**3)

def calculate_l(m_g, h_m, force_fn, gamma):
    """
    h_m is the 'Free Space' distance (Total Height - Bottle Height - Target)
    We find L such that L + X = h_m
    """
    height_cm = h_m * 100.0
    low = 1.0
    high = height_cm
    for _ in range(25): 
        mid = (low + high) / 2.0
        # In this simplified model, bottle bottom starts at top and falls to height_cm
        min_h = simulate_min_height(height_cm, m_g, mid, 0, gamma, force_fn, None)
        if min_h > 0: low = mid # Too high
        else: high = mid # Too low
    return (low + high) / 2.0

def generate_bungee_export(calibration_data, method, gamma, bottle_height=30.0, target_dist=0.0):
    force_fn = get_interpolator(calibration_data, method)
    # Train on Free Space (h) from 1m to 8m
    mass_range = np.linspace(100, 600, 12) 
    height_range = np.linspace(1, 8, 12) 
    results = []
    for m in mass_range:
        for h in height_range:
            l = calculate_l(m, h, force_fn, gamma)
            results.append({'m': float(m), 'h': float(h), 'l': float(l)})
    df = pd.DataFrame(results)
    m_raw = df['m'].values
    h_raw = df['h'].values
    y = df['l'].values
    
    # Build a 5th degree bivariate polynomial basis (21 terms)
    A_raw = []
    terms_meta = []
    for i in range(6): # degree m
        for j in range(6 - i): # degree h
            A_raw.append((m_raw**i) * (h_raw**j))
            terms_meta.append((i, j))
    A_raw = np.array(A_raw).T
    
    # COLUMN PRECONDITIONING: Scale columns to have max norm of 1
    # This is the "Secret Sauce" for high-degree polynomial stability.
    col_scales = np.max(np.abs(A_raw), axis=0)
    col_scales[col_scales == 0] = 1.0 # Avoid div by zero
    A_scaled = A_raw / col_scales
    
    # Use SVD solver on the scaled (perfectly conditioned) matrix
    popt_scaled, _, _, _ = np.linalg.lstsq(A_scaled, y, rcond=None)
    
    # Convert coefficients back to RAW units algebraically
    popt_raw = popt_scaled / col_scales
    
    predicted_l = A_raw @ popt_raw
    residuals = np.abs(y - predicted_l)
    avg_error = float(np.mean(residuals))
    max_error = float(np.max(residuals))
    
    # Construct formula string using RAW coefficients
    formula_parts = []
    for coeff, (m_deg, h_deg) in zip(popt_raw, terms_meta):
        if abs(coeff) < 1e-18: continue
        
        s_coeff = f"{coeff:.4f}" if abs(coeff) > 0.001 else f"{coeff:.4e}"
        if m_deg == 0 and h_deg == 0:
            formula_parts.append(s_coeff)
        else:
            term = ""
            if m_deg > 0: term += f"m^{m_deg}" if m_deg > 1 else "m"
            if h_deg > 0: 
                if term: term += "*"
                term += f"h^{h_deg}" if h_deg > 1 else "h"
            formula_parts.append(f"{s_coeff}*{term}")

    formula = "L(m, h) = " + " + ".join(formula_parts)
    
    # Surface for Plotly
    m_surf = np.linspace(100, 600, 25)
    h_surf = np.linspace(2, 8, 25)
    m_grid, h_grid = np.meshgrid(m_surf, h_surf)
    
    l_grid = np.zeros_like(m_grid)
    for coeff, (m_deg, h_deg) in zip(popt_raw, terms_meta):
        l_grid += coeff * (m_grid**m_deg) * (h_grid**h_deg)
    
    return {
        'points': results,
        'formula': formula,
        'avg_error': avg_error,
        'max_error': max_error,
        'parameters': popt_raw.tolist(),
        'surface': {
            'm': m_surf.tolist(),
            'h': h_surf.tolist(),
            'l': l_grid.tolist()
        }
    }
