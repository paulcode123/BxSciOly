# Circuit Lab Practice Setups

## Setup 1: Mystery Resistor Challenge
**Objective:** Determine the value of an unknown resistor using only voltage measurements

### Materials Needed:
- Breadboard
- 9V battery (or battery pack)
- Multimeter
- Unknown resistor (e.g., 220Ω, 470Ω, 1kΩ, 2.2kΩ, 4.7kΩ, 10kΩ)
- Known resistor (e.g., 1kΩ)
- Jumper wires

### Circuit Configuration:
```
Battery (+) → Known Resistor (1kΩ) → Unknown Resistor → Battery (-)
```

### Practice Task:
1. Build the series circuit with the known and unknown resistors
2. Measure the voltage across the known resistor (V₁)
3. Measure the voltage across the unknown resistor (V₂)
4. Measure the total voltage across both resistors (V_total)
5. Calculate the unknown resistance using:
   - Using voltage divider: R_unknown = R_known × (V₂/V₁)
   - Or using total voltage: R_unknown = R_known × (V_total - V₁)/V₁

### Variations:
- Try different known resistor values (100Ω, 1kΩ, 10kΩ)
- Use multiple unknown resistors in series
- Practice with resistors in parallel configurations

---

## Setup 2: Equal Brightness LED Challenge
**Objective:** Connect 2 LEDs so they are equally bright using wires, batteries, resistors, and LEDs

### Materials Needed:
- Breadboard
- 2 identical LEDs (same color and type)
- 2-4 resistors (various values: 220Ω, 330Ω, 470Ω, 1kΩ)
- Battery pack (3V or 6V)
- Jumper wires
- Multimeter (optional, for verification)

### Practice Task:
1. Given: 2 LEDs, battery pack, assorted resistors, wires
2. Goal: Make both LEDs equally bright
3. Options to try:
   - **Series connection:** LEDs in series with one resistor
   - **Parallel with matching resistors:** Each LED with its own resistor of equal value
   - **Parallel with different resistors:** Adjust resistor values to match brightness

### Key Concepts:
- LEDs have forward voltage drops (~1.8-3.2V depending on color)
- Current determines brightness
- Resistors limit current: I = (V_source - V_LED) / R
- For equal brightness, both LEDs need the same current

### Practice Variations:
- Use different colored LEDs (different forward voltages)
- Challenge: Use only one resistor value
- Measure current through each LED to verify equal brightness

---

## Setup 3: Electromagnet Construction & Power Calculation
**Objective:** Construct an electromagnet and calculate power supplied to the circuit

### Materials Needed:
- Iron bolt or nail (3-6 inches long)
- Insulated wire (magnet wire or enameled wire, ~22-26 AWG)
- Battery (9V or battery pack)
- Multimeter
- Paper clips or small metal objects (for testing)
- Optional: Switch

### Practice Task:
**Part A: Build the Electromagnet**
1. Wrap wire tightly around the bolt (50-100 turns)
2. Leave ~6 inches of wire free at each end
3. Strip insulation from wire ends
4. Connect one end to battery positive terminal
5. Connect other end to battery negative terminal
6. Test by picking up paper clips

**Part B: Calculate Power**
1. Measure voltage across the electromagnet: V
2. Measure current through the circuit: I
3. Calculate power: P = V × I
4. Calculate resistance: R = V / I
5. Verify power using: P = I²R or P = V²/R

### Practice Variations:
- Try different numbers of wire turns (50, 100, 150 turns)
- Measure how many paper clips each configuration can lift
- Compare power consumption vs. strength
- Add a switch to control the electromagnet
- Try different battery voltages (3V, 6V, 9V)

### Additional Challenge:
- Given a USB charger label, calculate:
  - Power output at different voltage/current settings
  - Time to charge a battery with specific capacity (mAh)
  - Example: USB charger outputs 5V @ 2A = 10W
  - Battery: 5000mAh @ 3.7V = 18.5Wh
  - Charging time ≈ 18.5Wh / 10W = 1.85 hours (assuming 100% efficiency)

---

## General Practice Tips:

1. **Breadboard Familiarity:**
   - Practice identifying power rails vs. terminal strips
   - Learn internal wiring patterns
   - Practice building circuits quickly

2. **Multimeter Skills:**
   - Voltage measurement (parallel connection)
   - Current measurement (series connection)
   - Resistance measurement (power off)
   - Proper range selection

3. **Circuit Analysis:**
   - Practice Ohm's Law: V = IR
   - Power calculations: P = VI = I²R = V²/R
   - Series and parallel resistor combinations
   - Voltage divider calculations

4. **Safety:**
   - Always check polarity
   - Don't exceed component ratings
   - Be careful with battery connections
   - Use appropriate resistor values to limit current

5. **Time Management:**
   - Practice building circuits quickly
   - Organize materials before starting
   - Have a systematic approach to measurements
