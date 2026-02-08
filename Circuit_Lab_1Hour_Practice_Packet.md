# Circuit Lab 1-Hour Practice Packet

**Total Time: 60 minutes**
**Difficulty: Intermediate (assumes basic circuit knowledge)**

---

## How to Use This Packet

1. **Go in order** - Don't skip around
2. **Work problems on scratch paper** - Shows your thinking
3. **Use the binder** - For calculations, look up values in your Circuit Lab Study Binder (especially for quick reference questions)
4. **Time yourself** - Keep to the suggested time for each section
5. **Check your work** - Review answers at the end

---

## SECTION 1: SERIES & PARALLEL CIRCUIT ANALYSIS (20 minutes)

### What You're Practicing
- Identifying circuit types (series vs parallel)
- Calculating equivalent resistance
- Finding voltages and currents
- Building intuition about how circuits behave

### Guided Example 1: Simple Series Circuit

**Circuit:** Battery (12V) connected to three resistors in series: R₁=2Ω, R₂=3Ω, R₃=5Ω

**Step 1: Find equivalent resistance**
```
For series: R_eq = R₁ + R₂ + R₃
R_eq = 2 + 3 + 5 = 10Ω
```

**Step 2: Find total current**
```
Using Ohm's Law: I = V / R_eq
I = 12V / 10Ω = 1.2A
```

**Step 3: Find voltage across each resistor**
```
V₁ = I × R₁ = 1.2A × 2Ω = 2.4V
V₂ = I × R₂ = 1.2A × 3Ω = 3.6V
V₃ = I × R₃ = 1.2A × 5Ω = 6.0V

Check: 2.4 + 3.6 + 6.0 = 12V ✓
```

**Key insight:** The largest resistor (R₃) gets the largest voltage drop!

---

### Guided Example 2: Simple Parallel Circuit

**Circuit:** Battery (12V) connected to three resistors in parallel: R₁=10Ω, R₂=10Ω, R₃=20Ω

**Step 1: Find equivalent resistance**
```
For parallel: 1/R_eq = 1/R₁ + 1/R₂ + 1/R₃
1/R_eq = 1/10 + 1/10 + 1/20
1/R_eq = 2/20 + 2/20 + 1/20 = 5/20 = 1/4
R_eq = 4Ω
```

**Step 2: Find total current**
```
I_total = V / R_eq = 12V / 4Ω = 3A
```

**Step 3: Find current through each branch**
```
All resistors have same voltage (12V) across them
I₁ = V / R₁ = 12V / 10Ω = 1.2A
I₂ = V / R₂ = 12V / 10Ω = 1.2A
I₃ = V / R₃ = 12V / 20Ω = 0.6A

Check: 1.2 + 1.2 + 0.6 = 3A ✓
```

**Key insight:** The smallest resistor (R₁ and R₂) get the most current!

---

### Your Turn: Practice Problems (15 minutes)

**Problem 1.1 (Series Circuit - 5 min)**

Circuit: 9V battery connected to resistors in series: R₁=100Ω, R₂=150Ω, R₃=50Ω

Find:
- a) Total equivalent resistance
- b) Total current
- c) Voltage across R₁, R₂, R₃
- d) Power dissipated in R₂

*Look up in binder:* Power formula (Section 1.1 or 1.5)

---

**Problem 1.2 (Parallel Circuit - 5 min)**

Circuit: 6V battery connected to three resistors in parallel: R₁=12Ω, R₂=12Ω, R₃=6Ω

Find:
- a) Total equivalent resistance
- b) Total current from battery
- c) Current through R₁, R₂, R₃
- d) Which resistor dissipates the most power?

*Look up in binder:* Power formula for parallel circuits

---

**Problem 1.3 (Mixed Series-Parallel - 5 min)**

Circuit: 18V battery connected to:
- R₁=4Ω in series with
- A parallel combination of R₂=8Ω and R₃=8Ω

Find:
- a) Equivalent resistance of the parallel section (R₂ and R₃)
- b) Total equivalent resistance
- c) Total current from battery
- d) Voltage across R₁
- e) Voltage across the parallel section

---

## SECTION 2: RC TIME CONSTANTS (15 minutes)

### What You're Practicing
- Understanding the RC time constant formula
- Predicting capacitor behavior at different times
- Reading/interpreting RC graphs
- Building intuition about exponential behavior

