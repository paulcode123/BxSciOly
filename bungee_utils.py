import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d, CubicSpline

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
    elif method == 'power':
        def power_func(s, a, b):
            return a * np.power(s, b)
        try:
            # Filter s > 0 for power fit to avoid log(0) issues if used internally by curve_fit
            mask = strains > 0
            if np.sum(mask) < 2: return interp1d(strains, forces, kind='linear', fill_value='extrapolate')
            popt, _ = curve_fit(power_func, strains[mask], forces[mask], p0=[10, 1.5], maxfev=2000)
            return lambda s: power_func(s, *popt)
        except:
            return interp1d(strains, forces, kind='linear', fill_value='extrapolate')
    elif method == 'exponential':
        def exp_func(s, a, b):
            return a * (np.exp(b * s) - 1)
        try:
            popt, _ = curve_fit(exp_func, strains, forces, p0=[1, 1], maxfev=2000)
            return lambda s: exp_func(s, *popt)
        except:
            return interp1d(strains, forces, kind='linear', fill_value='extrapolate')
    elif method == 'logarithmic':
        def log_func(s, a, b):
            return a * np.log(b * s + 1)
        try:
            popt, _ = curve_fit(log_func, strains, forces, p0=[10, 1], maxfev=2000)
            return lambda s: log_func(s, *popt)
        except:
            return interp1d(strains, forces, kind='linear', fill_value='extrapolate')
    elif method == 'rational':
        def rat_func(s, a, b):
            return (a * s) / (b + s)
        try:
            popt, _ = curve_fit(rat_func, strains, forces, p0=[100, 1], maxfev=2000)
            return lambda s: rat_func(s, *popt)
        except:
            return interp1d(strains, forces, kind='linear', fill_value='extrapolate')
    elif method == 'hill':
        # Hill equation for Strain Saturation: s(F) = a * F^n / (b^n + F^n)
        # This models a cord that has a maximum stretch 'a' and stiffens as it reaches it.
        # We invert this to get Force: F(s) = b * (s / (a - s))^(1/n)
        def s_model(f, a, b, n):
            f_safe = np.maximum(f, 1e-12)
            return a * np.power(f_safe, n) / (np.power(b, n) + np.power(f_safe, n))
        
        try:
            mask = (forces > 0) & (strains > 0)
            if np.sum(mask) < 3:
                return interp1d(strains, forces, kind='linear', fill_value='extrapolate')
            
            # Initial guesses: a (max strain), b (force at half-max strain), n (steepness)
            a0 = float(np.max(strains) * 1.5)
            b0 = float(np.median(forces[mask]))
            n0 = 2.0
            
            popt, _ = curve_fit(
                s_model, forces[mask], strains[mask],
                p0=[a0, b0, n0],
                bounds=([0.1, 0.1, 0.5], [10.0, 50.0, 10.0]),
                maxfev=5000
            )
            a, b, n = popt
            
            def force_from_strain(s):
                s_arr = np.asarray(s, dtype=float)
                # F(s) = b * (s / (a - s))^(1/n)
                # Clamp s to avoid division by zero at the asymptote 'a'
                s_safe = np.clip(s_arr, 1e-12, a * 0.995)
                f = b * np.power(s_safe / (a - s_safe), 1.0/n)
                
                # Linear extrapolation for strains near or beyond the asymptote
                mask_high = s_arr >= a * 0.995
                if np.any(mask_high):
                    s1 = a * 0.99
                    s2 = a * 0.995
                    f1 = b * np.power(s1 / (a - s1), 1.0/n)
                    f2 = b * np.power(s2 / (a - s2), 1.0/n)
                    slope = (f2 - f1) / (s2 - s1)
                    f[mask_high] = f2 + slope * (s_arr[mask_high] - s2)
                
                return np.where(s_arr <= 0, 0.0, f)
                
            return force_from_strain
        except Exception:
            return interp1d(strains, forces, kind='linear', fill_value='extrapolate')
    elif method.startswith('polynomial'):
        degree = 3
        if method == 'polynomial2': degree = 2
        coeffs = np.polyfit(strains, forces, degree)
        poly = np.poly1d(coeffs)
        return poly
    else:
        # Fallback to linear
        return interp1d(strains, forces, kind='linear', fill_value='extrapolate')

