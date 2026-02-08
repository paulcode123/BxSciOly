# CIRCUIT LAB STUDY BINDER - COMPLETE REFERENCE GUIDE
**Version 1.0 - Optimized for Quick Lookup During Tests**

---

## TABLE OF CONTENTS (Quick Navigation)

1. **ESSENTIAL FORMULAS & EQUATIONS**
   - 1.1 DC Circuit Fundamentals
   - 1.2 AC Circuit Formulas
   - 1.3 Electromagnetic Formulas
   - 1.4 Component-Specific Formulas
   - 1.5 Power and Energy

2. **COMPONENT SPECIFICATIONS & IDENTIFICATION**
   - 2.1 Resistors
   - 2.2 Capacitors
   - 2.3 Inductors
   - 2.4 Diodes and LEDs
   - 2.5 Transistors
   - 2.6 Transformers

3. **QUICK REFERENCE TABLES**
   - 3.1 Common Values and Constants
   - 3.2 Standard Resistor Values
   - 3.3 Household AC Standards
   - 3.4 Scientists and Units
   - 3.5 Component Symbols

4. **PROBLEM-SOLVING FRAMEWORKS**
   - 4.1 Circuit Analysis Strategy
   - 4.2 Equivalent Resistance Method
   - 4.3 AC Circuit Analysis
   - 4.4 Time Constant Applications

5. **VISUAL GUIDES & MENTAL MODELS**
   - 5.1 RC Circuit Behavior
   - 5.2 Right-Hand Rule (3 Contexts)
   - 5.3 Series vs. Parallel Comparison
   - 5.4 AC Sine Wave Reference
   - 5.5 Transformer Operation

6. **COMMON PITFALLS & TIPS**
   - 6.1 Formula Misapplication
   - 6.2 Circuit Analysis Errors
   - 6.3 Unit Conversion Mistakes
   - 6.4 Safety and Practical Tips

7. **TEST-SPECIFIC STRATEGIES**
   - 7.1 Rickards Test Focus
   - 7.2 Hawk&Hornet Test Focus
   - 7.3 UGA Test Focus
   - 7.4 UT Austin Test Focus
   - 7.5 MVSO Test Focus

8. **DERIVATION QUICK-REFS (For Advanced Questions)**
   - 8.1 Voltage Divider Derivation
   - 8.2 Time Constant Derivation
   - 8.3 Transformer EMF Derivation

---

## SECTION 1: ESSENTIAL FORMULAS & EQUATIONS

### SECTION 1.1: DC CIRCUIT FUNDAMENTALS

#### OHM'S LAW (The most important formula):
```
V = IR
I = V/R
R = V/I
```

Units: V (volts), I (amperes), R (ohms)

#### POWER EQUATIONS (All three forms):
```
P = VI          [voltage × current]
P = I²R         [current² × resistance]
P = V²/R        [voltage² / resistance]
```

**NOT VALID:** `P = V²R` (common error!)

Units: P in Watts (W)

> **[ADD IMAGE: Power Triangle - Shows relationship between P, V, I, R with three formulas in a triangle format and visual examples of power dissipation in resistors]**

#### ENERGY AND WORK:
```
W = VIt         [work = voltage × current × time]
W = V²t/R       [alternative form]
E = Pt          [energy = power × time]
```

Units: W, E in Joules (J); t in seconds

#### CURRENT DEFINITIONS:
```
I = Q/t         [charge / time]
I = nAvde       [charge density × area × drift velocity × electron charge]
I = J·A         [current density × area]
```

**NOT VALID:** `I = ie` (common error!)

#### RESISTANCE RELATIONSHIPS:
```
R = ρL/A        [resistivity × length / cross-sectional area]
```

- ρ = resistivity (material property, Ω·m)
- L = length of conductor (m)
- A = cross-sectional area (m²)

Memory aid: "Longer wire = bigger R, thicker wire = smaller R"

#### SERIES CIRCUITS:
```
R_eq = R₁ + R₂ + R₃ + ...
I_total = I_each (same current everywhere)
V_total = V₁ + V₂ + V₃ + ... (voltages add)
```

> **[ADD IMAGE: Series Circuit Diagram - Battery connected to 3 resistors in series, showing current flow arrows and voltage drop across each resistor, labeled V₁, V₂, V₃]**