### Guided Example: RC Charging

**Circuit:** 10V battery, 1kΩ resistor, 100μF capacitor (initially uncharged)

**Step 1: Calculate time constant**
```
τ = R × C
τ = 1kΩ × 100μF
τ = 1,000Ω × 0.0001F = 0.1 seconds = 100ms
```

**Step 2: Predict voltage at key times**

Using equation: V(t) = V₀(1 - e^(-t/τ))

```
At t = 0:     V = 10(1 - e^0) = 10(1 - 1) = 0V (capacitor starts empty)
At t = 1τ:    V = 10(1 - e^-1) = 10(1 - 0.368) = 6.32V
At t = 3τ:    V = 10(1 - e^-3) = 10(1 - 0.050) = 9.50V
At t = 5τ:    V = 10(1 - e^-5) = 10(1 - 0.007) = 9.93V (fully charged)
```

**Step 3: Time to reach specific voltages**
```
Question: How long to reach 5V (half of 10V)?

5 = 10(1 - e^(-t/τ))
0.5 = 1 - e^(-t/τ)
e^(-t/τ) = 0.5
-t/τ = ln(0.5) = -0.693
t = 0.693 × τ = 0.693 × 100ms = 69.3ms
```

**Key insights:**
- At 1τ: About 63% charged
- At 3τ: About 95% charged (practical full charge)
- At 5τ: About 99% charged (theoretical full charge)
- Shape is always exponential (same curve shape every time!)

---

### Your Turn: Practice Problems (12 minutes)

**Problem 2.1 (Time Constant Calculation - 3 min)**

Circuit 1: R=2kΩ, C=50μF → τ = ?
Circuit 2: R=10kΩ, C=10μF → τ = ?
Circuit 3: R=100Ω, C=1000μF → τ = ?

*Look up in binder:* Time constant formula (Section 1.2)

---

**Problem 2.2 (RC Charging - 5 min)**

Circuit: 12V battery, 5kΩ resistor, 50μF capacitor

- a) Calculate τ
- b) How long to reach 95% charge? (Use 3τ rule)
- c) What is the voltage at 1τ?
- d) What is the voltage at 5τ?
- e) If you wanted to charge faster, what would you change: R or C? Why?

*Look up in binder:* Charging formula and time constant table (Section 5.1)

---

**Problem 2.3 (RC Discharging - 4 min)**

Same capacitor as 2.2, fully charged to 12V, now discharging through the 5kΩ resistor

- a) What's the voltage at t = 1τ?
- b) What's the voltage at t = 3τ?
- c) How long until only 1% remains? (Use 5τ rule)
- d) Compare charging and discharging times - are they the same? Why?

*Look up in binder:* Discharging formula (Section 5.1)

---

## SECTION 3: TRANSFORMERS & AC FUNDAMENTALS (10 minutes)

### What You're Practicing
- Transformer voltage/current relationships
- AC voltage conversions (RMS ↔ Peak)
- Frequency and period calculations
- Understanding when transformers work

### Guided Example: Transformer Problem

**Scenario:** Power company uses a transformer to step up voltage for efficient transmission

**Given:**
- Primary coil: 100 turns, input 240V
- Secondary coil: 5,000 turns
- Question: What's the output voltage?

**Solution:**
```
Transformer equation: V₂/V₁ = N₂/N₁

V₂ = V₁ × (N₂/N₁)
V₂ = 240V × (5,000/100)
V₂ = 240V × 50
V₂ = 12,000V (high voltage for efficient transmission!)
```

**Current relationship:**
```
Power conserved (ideal transformer): P_in = P_out
V₁ × I₁ = V₂ × I₂

If I₁ = 100A at primary:
240V × 100A = 12,000V × I₂
24,000W = 12,000V × I₂
I₂ = 24,000W / 12,000V = 2A

Notice: Voltage went up 50×, current went down 50×
```

---

### Guided Example: AC Voltage Conversion

**Given:** Household outlet reading: 120V RMS

**Find:** Peak voltage and peak-to-peak voltage

```
V_peak = V_RMS × √2
V_peak = 120V × 1.414
V_peak = 169.7V ≈ 170V

V_peak-to-peak = 2 × V_peak
V_peak-to-peak = 2 × 170V = 340V
```