def simulate_min_height(height_cm, mass_g, cord_length_cm, bottle_height_cm, gamma, force_fn, k_eff_fn, area_m2=0.0045, cd=1.0):
    """Simulates the drop and returns the minimum height achieved by the bottle"""
    g = 9.8
    rho = 1.225 # Air density kg/m3
    dt = 0.003  # Slightly coarser for export performance (App Engine timeout)
    mass_kg = mass_g / 1000.0
    y = height_cm - bottle_height_cm  # Bottle bottom height
    v = 0.0
    min_y = y
    
    # Calculate damping
    # We need k_eff at equilibrium strain
    # s_eq is strain where force_fn(s_eq) = mass_kg * g
    s_vals = np.linspace(0, 5.0, 250)  # Reduced for export performance
    f_vals = force_fn(s_vals)
    # np.interp requires xp (f_vals) to be monotonically increasing; sort if needed
    sort_idx = np.argsort(f_vals)
    f_sorted = f_vals[sort_idx]
    s_sorted = s_vals[sort_idx]
    s_eq = np.clip(np.interp(mass_kg * g, f_sorted, s_sorted), 0.001, 4.99)
    
    # dF/ds at s_eq
    ds = 0.01
    f1 = force_fn(s_eq)
    f2 = force_fn(s_eq + ds)
    k_eff_s = (f2 - f1) / ds  # dF/ds
    
    k_eff_si = (k_eff_s / max(cord_length_cm, 1.0)) * 100.0  # N/m
    k_eff_si = max(k_eff_si, 0.1)  # Ensure positive for sqrt; avoid NaN
    
    zeta = -np.log(max(0.01, gamma)) / np.pi
    damping_coeff = 2 * zeta * np.sqrt(mass_kg * k_eff_si)
    
    t = 0
    while t < 5.0:
        cord_top = height_cm
        bottle_top = y + bottle_height_cm
        total_dist = cord_top - bottle_top
        extension = max(0, total_dist - cord_length_cm)
        
        net_force = -mass_kg * g
        
        # 1. Quadratic Air Drag
        v_m_s = v / 100.0
        drag_force = 0.5 * rho * cd * area_m2 * v_m_s * abs(v_m_s)
        net_force -= drag_force
        
        if extension > 0:
            strain = extension / cord_length_cm
            net_force += force_fn(strain)
            # 2. Linear Internal Damping (Viscosity)
            net_force -= damping_coeff * v_m_s
            
        accel = (net_force / mass_kg) * 100.0
        v += accel * dt
        y += v * dt
        
        if y < min_y:
            min_y = y
        if t > 0.2 and v > 0:
            break
        t += dt
        
    return min_y

def calculate_l(m_g, h_m, force_fn, bottle_height, target_dist, gamma, area_m2=0.0045, cd=1.0):
    height_cm = h_m * 100.0
    y_release = height_cm - bottle_height
    
    low = 1.0
    high = y_release - target_dist
    
    # Increase iterations for export precision
    for _ in range(25): 
        mid = (low + high) / 2.0
        min_h = simulate_min_height(height_cm, m_g, mid, bottle_height, gamma, force_fn, None, area_m2, cd)
        
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

def calculate_l_freespace(m_g, h_m, force_fn, gamma, area_m2=0.0045, cd=1.0):
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
        min_h = simulate_min_height(height_cm, m_g, mid, 0, gamma, force_fn, None, area_m2, cd)
        if min_h > 0: low = mid # Too high
        else: high = mid # Too low
    return (low + high) / 2.0

def generate_bungee_export(calibration_data, method, gamma, bottle_height=30.0, target_dist=0.0, area_m2=0.0045, cd=1.0):
    force_fn = get_interpolator(calibration_data, method)
    # Train on Free Space (h) from 1m to 8m (8x8 grid for App Engine timeout safety)
    mass_range = np.linspace(100, 600, 8) 
    height_range = np.linspace(1, 8, 8) 
    results = []
    for m in mass_range:
        for h in height_range:
            l = calculate_l_freespace(m, h, force_fn, gamma, area_m2, cd)
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
    
    # Generate 2D cross-sections
    # 1. Length vs Mass at h=1m
    m_axis = np.linspace(100, 600, 50)
    h_fixed = 1.0
    l_at_h1 = np.zeros_like(m_axis)
    for coeff, (m_deg, h_deg) in zip(popt_raw, terms_meta):
        l_at_h1 += coeff * (m_axis**m_deg) * (h_fixed**h_deg)
    
    # 2. Strain vs Mass (Strain = (H-L)/L)
    # Since peak strain is independent of H, we can use any H.
    # We'll use h=1m: strain = (1.0 - L)/L; guard against division by zero
    l_safe = np.where(np.abs(l_at_h1) < 1e-6, 1e-6, l_at_h1)
    strain_at_h1 = (100.0 - l_at_h1) / l_safe  # Lengths are in cm, H=100cm
    strain_at_h1 = np.clip(strain_at_h1 * 100, -1e6, 1e6)  # Convert to %, clamp inf/nan
    
    def to_json_safe(arr):
        """Convert numpy array to JSON-serializable list, replacing nan/inf."""
        a = np.asarray(arr)
        flat = a.ravel()
        return [float(x) if np.isfinite(x) else 0.0 for x in flat] if a.ndim == 1 else [
            [float(x) if np.isfinite(x) else 0.0 for x in row] for row in a
        ]
    
    return {
        'points': results,
        'formula': formula,
        'avg_error': float(avg_error) if np.isfinite(avg_error) else 0.0,
        'max_error': float(max_error) if np.isfinite(max_error) else 0.0,
        'parameters': to_json_safe(popt_raw),
        'surface': {
            'm': to_json_safe(m_surf),
            'h': to_json_safe(h_surf),
            'l': to_json_safe(l_grid)
        },
        'analytical': {
            'm': to_json_safe(m_axis),
            'l_at_h1': to_json_safe(l_at_h1),
            'strain': to_json_safe(strain_at_h1)
        }
    }