#### PARALLEL CIRCUITS:
```
1/R_eq = 1/R₁ + 1/R₂ + 1/R₃ + ...
V_across = V_each (same voltage everywhere)
I_total = I₁ + I₂ + I₃ + ... (currents add)
```

> **[ADD IMAGE: Parallel Circuit Diagram - Battery connected to 3 resistors in parallel, showing voltage same across each branch and current splitting I₁, I₂, I₃]**

- Special case (2 resistors): `R_eq = (R₁ × R₂)/(R₁ + R₂)`
- Special case (N identical resistors): `R_eq = R/N`

#### VOLTAGE DIVIDER (Series resistors):
```
V_out = V_in × R₂/(R₁ + R₂)
```

Where R₂ is the "bottom" resistor (connected to ground)

- Current through divider: `I = V_in/(R₁ + R₂)`
- Power dissipation: `P_total = V_in²/(R₁ + R₂)`

> **[ADD IMAGE: Voltage Divider Circuit - R1 on top, R2 on bottom, showing Vin input and Vout tap]**

---

### SECTION 1.2: AC CIRCUIT FORMULAS

#### RMS vs. PEAK CONVERSION:
```
V_RMS = V_peak / √2
V_peak = V_RMS × √2 ≈ V_RMS × 1.414

I_RMS = I_peak / √2
```

Household AC: 120V RMS = 170V peak (120 × 1.414)

> **[ADD IMAGE: AC Sine Wave showing 120V RMS, 170V peak, 340V peak-to-peak, 60Hz, 16.7ms period]**

#### AC FREQUENCY & PERIOD:
```
f = 1/T         [frequency = 1 / period]
T = 1/f
ω = 2πf         [angular frequency in rad/s]
```

North America: f = 60 Hz, so T = 1/60 ≈ 16.7 ms

#### IMPEDANCE (Complex quantity):
```
Z = R + jX      (complex form)
|Z| = √(R² + X²) (magnitude)
```

- Capacitive reactance: `X_C = 1/(ωC) = 1/(2πfC)`
- Inductive reactance: `X_L = ωL = 2πfL`
- Phase angle: `φ = arctan(X/R)`

#### RESONANT FREQUENCY (LC circuits):
```
f = 1/(2π√(LC))
ω = 1/√(LC)
```

At resonance, impedance is minimum (if resistive)

#### TIME CONSTANTS:

> **[ADD IMAGE: RC Circuit with battery, resistor, capacitor, and switch]**

**RC Circuits:** `τ = RC`
- Charging: `V(t) = V₀(1 - e^(-t/τ))`
- Discharging: `V(t) = V₀e^(-t/τ)`
- Current during charging: `I(t) = (V₀/R)e^(-t/τ)`
- Time to ~63% charge: 1τ
- Time to ~95% charge: 3τ
- Time to ~99% charge: 5τ

**RL Circuits:** `τ = L/R`
- Current rise: `I(t) = I₀(1 - e^(-t/τ))`
- Time to ~63% current: 1τ
- Time to steady-state: ~5τ

---

### SECTION 1.3: ELECTROMAGNETIC FORMULAS

#### MAGNETIC FIELD (Straight wire):
```
B = μ₀I/(2πr)
```

- μ₀ = 4π × 10⁻⁷ T·m/A (permeability of free space)
- r = distance from wire
- Field forms concentric circles (right-hand rule)

> **[ADD IMAGE: Magnetic field around straight wire - Top view showing concentric circles of field lines with right-hand rule hand demonstration showing thumb = current, fingers = field direction]**

#### MAGNETIC FIELD (Solenoid):
```
B = μ₀nI
```

- n = N/L (turns per unit length)
- N = total number of turns
- L = length of solenoid
- Field is uniform inside

> **[ADD IMAGE: Solenoid diagram showing coil with magnetic field lines running through center, labeled with N turns, length L, current I, and resulting field B]**

#### MAGNETIC FORCE (Moving charge):
```
F = q(v × B) = qvB sin(θ)
```

- Direction: Right-hand rule (v × B)
- For electrons (negative charge): Reverse direction
- If v ⊥ B: `F = qvB` (maximum)
- If v ∥ B: `F = 0` (no force)