*Why important?* Transformers, inductors, and AC circuits need RMS values for power calculations!

---

### Your Turn: Practice Problems (8 minutes)

**Problem 3.1 (Transformer Ratios - 3 min)**

Transformer 1: Primary 100V, Secondary 5V, Primary has 200 turns. How many turns on secondary?

Transformer 2: Primary 480V, Secondary 120V, Primary has 400 turns. How many turns on secondary?

*Look up in binder:* Transformer formula (Section 1.4 or 5.5)

---

**Problem 3.2 (Power Conservation - 3 min)**

Transformer 3: 
- Primary: 100V, 20A
- Secondary: 200V
- What's the secondary current?
- Is power conserved? (Show calculation)

Transformer 4:
- Primary: 12V, ? current
- Secondary: 120V, 1A
- What's the primary current?

---

**Problem 3.3 (AC Voltage Conversion - 2 min)**

European outlet: 230V RMS

- a) What's the peak voltage?
- b) What's the peak-to-peak voltage?
- c) What's the frequency in Europe? (Look up in binder)

*Look up in binder:* AC standards (Section 3.3)

---

## SECTION 4: RIGHT-HAND RULE PRACTICE (10 minutes)

### What You're Practicing
- Three different contexts for right-hand rule
- Predicting force/field direction
- Avoiding common reversals
- Building spatial reasoning

### Context 1: Magnetic Field From Straight Wire

**Rule:** Thumb = current direction, fingers = field circles around

**Guided Example:**
```
Wire carries current upward (↑)
Point thumb up ↑
Curl fingers around thumb
→ Fingers point in circle direction (clockwise when viewed from right, counterclockwise from left)
```

**Your turn (1 min):**
- Wire carries current to the RIGHT (→)
- What direction does the magnetic field circle? (Draw it on paper)
- Check: Use right hand, thumb RIGHT, fingers curl which way?

---

### Context 2: Magnetic Field From Current Loop

**Rule:** Curl fingers = current direction, thumb = field direction through loop

**Guided Example:**
```
Loop has current flowing clockwise (viewed from above)
Curl fingers clockwise ⟳
Thumb points DOWN ↓ (into the page)
→ Field points into page (symbol: ⊗)
```

**Your turn (1 min):**
- Loop has current flowing counterclockwise (viewed from above)
- What direction does the field point?
- Check: Curl fingers counterclockwise, thumb points which way?

---

### Context 3: Force on Moving Charge

**Rule:** Point fingers = velocity, curl toward field, thumb = force

**Guided Example:**
```
Electron moving RIGHT (→)
Magnetic field pointing UP (↑)
Point fingers RIGHT (→)
Curl toward UP (↑) - fingers rotate 90° to point up
Thumb points FORWARD (toward you ↗)
But wait... electron is NEGATIVE! Reverse the answer!
→ Force points BACKWARD (away from you ↙)
```

**Your turn (2 min):**
- Positive charge moving to the RIGHT (→)
- Magnetic field pointing OUT OF PAGE (⊙)
- What direction is the force?
- Try with electron (negative charge) - does it reverse?

---

### Advanced Practice: Mixing Contexts (5 minutes)

**Problem 4.1**

Straight wire carries current downward (↓). A positive charge moves parallel to the wire in the same direction (downward ↓).

- a) What direction is the magnetic field at a point to the RIGHT of the wire?
- b) The charge moves parallel to the field. What force does it experience?

---

**Problem 4.2**

Wire carries current to the RIGHT (→). Another point charge is stationary 5cm directly above the wire.

- a) What direction is the magnetic field at the charge's location?
- b) The charge is not moving. What force does it experience?
- c) Now imagine the charge starts moving TOWARD the wire. What force acts on it?

---

## SECTION 5: QUICK FACTS & LOOKUP PRACTICE (5 minutes)

### What You're Practicing
- Using your binder efficiently
- Recalling common values
- Building familiarity with reference material
- Speed lookups under pressure

### Rapid Fire Questions (Set timer for 5 minutes total)

**Household AC Standards**
- Q1: What's the RMS voltage of a standard US outlet?
  - Look up in binder: Section 3.3
  - Answer: __________
  
- Q2: What's the frequency?
  - Look up in binder: Section 3.3
  - Answer: __________
  
