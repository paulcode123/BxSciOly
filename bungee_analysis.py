import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import curve_fit

# Physics Constants
G = 9.8
BOTTLE_HEIGHT = 30.0  # cm
TARGET_DIST = 2.0     # cm
GAMMA = 0.95          # Amplitude decay ratio
DT = 0.002            # s

# BxS1 Polynomial Coefficients for F(strain) = as^3 + bs^2 + cs + d
COEFFS = [0.648409, -2.539174, 3.68841, 0.059985]
DERIV_COEFFS = [1.945226, -5.078347, 3.68841]

def get_force(strain):
    """Calculates force (N) given strain (fractional extension)"""
    return COEFFS[0]*strain**3 + COEFFS[1]*strain**2 + COEFFS[2]*strain + COEFFS[3]

def get_k_eff(strain):
    """Calculates effective stiffness k = dF/dx = (dF/ds) / L"""
    # Note: This is dF/ds. To get k in N/cm, divide by L.
    return DERIV_COEFFS[0]*strain**2 + DERIV_COEFFS[1]*strain + DERIV_COEFFS[2]

def get_strain_for_force(target_force):
    """Finds strain for a given force using Newton's method"""
    s = 0.5 # Initial guess
    for _ in range(5):
        f = get_force(s)
        df = DERIV_COEFFS[0]*s**2 + DERIV_COEFFS[1]*s + DERIV_COEFFS[2]
        s = s - (f - target_force) / df
    return max(0, s)

def simulate_min_height(height_cm, mass_g, cord_length_cm, bottle_height_cm, gamma):
    """Simulates the drop and returns the minimum height achieved by the bottle"""
    mass_kg = mass_g / 1000.0
    y = height_cm - bottle_height_cm  # Bottle bottom height
    v = 0.0
    min_y = y
    
    # Calculate damping
    s_eq = get_strain_for_force(mass_kg * G)
    k_eff_s = get_k_eff(s_eq) # dF/ds
    k_eff_si = (k_eff_s / cord_length_cm) * 100.0 # N/m
    
    zeta = -np.log(gamma) / np.pi
    damping_coeff = 2 * zeta * np.sqrt(mass_kg * k_eff_si)
    
    # Simulation
    t = 0
    while t < 5.0:
        # Distance from top to bottle top
        cord_top = height_cm
        bottle_top = y + bottle_height_cm
        total_dist = cord_top - bottle_top
        extension = max(0, total_dist - cord_length_cm)
        
        net_force = -mass_kg * G
        if extension > 0:
            strain = extension / cord_length_cm
            net_force += get_force(strain)
            net_force -= damping_coeff * (v / 100.0) # v is cm/s, need m/s
            
        accel = (net_force / mass_kg) * 100.0 # cm/s^2
        v += accel * DT
        y += v * DT
        
        if y < min_y:
            min_y = y
            
        # Stop at first bounce
        if t > 0.2 and v > 0:
            break
        t += DT
        
    return min_y

def calculate_l(m_g, h_m):
    """Finds the required cord length L for a given mass and drop height"""
    height_cm = h_m * 100.0
    y_release = height_cm - BOTTLE_HEIGHT
    
    # Binary search for L
    low = 1.0
    high = y_release - TARGET_DIST
    
    for _ in range(20):
        mid = (low + high) / 2.0
        min_h = simulate_min_height(height_cm, m_g, mid, BOTTLE_HEIGHT, GAMMA)
        
        if min_h > TARGET_DIST:
            low = mid
        else:
            high = mid
            
    return (low + high) / 2.0

def fitted_function(X, a, b, c, d, e, f):
    m, h = X
    # A physical-inspired model: L = h - sqrt(m*h/k)
    # Plus some corrections
    return a * h + b * np.sqrt(m * h) + c * m + d * h**2 + e * m**2 + f

def main():
    print("Generating bungee drop data points...")
    masses = np.linspace(100, 600, 5) # 5 points
    heights = np.linspace(2, 8, 5)   # 5 points
    
    data = []
    for m in masses:
        for h in heights:
            l = calculate_l(m, h)
            data.append([m, h, l])
            print(f"m={m:3.0f}g, h={h:3.1f}m -> L={l:6.2f}cm")
            
    df = pd.DataFrame(data, columns=['m', 'h', 'l'])
    df.to_csv('bungee_dataset.csv', index=False)
    print("\nData saved to bungee_dataset.csv")
    
    # Fit function
    X = (df['m'].values, df['h'].values)
    y = df['l'].values
    popt, _ = curve_fit(fitted_function, X, y)
    
    print("\nFitted Function Parameters:")
    names = ['a', 'b', 'c', 'd', 'e', 'f']
    for name, val in zip(names, popt):
        print(f"  {name} = {val:e}")
        
    # Output the formula
    formula = f"L(m, h) = {popt[0]:.4f}*h + {popt[1]:.4f}*sqrt(m*h) + {popt[2]:.4f}*m + {popt[3]:.4e}*h^2 + {popt[4]:.4e}*m^2 + {popt[5]:.4f}"
    print(f"\nFitted Formula:\n{formula}")
    
    # 3D Plot
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot original data
    ax.scatter(df['m'], df['h'], df['l'], c='r', marker='o', label='Simulation Data')
    
    # Plot fitted surface
    m_grid, h_grid = np.meshgrid(np.linspace(100, 600, 30), np.linspace(2, 8, 30))
    l_grid = fitted_function((m_grid, h_grid), *popt)
    ax.plot_surface(m_grid, h_grid, l_grid, alpha=0.3, cmap='viridis')
    
    ax.set_xlabel('Mass (g)')
    ax.set_ylabel('Height (m)')
    ax.set_zlabel('Cord Length L (cm)')
    ax.set_title('Bungee Drop Calibration: L(m, h)')
    ax.legend()
    
    plt.savefig('bungee_plot.png')
    print("\nGraph saved to bungee_plot.png")
    # plt.show()

if __name__ == "__main__":
    main()