> **[ADD IMAGE: Lorentz Force Diagram - Charge moving through magnetic field with velocity vector, field vector, and resulting force vector shown with 3D arrows and right-hand rule demonstration]**

#### MAGNETIC FORCE (Current-carrying wire):
```
F = IL × B
```

- L = length of wire
- Direction: Right-hand rule (I × B)

> **[ADD IMAGE: Current-carrying wire with magnetic field, showing force direction using right-hand rule]**

#### MAGNETIC FLUX:
```
Φ_B = B·A = BAcos(θ)
```

- Maximum flux: θ = 0° (B perpendicular to area)
- Zero flux: θ = 90° (B parallel to area)
- Units: Weber (Wb) = T·m²

#### FARADAY'S LAW (Induction):
```
ε = -N(dΦ/dt)
```

For constant flux change: `ε = -N(ΔΦ/Δt)`

- N = number of turns
- Negative sign: Lenz's law (opposes change)

#### COULOMB'S LAW:
```
F = kq₁q₂/r²
```

- k = 8.99 × 10⁹ N·m²/C² (Coulomb constant)
- r = distance between charges
- Inverse square law: 1/r² dependence
- Force is repulsive for like charges, attractive for opposite

#### ELECTRIC FIELD (Point charge):
```
E = kq/r²
```

- Field points away from positive charge, toward negative
- Units: V/m or N/C

---

### SECTION 1.4: COMPONENT-SPECIFIC FORMULAS

#### RESISTOR POWER DISSIPATION:
```
P = I²R
P = V²/R
P = VI
```

Thermal failure occurs when P exceeds power rating

#### CAPACITOR BEHAVIOR:
```
Q = CV        [charge = capacitance × voltage]
C = ε₀εᵣA/d   [parallel plate capacitor]
```

Energy stored: `E = ½CV² = ½Q²/C = ½QV`

- Series: `1/C_eq = 1/C₁ + 1/C₂ + ...`
- Parallel: `C_eq = C₁ + C₂ + ...`
- With dielectric: `C_new = κC_old`
- Electric field with dielectric: `E_new = E_old/κ`

#### INDUCTOR BEHAVIOR:
```
V = L(dI/dt)  [voltage across inductor]
```

Energy stored: `E = ½LI²`

- Series: `L_eq = L₁ + L₂ + ...`
- Parallel: `1/L_eq = 1/L₁ + 1/L₂ + ...`

#### DIODE SPECIFICATIONS:

**Forward voltage (typical):**
- Silicon diodes: ~0.7V
- Schottky diodes: ~0.3V
- Red LED: ~1.8-2.0V
- Green/Yellow LED: ~2.0-2.2V
- Blue/White LED: ~3.0-3.5V

**Forward voltage range (min to max):**
- Typically 0.4-0.8V spread between typical and max
- Example: Typical 0.7V, Max 1.1V

- LED forward current: ~20mA typical
- LED series resistor: `R = (V_supply - V_LED)/I_LED`

#### TRANSFORMER EQUATIONS:
```
V₂/V₁ = N₂/N₁    [voltage ratio = turns ratio]
I₂/I₁ = N₁/N₂    [current ratio = inverse of turns ratio]
```

Power conservation (ideal): `P_in = P_out → V₁I₁ = V₂I₂`

- Step-up: N₂ > N₁ → V₂ > V₁ (voltage increases)
- Step-down: N₂ < N₁ → V₂ < V₁ (voltage decreases)
- EMF in coil: `ε = -N(dΦ/dt)`
- Average EMF: `ε_avg = -NΔΦ/Δt`

#### BJT TRANSISTOR:
```
I_C = βI_B      [collector current = β × base current]
```

- β = current gain (typically 50-300)
- V_BE ≈ 0.7V (base-emitter voltage, silicon)

---

### SECTION 1.5: POWER AND ENERGY

#### POWER TRANSMISSION LOSS:
```
P_loss = I²R    [power loss in transmission line]
```

For constant power P = VI:
- Higher voltage → Lower current → Less loss
- `P_loss ∝ 1/V²` (high voltage is much more efficient)

AC transmitted at high voltage, stepped down for use

#### EQUIVALENT POWER FROM MULTIPLE SOURCES:
```
P_total = P₁ + P₂ + ... (powers add)
```