- Q3: What's the peak voltage?
  - Calculate or look up: __________

---

**Component Specifications**

- Q4: Red LED forward voltage?
  - Look up in binder: Section 2.4
  - Answer: __________

- Q5: Blue LED forward voltage?
  - Look up in binder: Section 2.4
  - Answer: __________

- Q6: Silicon diode forward voltage?
  - Look up in binder: Section 2.4
  - Answer: __________

---

**Scientists & Units**

- Q7: Voltage unit is named after: __________
  - Look up in binder: Section 3.4
  
- Q8: Current unit is named after: __________
  - Look up in binder: Section 3.4

- Q9: Resistance unit is named after: __________
  - Look up in binder: Section 3.4

---

**Key Facts**

- Q10: What determines how dangerous an electrical shock is?
  - Look up in binder: Section 6.4
  - Answer: __________

- Q11: Do magnetic monopoles exist?
  - Look up in binder: Section 1.3 or 4
  - Answer: __________

- Q12: Why are transformers used in power transmission?
  - Look up in binder: Section 5.5 or 1.5
  - Answer: __________

---

## SECTION 6: CUMULATIVE PROBLEM (10 minutes)

### Challenge Problem: Putting It All Together

**Scenario:** You're designing an LED circuit using a 9V battery. You want to use:
- Red LED (forward voltage 1.8V, operating current 20mA)
- An RC filter circuit with a 100μF capacitor to smooth out noise

**Part A: Circuit Design (5 min)**

1. Calculate the resistor needed in series with the LED
   - Formula: R = (V_supply - V_LED) / I_LED
   - Show work: __________
   - Answer: __________ Ω

2. What standard resistor value would you use? (Look up closest E12 value in binder Section 3.2)
   - Answer: __________ Ω

3. What's the power rating of resistor needed?
   - Calculate: P = I² × R
   - Should it be ¼W, ½W, or 1W? __________

---

**Part B: RC Time Constant (3 min)**

4. If you add a smoothing capacitor (100μF) in parallel with the LED:
   - Calculate τ = R × C
   - τ = __________

5. How long to reach 95% of final voltage?
   - Use 3τ rule: __________

6. Interpret: Is this smoothing effect fast enough for perceivable flickering? (Should be less than ~50ms to be imperceptible)
   - Yes / No (circle one)
   - Explain: __________

---

**Part C: Real-World Consideration (2 min)**

7. If this circuit will receive AC power instead (after a transformer steps down 120V AC to 9V AC), what happens?
   - Would a regular capacitor work for smoothing?
   - Explain: __________

---

## ANSWER GUIDE & SOLUTIONS

### Section 1 Answers

**Problem 1.1:**
- a) R_eq = 100 + 150 + 50 = 300Ω
- b) I = 9V / 300Ω = 0.03A = 30mA
- c) V₁ = 3V, V₂ = 4.5V, V₃ = 1.5V (check: 3+4.5+1.5=9V ✓)
- d) P₂ = (0.03A)² × 150Ω = 0.135W = 135mW

**Problem 1.2:**
- a) 1/R_eq = 1/12 + 1/12 + 1/6 = 1/12 + 1/12 + 2/12 = 4/12 → R_eq = 3Ω
- b) I = 6V / 3Ω = 2A
- c) I₁ = 0.5A, I₂ = 0.5A, I₃ = 1A (check: 0.5+0.5+1 = 2A ✓)
- d) R₃ (6Ω) dissipates most: P₃ = 6V × 1A = 6W

**Problem 1.3:**
- a) Parallel: 1/R_parallel = 1/8 + 1/8 = 2/8 → R_parallel = 4Ω
- b) R_total = 4Ω + 4Ω = 8Ω
- c) I = 18V / 8Ω = 2.25A
- d) V₁ = 2.25A × 4Ω = 9V
- e) V_parallel = 18V - 9V = 9V

---

### Section 2 Answers

**Problem 2.1:**
- Circuit 1: τ = 2,000 × 0.00005 = 0.1s = 100ms
- Circuit 2: τ = 10,000 × 0.00001 = 0.1s = 100ms
- Circuit 3: τ = 100 × 1 = 100s