- Series voltage: `V_total = V₁ + V₂ + ...`
- Parallel current: `I_total = I₁ + I₂ + ...`

---

## SECTION 2: COMPONENT SPECIFICATIONS & IDENTIFICATION

### SECTION 2.1: RESISTORS

#### RESISTOR COLOR CODES:

> **[ADD IMAGE: Resistor Color Code Reference - Physical resistor showing 4-band, 5-band, and 6-band configurations with color labels and value calculations]**

**4-Band Resistor (Standard):**
- Band 1: First digit
- Band 2: Second digit
- Band 3: Multiplier (power of 10)
- Band 4: Tolerance

**5-Band Resistor:**
- Band 1: First digit
- Band 2: Second digit
- Band 3: Third digit
- Band 4: Multiplier
- Band 5: Tolerance

**6-Band Resistor:**
- Same as 5-band, plus Band 6: Temperature coefficient (ppm/K)

**COLOR VALUES:**
- 0 = Black     1 = Brown     2 = Red       3 = Orange    4 = Yellow
- 5 = Green     6 = Blue      7 = Violet    8 = Gray      9 = White

**MULTIPLIER VALUES:**
- ×10⁰ = Black      ×10¹ = Brown      ×10² = Red        ×10³ = Orange
- ×10⁴ = Yellow     ×10⁵ = Green      ×10⁶ = Blue       ×10⁷ = Violet
- ×10⁸ = Gray       ×10⁹ = White
- ×0.1 = Gold       ×0.01 = Silver

**TOLERANCE VALUES:**
- ±0.1% = None        ±0.5% = None         ±1% = Brown
- ±2% = Red           ±5% = Gold           ±10% = Silver
- ±20% = None/Band missing

Temperature coefficient (ppm/K): Only on 6-band resistors
- Example: 1 ppm/K = 0.0001% per Kelvin

**EXAMPLES:**

Example 1: Brown-Black-Brown-Gold
- 1-0 × 10¹ ± 5% = 10Ω ± 5%

Example 2: Violet-Red-Blue-Black-Green-Gray
- 7-3-6 × 10⁰ ± 0.5%, 1 ppm/K = 736Ω ± 0.5%, 1 ppm/K

Example 3: Orange-Blue-Brown-Gold
- 3-6 × 10¹ ± 5% = 360Ω ± 5%

> **[ADD IMAGE: Physical 4-band, 5-band, and 6-band resistors showing color locations and breakdown of Brown-Black-Brown-Gold (10Ω) and Orange-Blue-Brown-Gold (360Ω) examples]**

#### POWER RATINGS:
- 1/8W = 0.125W (least common)
- 1/4W = 0.25W (most common in circuits)
- 1/2W = 0.5W
- 1W = 1W
- 2W = 2W (less common)

Heat dissipation: Larger resistor physically = usually higher power rating
Maximum temperature rise determines power limit

#### STANDARD VALUES (E12 series - Common):
10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82 (× powers of 10)

Examples: 1.0Ω, 10Ω, 100Ω, 1kΩ, 10kΩ, 100kΩ, 1MΩ
- 1.2Ω, 12Ω, 120Ω, 1.2kΩ, 12kΩ, 120kΩ, etc.

---

### SECTION 2.2: CAPACITORS

#### CAPACITANCE VALUES:
- Electrolytic: 1μF to 10,000μF (high values, polarized)
- Ceramic: 1nF to 10μF (common, non-polarized)
- Film: 0.1μF to 10μF (stable, non-polarized)

#### VOLTAGE RATINGS:
Common: 5V, 6.3V, 10V, 16V, 25V, 50V, 100V

Do not exceed rated voltage (dielectric breakdown)

#### POLARITY (Electrolytic capacitors only):
- Red/Long lead = Positive (+, anode)
- Black/Short lead = Negative (-, cathode)

Reversing polarity causes failure/explosion in AC
Non-polarized capacitors: Can be connected either way

#### DIELECTRIC TYPES:
- Ceramic: κ ≈ 10-1000 (varies with type)
- Electrolytic: κ ≈ 50-200
- Film: κ ≈ 2-10

Higher κ = smaller physical size for same capacitance

#### CAPACITANCE FORMULA (Parallel plate):
```
C = ε₀εᵣA/d
```

- ε₀ = 8.85 × 10⁻¹² F/m
- εᵣ = relative permittivity (dielectric constant)
- A = plate area (m²)
- d = plate separation (m)

---

### SECTION 2.3: INDUCTORS

#### INDUCTANCE VALUES:
- Common range: 1μH to 10H
- Small signal: 1μH to 10mH (surface mount, coils)
- Power inductors: 1mH to 10H (larger, more current capacity)

#### INDUCTOR TYPES:
- Air-core: Simple coil, low inductance
- Iron-core: Ferrite rod, moderate inductance
- Ferrite core: Soft ferrite, high inductance

#### SATURATION:
- Iron and ferrite cores saturate at high currents
- After saturation, inductance drops significantly
- Maximum current rating must be respected

---

### SECTION 2.4: DIODES AND LEDs

#### STANDARD DIODE SPECIFICATIONS:

**Silicon Rectifier Diode:**
- Forward voltage: ~0.7V
- Typical range: 0.6V to 0.8V
- Reverse breakdown: Varies (50V to 1000V+)
- Current rating: Varies

**Schottky Diode:**
- Forward voltage: ~0.3V (much lower)
- Used for low-voltage applications
- Lower forward voltage = less power loss

**Zener Diode:**
- Operates in reverse breakdown
- Voltage regulation applications
- Breakdown voltage: Specified (5V, 10V, 12V, etc.)

**Photodiode:**
- Light-sensitive
- Current output proportional to light intensity

**Varactor (Varicap):**
- Voltage-controlled capacitance
- Used in frequency tuning circuits
- Capacitance varies with reverse bias voltage

#### LED (Light Emitting Diode) SPECIFICATIONS:

> **[ADD IMAGE: LED Color vs Forward Voltage Chart - Shows LED beads of different colors (red, green, yellow, blue, white, IR) with corresponding forward voltage ranges displayed as a bar chart]**

**Forward Voltage (Color-dependent):**
- Red: 1.8V - 2.0V
- Green: 2.0V - 2.2V
- Yellow: 2.0V - 2.2V
- Blue: 3.0V - 3.5V
- White: 3.0V - 3.5V
- IR (Infrared): 1.2V - 1.6V

**Typical vs. Maximum Forward Voltage:**
Example: Red LED
- Typical: 1.8V
- Maximum: 2.5V
- Difference: ~0.7V

Always use typical for design, but respect maximum

**Forward Current:**
- Typical: 20mA for standard LEDs
- Can range: 5mA (low-power) to 100mA+ (high-power)

Never exceed max current (burns out LED instantly)

Series resistor: `R = (V_supply - V_LED_typical) / I_LED`

Example: 9V supply, red LED (1.8V), 20mA
- `R = (9 - 1.8) / 0.020 = 7.2 / 0.020 = 360Ω`
- Use 390Ω or 360Ω standard value

**Power Dissipation:**
```
P_LED = V_LED × I_LED
P_resistor = I² × R
```

Example (continued): 
- `P_LED = 1.8 × 0.020 = 36mW`
- `P_resistor = 0.020² × 360 = 0.144W = 144mW`
- Total power from supply = 9V × 20mA = 180mW

**Efficiency:**
- LEDs: 80-90% efficient (light output per watt)
- Incandescent: ~5% efficient
- LEDs produce little heat compared to incandescent

**Color vs. Wavelength:**
- IR: >940nm
- Red: 620-630nm
- Green: 500-550nm
- Blue: 450-470nm
- White: Combination of multiple wavelengths

---

### SECTION 2.5: TRANSISTORS

#### BJT (Bipolar Junction Transistor):

**Types:**
- **NPN:** Arrow OUT of base (emitter side)
  - Easier to turn on
  - Common configuration
  - Current flows INTO base to turn on

- **PNP:** Arrow INTO base (emitter side)
  - Opposite polarity from NPN
  - Current flows OUT of base to turn on

**Key Parameters:**
- β (beta) = current gain = I_C / I_B
  - Typical values: 50 to 300
  - Varies with device, temperature, current level
- V_BE (base-emitter voltage) ≈ 0.7V for silicon
- V_CE_SAT (saturation) ≈ 0.2V (when fully on)