**Problem 2.2:**
- a) τ = 5,000Ω × 0.00005F = 0.25s = 250ms
- b) 3τ = 750ms
- c) V = 12(1 - e^-1) = 12 × 0.632 = 7.58V
- d) V = 12(1 - e^-5) = 12 × 0.993 = 11.92V (essentially 12V)
- e) Decrease R: Lower resistance = faster charging (τ = RC gets smaller)

**Problem 2.3:**
- a) V = 12 × e^-1 = 12 × 0.368 = 4.4V
- b) V = 12 × e^-3 = 12 × 0.05 = 0.6V
- c) 5τ = 5 × 0.25s = 1.25s
- d) Same time constant (τ = RC) applies to both - charging and discharging take same amount of time!

---

### Section 3 Answers

**Problem 3.1:**
- Transformer 1: N₂ = 200 × (5/100) = 10 turns
- Transformer 2: N₂ = 400 × (120/480) = 100 turns

**Problem 3.2:**
- Transformer 3: I₂ = (100V × 20A) / 200V = 10A ✓ Power conserved: 2000W = 2000W
- Transformer 4: I₁ = (120V × 1A) / 12V = 10A

**Problem 3.3:**
- a) V_peak = 230 × 1.414 = 325V
- b) V_peak-to-peak = 650V
- c) 50Hz (European standard)

---

### Section 4 Answers

**Context 1 Your Turn:**
- Current RIGHT: Field circles (counterclockwise from front, clockwise from back) ⟳

**Context 2 Your Turn:**
- Counterclockwise: Thumb points UP (out of page) ⊙

**Context 3 Your Turn:**
- Positive charge: RIGHT × OUT = DOWN-RIGHT (toward corner) ↘
- Electron: Same situation, force REVERSED = UP-LEFT ↖

**Problem 4.1:**
- a) Field points FORWARD (out of page) ⊙ (use RHR: current down, point down, fingers curl forward)
- b) Force = ZERO (velocity parallel to field, no force) ✓

**Problem 4.2:**
- a) Field points BACKWARD (into page) ⊗ at top of wire (use RHR: current right, point right, fingers curl back at top)
- b) Force = ZERO (charge not moving, no magnetic force)
- c) Force points AWAY from wire (use Lorentz force: v↓ × B⊗ = F→ away)

---

### Section 5 Answers

Rapid Fire:
1. 120V RMS
2. 60Hz
3. 170V
4. 1.8V - 2.0V
5. 3.0V - 3.5V
6. 0.7V
7. Alessandro Volta
8. André-Marie Ampère
9. Georg Ohm
10. Current, voltage, frequency, contact duration, resistance of skin
11. No (Gauss's law for magnetism shows they don't exist)
12. High voltage reduces transmission losses (P_loss = I²R, lower current = less loss)

---

### Section 6 Challenge Problem

**Part A:**
1. R = (9 - 1.8) / 0.02 = 7.2 / 0.02 = 360Ω
2. 360Ω (standard E12 value)
3. P = (0.02)² × 360 = 0.144W → 1/4W (0.25W) resistor

**Part B:**
4. τ = 360 × 0.1 = 36 seconds (large!)
5. 3τ = 108 seconds (way too slow for practical use!)
6. No - this is way too slow. The flicker would be visible!

**Part C:**
7. Transformers only work with AC, not DC. So yes, the capacitor would smooth the AC after transformer. But you'd need a rectifier circuit first to convert AC to DC!

---

## Reflection Questions (After completing)

1. What topic felt easiest? Why?
2. What topic gave you the most trouble?
3. Which binder sections did you use most? Least?
4. If you had another 30 minutes, what would you practice more?
5. Rate your confidence (1-10) for each section:
   - Series/Parallel circuits: ___
   - RC time constants: ___
   - Transformers/AC: ___
   - Right-hand rule: ___
   - Quick facts: ___

---

## Tips for Test Day

✓ **Bring your binder** - These are all in there for a reason
✓ **Start with easy problems** - Build momentum and confidence
✓ **Show all work** - Partial credit is better than no credit
✓ **When stuck:** Use the flowchart (Section 4.1) to decide your approach
✓ **Double-check units** - Most errors come from unit conversion
✓ **Verify with power balance** - If answer seems wrong, check P_in = P_out
✓ **Right-hand rule problems:** Actually use your hand! Don't try to visualize

---

**Good luck on your test! You've got this.** 🎯