**Regions of Operation:**
- Cut-off: Base current ≈ 0 → Collector current ≈ 0 (transistor OFF)
- Linear/Active: Base current controlled → Collector current = β × I_B
- Saturation: Base current high → Collector current = V_CC / R_C (transistor ON)

#### MOSFET (Metal-Oxide-Semiconductor Field-Effect Transistor):

**Types:**
- N-channel: Enhanced by positive gate voltage
- P-channel: Enhanced by negative gate voltage

**Key Characteristics:**
- Gate input impedance: Very high (essentially infinite)
- Less current gain than BJT, but voltage-controlled
- Faster switching than BJT
- History: Julius Edgar Lilienfeld proposed in 1925
- "Metal" can actually be polysilicon (misnomer)

---

### SECTION 2.6: TRANSFORMERS

#### BASIC SPECIFICATIONS:

**Turns Ratio:**
- N_primary : N_secondary (e.g., 100:1000, or 1:10 step-up)
- Voltage ratio: `V_secondary / V_primary = N_secondary / N_primary`
- Current ratio: `I_secondary / I_primary = N_primary / N_secondary`

**Power Rating:**
- VA (volt-amperes) = V × I
- Example: 1000VA transformer at 120V primary = 8.33A maximum input

**Efficiency:**
- Ideal transformer: 100% (impossible in practice)
- Real transformer: 95-99% (depends on losses)

**Core Types:**
- Iron core: High efficiency, can saturate
- Air core: Low efficiency, linear up to high currents
- Ferrite core: Good efficiency, can saturate

**Step-up Transformer:**
- More turns in secondary than primary
- Voltage increases, current decreases
- Example: 1:10 step-up → 120V becomes 1200V, current reduced 10×

**Step-down Transformer:**
- More turns in primary than secondary
- Voltage decreases, current increases
- Example: 10:1 step-down → 1200V becomes 120V, current increases 10×

Household transformers: Power line (2400V) → 240V → 120V (step-down)

---

## SECTION 3: QUICK REFERENCE TABLES

### SECTION 3.1: COMMON VALUES AND CONSTANTS

#### PHYSICAL CONSTANTS:

- Speed of light: c = 3 × 10⁸ m/s
- Electron charge: e = 1.602 × 10⁻¹⁹ C
- Coulomb constant: k = 8.99 × 10⁹ N·m²/C²
- Vacuum permittivity: ε₀ = 8.85 × 10⁻¹² F/m
- Vacuum permeability: μ₀ = 4π × 10⁻⁷ T·m/A

#### UNIT PREFIXES:

- Tera (T)  = 10¹²    Giga (G)  = 10⁹     Mega (M)  = 10⁶    Kilo (k)  = 10³
- Centi (c) = 10⁻²    Milli (m) = 10⁻³   Micro (μ) = 10⁻⁶   Nano (n)  = 10⁻⁹
- Pico (p)  = 10⁻¹²

#### RESISTANCE CONVERSIONS:

- 1 kΩ = 1,000 Ω
- 1 MΩ = 1,000,000 Ω = 1,000 kΩ

#### CAPACITANCE CONVERSIONS:

- 1 μF = 1,000 nF = 1,000,000 pF
- 1 nF = 1,000 pF
- 1 pF = 0.001 nF

#### INDUCTANCE CONVERSIONS:

- 1 H = 1,000 mH = 1,000,000 μH
- 1 mH = 1,000 μH

#### FREQUENCY & PERIOD:

- f (Hz) = 1 / T (seconds)
- T (seconds) = 1 / f (Hz)
- ω (rad/s) = 2π × f (Hz)
- f (Hz) = ω (rad/s) / 2π

#### POWER CONVERSIONS:

- 1 W = 1 J/s
- 1 kW = 1,000 W
- 1 horsepower (hp) ≈ 746 W

---

### SECTION 3.2: MOST IMPORTANT FORMULAS TO MEMORIZE

#### MUST-MEMORIZE FORMULAS:

- ☐ `V = IR` (Ohm's Law) - Foundation
- ☐ `P = VI = I²R = V²/R` (Power - all three forms!)
- ☐ `R_series = R₁ + R₂ + ...` (Series resistors add)
- ☐ `1/R_parallel = 1/R₁ + 1/R₂ + ...` (Parallel reciprocals)
- ☐ `V_divider = V_in × R₂/(R₁ + R₂)` (Voltage divider formula)
- ☐ `τ_RC = RC` (RC time constant)
- ☐ `τ_RL = L/R` (RL time constant)
- ☐ `V(t) = V₀(1 - e^(-t/τ))` (RC charging)
- ☐ `V(t) = V₀e^(-t/τ)` (RC discharging)
- ☐ `B = μ₀I/(2πr)` (Magnetic field from straight wire)
- ☐ `B = μ₀nI` (Magnetic field in solenoid, n = N/L)
- ☐ `F = qvB sin(θ)` (Magnetic force on charge)
- ☐ `ε = -N(dΦ/dt)` (Faraday's law of induction)
- ☐ `F = kq₁q₂/r²` (Coulomb's law, 1/r² force)
- ☐ `V₂/V₁ = N₂/N₁` (Transformer voltage ratio)
- ☐ `V_RMS = V_peak / √2` (AC RMS conversion)
- ☐ `X_C = 1/(2πfC)` (Capacitive reactance)
- ☐ `X_L = 2πfL` (Inductive reactance)
- ☐ `C = ε₀εᵣA/d` (Parallel plate capacitor)
- ☐ `f = 1/(2π√(LC))` (LC resonant frequency)

---

### SECTION 3.3: STANDARD RESISTOR VALUES (E12 Series)

**Base values (multiply by 10^n):**

10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82

**MOST COMMON VALUES:**

- 1Ω, 10Ω, 100Ω, 1kΩ, 10kΩ, 100kΩ, 1MΩ
- 1.2Ω, 12Ω, 120Ω, 1.2kΩ, 12kΩ, 120kΩ, 1.2MΩ
- 1.5Ω, 15Ω, 150Ω, 1.5kΩ, 15kΩ, 150kΩ, 1.5MΩ
- 2.2Ω, 22Ω, 220Ω, 2.2kΩ, 22kΩ, 220kΩ, 2.2MΩ
- 3.3Ω, 33Ω, 330Ω, 3.3kΩ, 33kΩ, 330kΩ, 3.3MΩ
- 4.7Ω, 47Ω, 470Ω, 4.7kΩ, 47kΩ, 470kΩ, 4.7MΩ
- 6.8Ω, 68Ω, 680Ω, 6.8kΩ, 68kΩ, 680kΩ, 6.8MΩ

---

### SECTION 3.4: HOUSEHOLD AC STANDARDS

**North America (Standard):**
- Voltage (RMS): 120V
- Voltage (Peak): 170V (= 120 × 1.414)
- Voltage (Peak-to-peak): 340V (= 2 × 170)
- Frequency: 60 Hz
- Period: 16.7 ms

High-power circuits: 240V (RMS), 340V (peak)

---

### SECTION 3.5: SCIENTISTS AND UNITS

#### UNIT NAMESAKES AND THEIR CONTRIBUTIONS:

**Volt (V)** ← Alessandro Volta (1745-1827, Italian)
- Invented first battery (Voltaic Pile, 1800)

**Ampere (A)** ← André-Marie Ampère (1775-1836, French)
- Ampere's law (1/r dependence in magnetic fields)

**Ohm (Ω)** ← Georg Ohm (1789-1854, German)
- Ohm's law (V = IR)

**Farad (F)** ← Michael Faraday (1791-1867, British)
- Electromagnetic induction

**Coulomb (C)** ← Charles-Augustin Coulomb (1736-1806, French)
- Coulomb's law (1/r² electrostatic force)

**Tesla (T)** ← Nikola Tesla (1856-1943, Serbian-American)
- AC power systems

**Weber (Wb)** ← Wilhelm Eduard Weber (1804-1891, German)
- Magnetic flux unit

#### MAXWELL'S EQUATIONS CONTRIBUTORS:

- **Maxwell:** Mathematical formalization (1860s)
- **Faraday:** Experimental discovery
- **Ampère:** Current-magnetic field relationship
- **Gauss:** Flux laws

**NOT in Maxwell's equations:** Heinrich Hertz (verified waves)

---

## END OF STUDY BINDER - ESSENTIAL SECTIONS
