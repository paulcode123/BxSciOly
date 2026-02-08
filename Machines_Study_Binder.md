# MACHINES STUDY BINDER - COMPLETE REFERENCE GUIDE
**Version 1.0 - Optimized for Quick Lookup During Tests**

---

## TABLE OF CONTENTS (Quick Navigation)

1. **ESSENTIAL FORMULAS & EQUATIONS**
   - 1.1 Mechanical Advantage Fundamentals
   - 1.2 Lever Formulas
   - 1.3 Pulley System Formulas
   - 1.4 Inclined Plane Formulas
   - 1.5 Screw Formulas
   - 1.6 Wedge Formulas
   - 1.7 Wheel and Axle Formulas
   - 1.8 Gear Formulas
   - 1.9 Work, Energy, and Efficiency
   - 1.10 Friction and Angle of Repose

2. **MACHINE TYPES & IDENTIFICATION**
   - 2.1 Lever Classes (First/Second/Third)
   - 2.2 Pulley Types and Configurations
   - 2.3 Screw Specifications
   - 2.4 Wedge Applications
   - 2.5 Wheel and Axle Examples
   - 2.6 Gear Types
   - 2.7 Compound Machines

3. **QUICK REFERENCE TABLES**
   - 3.1 Common Lever Classifications
   - 3.2 Standard Mechanical Advantage Values
   - 3.3 Friction Coefficients
   - 3.4 Unit Conversions
   - 3.5 Physical Constants

4. **PROBLEM-SOLVING FRAMEWORKS**
   - 4.1 Mechanical Advantage Calculation Strategy
   - 4.2 Efficiency Problem Approach
   - 4.3 Compound Machine Analysis
   - 4.4 Self-Locking Determination

5. **VISUAL GUIDES & MENTAL MODELS**
   - 5.1 Lever Class Diagrams
   - 5.2 Pulley System Configurations
   - 5.3 Inclined Plane Force Analysis
   - 5.4 Screw Thread Visualization
   - 5.5 Compound Machine Combinations

6. **COMMON PITFALLS & TIPS**
   - 6.1 Formula Misapplication
   - 6.2 IMA vs AMA Confusion
   - 6.3 Efficiency Calculation Errors
   - 6.4 Unit Conversion Mistakes

7. **TEST-SPECIFIC STRATEGIES**
   - 7.1 UGA Test Focus (Fundamentals)
   - 7.2 UT Austin Test Focus (Comprehensive)
   - 7.3 Hawk&Hornet Test Focus (Physics Integration)
   - 7.4 MVSO Test Focus (Advanced Problem-Solving)
   - 7.5 Rickards Test Focus (Theoretical Depth)

8. **DERIVATION QUICK-REFS (For Advanced Questions)**
   - 8.1 Inclined Plane IMA Derivation
   - 8.2 Pulley IMA Derivation
   - 8.3 Screw IMA Derivation
   - 8.4 Wedge IMA Derivation

---

## SECTION 1: ESSENTIAL FORMULAS & EQUATIONS

### SECTION 1.1: MECHANICAL ADVANTAGE FUNDAMENTALS

#### IDEAL MECHANICAL ADVANTAGE (IMA):
```
IMA = Load / Effort (ideal, frictionless)
IMA = Distance_effort / Distance_load
IMA = Output_force / Input_force (ideal)
```

**Key Point:** IMA depends ONLY on machine geometry, NOT on friction or efficiency.

#### ACTUAL MECHANICAL ADVANTAGE (AMA):
```
AMA = Load / Effort (actual, with friction)
AMA = Output_force / Input_force (actual)
```

**Critical Relationship:** `AMA ≤ IMA` ALWAYS (due to friction and energy losses)

#### EFFICIENCY:
```
η = AMA / IMA
η = Work_output / Work_input
η = (Output_force × Output_distance) / (Input_force × Input_distance)
```

**Important:** Efficiency is ALWAYS less than 100% (η < 1.0) due to friction and energy losses.

**Efficiency as Percentage:**
```
Efficiency (%) = (AMA / IMA) × 100%
```

> **[ADD IMAGE: IMA vs AMA vs Efficiency Triangle - Shows relationship between IMA, AMA, and efficiency with visual examples]**

#### WORK CONSERVATION:
```
Work_input = Work_output + Work_lost
Work_lost = Work_input × (1 - η)
```

**Key Principle:** Machines cannot create energy; they can only multiply force at the expense of distance.

---

### SECTION 1.2: LEVER FORMULAS

#### LEVER MECHANICAL ADVANTAGE:
```
IMA = Effort_arm_length / Load_arm_length
IMA = Distance_from_fulcrum_effort / Distance_from_fulcrum_load
```

**Memory Aid:** Longer effort arm = greater mechanical advantage

#### LEVER EQUILIBRIUM (Torque Balance):
```
Effort × Effort_arm = Load × Load_arm
F₁ × d₁ = F₂ × d₂
```

For balanced lever: `Στ = 0` (sum of torques equals zero)

#### LEVER CLASSES:

**First Class Lever:**
- Fulcrum between load and effort
- IMA can be > 1, = 1, or < 1
- Examples: Scissors, seesaw, crowbar

**Second Class Lever:**
- Load between fulcrum and effort
- IMA always > 1 (mechanical advantage)
- Examples: Wheelbarrow, nutcracker, bottle opener

**Third Class Lever:**
- Effort between fulcrum and load
- IMA always < 1 (mechanical disadvantage, but speed advantage)
- Examples: Tweezers, human arm, fishing rod

> **[ADD IMAGE: Three Lever Classes Diagram - Shows fulcrum (F), load (L), and effort (E) positions for each class with labeled examples]**

#### COMMON LEVER IDENTIFICATIONS:

| Object | Lever Class | Reasoning |
|--------|-------------|-----------|
| Scissors | First | Fulcrum (pivot) between blades (load) and handles (effort) |
| Wheelbarrow | Second | Load (weight) between wheel (fulcrum) and handles (effort) |
| Nutcracker | Second | Nut (load) between pivot (fulcrum) and handles (effort) |
| Tweezers | Third | Effort (fingers) between pivot (fulcrum) and object (load) |
| Crowbar | First | Fulcrum between object (load) and handle (effort) |
| Stapler | Second | Paper (load) between pivot (fulcrum) and handle (effort) |
| Hammer (pulling nail) | First | Fulcrum between nail (load) and handle (effort) |
| Human arm | Third | Effort (muscle) between elbow (fulcrum) and hand (load) |
| Fishing rod | Third | Effort (hand) between reel (fulcrum) and tip (load) |
| Bottle opener | Second | Cap (load) between pivot (fulcrum) and handle (effort) |
| Brake pedal | First | Fulcrum between brake mechanism (load) and foot (effort) |

---

### SECTION 1.3: PULLEY SYSTEM FORMULAS

#### PULLEY IMA DETERMINATION:
```
IMA = Number of rope segments supporting the load
```

**Key Method:** Count the number of rope segments that directly support the movable pulley(s) or load.

#### MOVABLE VS FIXED PULLEYS:

**Fixed Pulley:**
- IMA = 1 (changes direction only, no force multiplication)
- Effort = Load (ideal)

**Movable Pulley:**
- IMA = 2 (one movable pulley)
- Effort = Load / 2 (ideal)

**Multiple Movable Pulleys:**
- IMA = 2^n (where n = number of movable pulleys)
- OR count supporting rope segments

#### BLOCK AND TACKLE:
```
IMA = Number of supporting rope segments
```

Common configurations:
- 2 pulleys (1 fixed, 1 movable): IMA = 2
- 4 pulleys (2 fixed, 2 movable): IMA = 4
- 6 pulleys (3 fixed, 3 movable): IMA = 6

#### PULLEY EFFICIENCY:
```
AMA = Load / Effort_actual
η = AMA / IMA
```

With friction: `Effort_actual = Load / (IMA × η)`

#### SPECIAL PULLEY SYSTEMS:

**Gun Tackle:**
- IMA = 2
- One fixed, one movable pulley

**Gyn Tackle:**
- IMA = 3
- Specific configuration with 3 supporting ropes

**Single Luff Tackle:**
- IMA = 3
- One fixed pulley, one movable pulley with specific rope routing

**Twofold Purchase:**
- IMA = 4
- Two fixed, two movable pulleys

**Threefold Purchase:**
- IMA = 6
- Three fixed, three movable pulleys

> **[ADD IMAGE: Pulley System Configurations - Shows fixed vs movable pulleys, block and tackle, and special tackle types with IMA labeled]**

---

### SECTION 1.4: INCLINED PLANE FORMULAS

#### INCLINED PLANE IMA:
```
IMA = Length / Height
IMA = L / h
IMA = 1 / sin(θ)  [where θ is the angle of incline]
```

**Memory Aid:** Longer ramp = greater mechanical advantage

#### INCLINED PLANE EFFORT FORCE (Frictionless):
```
Effort = Load × sin(θ)
Effort = mg × sin(θ)
Effort = Load × (Height / Length)
```

#### INCLINED PLANE WITH FRICTION:
```
Effort = Load × sin(θ) + Friction
Effort = mg × sin(θ) + μ × mg × cos(θ)
Effort = mg × (sin(θ) + μ × cos(θ))
```

Where:
- μ = coefficient of friction
- θ = angle of incline

#### WORK ON INCLINED PLANE:
```
Work = Effort × Length
Work = Load × Height (output work, ideal)
Work_with_friction = Load × Height + Friction × Length
```

#### ANGLE FROM IMA:
```
θ = arcsin(Height / Length)
θ = arcsin(1 / IMA)
```

> **[ADD IMAGE: Inclined Plane Force Diagram - Shows ramp with length L, height h, angle θ, with force vectors: weight (mg), normal force (N), friction (f), and effort force (F) labeled]**

---

### SECTION 1.5: SCREW FORMULAS

#### SCREW IMA (Basic):
```
IMA = Circumference / Pitch
IMA = 2πr / p
IMA = πd / p
```

Where:
- r = radius of screw (or handle radius)
- d = diameter of screw
- p = pitch (distance between threads)

#### SCREW IMA (With Handle):
```
IMA = 2πR / p
```

Where:
- R = radius of handle/wrench
- p = pitch

**Memory Aid:** Larger handle radius = greater mechanical advantage

#### PITCH VS LEAD:

**Pitch:**
- Distance between adjacent threads
- Measured parallel to axis

**Lead:**
- Distance screw advances in one complete turn
- For single-start screw: Lead = Pitch
- For multi-start screw: Lead = Pitch × Number_of_starts

**Example:** Double-start screw with 2mm pitch has 4mm lead

#### SCREW THREAD SPECIFICATION:
```
M × p mm
```

Example: M8 × 1.25 mm
- M8 = metric thread, 8mm diameter
- 1.25 mm = pitch

#### SELF-LOCKING CONDITION:
```
tan(λ) < μ
```

Where:
- λ = lead angle = arctan(p / (2πr))
- μ = coefficient of friction

**If self-locking:** Screw will not back-drive under load
**If NOT self-locking:** Screw will back-drive, requires holding force

#### SCREW EFFICIENCY:
```
η = AMA / IMA
```

Higher efficiency → More likely to back-drive (less self-locking)

> **[ADD IMAGE: Screw Thread Diagram - Shows pitch, lead, diameter, and lead angle (λ) with labeled measurements]**

---

### SECTION 1.6: WEDGE FORMULAS

#### WEDGE IMA:
```
IMA = Length / Thickness
IMA = L / t
IMA = 1 / tan(α)  [for symmetric wedge with half-angle α]
```

Where:
- L = length of wedge (slope length)
- t = thickness (separation distance)
- α = half-angle of wedge

**Memory Aid:** Thinner wedge = greater mechanical advantage

#### WEDGE WITH SEPARATION ANGLE:
For wedge with total separation angle 2α:
```
IMA = 1 / tan(α)
```

**Example:** 18° separation angle (2α = 18°, so α = 9°)
- IMA = 1 / tan(9°) ≈ 1 / 0.158 ≈ 6.3

#### EQUILATERAL WEDGE:
For equilateral wedge (60° angles):
```
IMA = √3 ≈ 1.732
```

#### WEDGE SELF-LOCKING:
Wedge is self-locking when friction prevents it from sliding out.

**Condition:** Depends on wedge angle and coefficient of friction

> **[ADD IMAGE: Wedge Diagram - Shows wedge with length L, thickness t, half-angle α, with force vectors showing input force and output separation force]**

---

### SECTION 1.7: WHEEL AND AXLE FORMULAS

#### WHEEL AND AXLE IMA:
```
IMA = Radius_wheel / Radius_axle
IMA = R / r
```

**Memory Aid:** Larger wheel radius = greater mechanical advantage

#### WHEEL AND AXLE AS LEVER:
Wheel and axle is essentially a continuous lever:
- Effort applied at wheel rim
- Load applied at axle
- IMA = R_effort / R_load

#### WHEEL AND AXLE EFFICIENCY:
```
AMA = Load / Effort_actual
η = AMA / IMA
```

#### COMMON EXAMPLES:
- Door knob: Wheel (knob) and axle (spindle)
- Steering wheel: Large wheel, small axle
- Windlass: Wheel (drum) and axle (shaft)

> **[ADD IMAGE: Wheel and Axle Diagram - Shows large wheel radius R and small axle radius r, with effort force on wheel and load force on axle]**

---

### SECTION 1.8: GEAR FORMULAS

#### GEAR RATIO:
```
Gear_Ratio = N_driver / N_driven
Gear_Ratio = Teeth_driver / Teeth_driven
```

#### ANGULAR VELOCITY RELATIONSHIP:
```
ω_driven / ω_driver = N_driver / N_driven
ω₂ / ω₁ = N₁ / N₂
```

**Memory Aid:** More teeth = slower rotation

#### GEAR MECHANICAL ADVANTAGE:
```
IMA = N_driver / N_driven
```

For torque multiplication: More teeth on driven gear = greater torque

#### GEAR TRAIN (Multiple Gears):
```
Overall_Ratio = (N₁/N₂) × (N₃/N₄) × ...
```

For gears on same shaft: They rotate together (same angular velocity)

#### GEAR TYPES:

**Spur Gear:**
- Straight teeth, parallel axes
- Most common type

**Helical Gear:**
- Angled teeth, smoother operation
- Can transmit power between parallel or crossed axes

**Worm Gear:**
- Worm (screw-like) drives gear
- High reduction ratio
- Often self-locking

**Miter Gear:**
- 90° angle between axes
- Same number of teeth on both gears

**Rack and Pinion:**
- Converts rotational to linear motion
- Pinion (gear) drives rack (straight bar)

**Hypoid Gear:**
- Similar to spiral bevel gear
- Offset axes

> **[ADD IMAGE: Gear Types Diagram - Shows spur, helical, worm, miter, rack and pinion, and hypoid gears with labeled characteristics]**

---

### SECTION 1.9: WORK, ENERGY, AND EFFICIENCY

#### WORK DEFINITION:
```
Work = Force × Distance (in direction of force)
W = F × d
```

Units: Joules (J) = Newton-meters (N·m)

#### WORK ON MACHINES:
```
Work_input = Effort × Distance_effort
Work_output = Load × Distance_load
```

#### WORK CONSERVATION (Ideal Machine):
```
Work_input = Work_output (ideal, no losses)
```

#### WORK WITH EFFICIENCY:
```
Work_output = η × Work_input
Work_lost = Work_input × (1 - η)
```

#### POWER:
```
Power = Work / Time
P = W / t
P = Force × Velocity
```

Units: Watts (W) = Joules/second (J/s)

#### ENERGY CONSERVATION:
```
Energy_input = Energy_output + Energy_lost
```

Energy lost primarily as heat from friction

#### POTENTIAL ENERGY:
```
PE = mgh
```

Where:
- m = mass
- g = gravitational acceleration (9.8 m/s²)
- h = height

#### KINETIC ENERGY:
```
KE = ½mv²
```

Where:
- m = mass
- v = velocity

---

### SECTION 1.10: FRICTION AND ANGLE OF REPOSE

#### COEFFICIENT OF FRICTION:
```
μ = F_friction / F_normal
μ = F_f / N
```

#### STATIC VS KINETIC FRICTION:
```
μ_static ≥ μ_kinetic (always)
```

Static friction: Prevents motion
Kinetic friction: Opposes motion

#### FRICTION FORCE:
```
F_friction = μ × F_normal
F_f = μN
```

#### ANGLE OF REPOSE:
```
μ_static = tan(θ_repose)
θ_repose = arctan(μ_static)
```

**Definition:** Maximum angle at which material will remain at rest without sliding

#### INCLINED PLANE FRICTION:
For object on incline at angle θ:
```
F_friction = μ × mg × cos(θ)
F_normal = mg × cos(θ)
```

Object begins sliding when:
```
tan(θ) = μ_static
```

#### FRICTION AND EFFICIENCY:
Friction always reduces efficiency:
```
η = (Work_output) / (Work_output + Work_friction)
```

Higher friction → Lower efficiency

> **[ADD IMAGE: Friction on Inclined Plane - Shows block on ramp with friction force, normal force, weight components, and angle of repose demonstration]**

---

## SECTION 2: MACHINE TYPES & IDENTIFICATION

### SECTION 2.1: LEVER CLASSES (First/Second/Third)

#### FIRST CLASS LEVER:

**Characteristics:**
- Fulcrum between load and effort
- IMA can be > 1, = 1, or < 1
- Can multiply force OR speed

**Common Examples:**
- Scissors (fulcrum = pivot, load = material being cut, effort = handles)
- Seesaw (fulcrum = center, load = person on one side, effort = person on other)
- Crowbar (fulcrum = pivot point, load = object being lifted, effort = handle)
- Hammer pulling nail (fulcrum = pivot, load = nail, effort = handle)
- Brake pedal (fulcrum = pivot, load = brake mechanism, effort = foot)
- Pliers (fulcrum = pivot, load = object, effort = handles)
- Nutcracker (some designs - fulcrum between nut and handles)

**Visual Pattern:** F - L - E or F - E - L (fulcrum in middle)

#### SECOND CLASS LEVER:

**Characteristics:**
- Load between fulcrum and effort
- IMA always > 1 (mechanical advantage)
- Always multiplies force

**Common Examples:**
- Wheelbarrow (fulcrum = wheel, load = contents, effort = handles)
- Nutcracker (fulcrum = pivot, load = nut, effort = handles)
- Bottle opener (fulcrum = pivot, load = cap, effort = handle)
- Stapler (fulcrum = pivot, load = paper, effort = handle)
- Door (fulcrum = hinges, load = door weight, effort = handle)
- Can opener (fulcrum = pivot, load = can lid, effort = handle)

**Visual Pattern:** F - L - E (load in middle)

#### THIRD CLASS LEVER:

**Characteristics:**
- Effort between fulcrum and load
- IMA always < 1 (mechanical disadvantage)
- Multiplies speed/distance instead of force

**Common Examples:**
- Tweezers (fulcrum = pivot, effort = fingers, load = object)
- Human arm (fulcrum = elbow, effort = bicep muscle, load = hand/object)
- Fishing rod (fulcrum = reel, effort = hand, load = tip/line)
- Shovel (fulcrum = hand on shaft, effort = other hand, load = dirt)
- Broom (fulcrum = hand near middle, effort = other hand, load = bristles)
- Rake (fulcrum = hand, effort = other hand, load = tines)

**Visual Pattern:** F - E - L (effort in middle)

#### LEVER IDENTIFICATION STRATEGY:

1. **Find the fulcrum** (pivot point)
2. **Identify the load** (what is being moved/lifted)
3. **Identify the effort** (where force is applied)
4. **Determine order:** F - L - E, F - E - L, or L - F - E

> **[ADD IMAGE: Lever Class Identification Flowchart - Step-by-step process for identifying lever classes with examples]**

---

### SECTION 2.2: PULLEY TYPES AND CONFIGURATIONS

#### FIXED PULLEY:

**Characteristics:**
- Pulley attached to fixed support
- IMA = 1
- Changes direction only
- No force multiplication

**Example:** Single pulley on ceiling lifting weight

#### MOVABLE PULLEY:

**Characteristics:**
- Pulley attached to load
- IMA = 2
- Multiplies force
- Load moves half the distance of rope pulled

**Example:** Pulley attached to weight, rope goes up to fixed point

#### BLOCK AND TACKLE:

**Configuration:**
- Multiple pulleys (fixed + movable)
- IMA = number of supporting rope segments

**Common Setups:**
- 2 pulleys: IMA = 2
- 4 pulleys: IMA = 4
- 6 pulleys: IMA = 6

#### COUNTING SUPPORTING ROPES:

**Method:**
1. Identify the load or movable pulley
2. Count rope segments that directly support it
3. Each segment contributes to IMA

**Key Point:** Rope segments that don't support the load don't count!

#### SPECIAL PULLEY SYSTEMS:

**Gun Tackle:**
- IMA = 2
- One fixed, one movable pulley
- Rope attached to fixed support

**Gyn Tackle:**
- IMA = 3
- Specific rope routing
- Three supporting rope segments

**Single Luff Tackle:**
- IMA = 3
- One fixed, one movable pulley
- Rope goes through fixed pulley first

**Twofold Purchase:**
- IMA = 4
- Two fixed, two movable pulleys
- Four supporting rope segments

**Threefold Purchase:**
- IMA = 6
- Three fixed, three movable pulleys
- Six supporting rope segments

**Differential Pulley:**
- Two pulleys of different radii (R and r) on same shaft
- IMA = 2R / (R - r)
- Very high mechanical advantage possible

> **[ADD IMAGE: Pulley System Gallery - Shows all pulley types with labeled IMA and rope routing]**

---

### SECTION 2.3: SCREW SPECIFICATIONS

#### SCREW THREAD TYPES:

**Metric Threads (M):**
- Format: M × pitch
- Example: M8 × 1.25 (8mm diameter, 1.25mm pitch)

**Unified Threads (UNC/UNF):**
- UNC = Coarse thread
- UNF = Fine thread
- Example: 1/4-20 UNC (1/4 inch diameter, 20 threads per inch)

#### SINGLE-START VS MULTI-START SCREWS:

**Single-Start:**
- One thread path
- Lead = Pitch
- Most common

**Double-Start:**
- Two thread paths
- Lead = 2 × Pitch
- Faster advancement

**Triple-Start:**
- Three thread paths
- Lead = 3 × Pitch
- Very fast advancement

#### SCREW HEAD TYPES:

**Socket Head (Cap Screw):**
- Hex socket in head
- Requires Allen wrench

**Hex Head:**
- External hex
- Requires wrench

**Phillips/Slotted:**
- For screwdriver
- Lower torque capacity

#### SCREW APPLICATIONS:

**Screw Jack:**
- Lifting heavy loads
- Very high IMA
- Often self-locking

**Bolt and Nut:**
- Fastening
- Thread engagement determines strength

**Lead Screw:**
- Precision linear motion
- Used in machines (lathes, 3D printers)

> **[ADD IMAGE: Screw Thread Types - Shows single-start, double-start, triple-start with pitch and lead labeled]**

---

### SECTION 2.4: WEDGE APPLICATIONS

#### COMMON WEDGE EXAMPLES:

**Cutting Tools:**
- Knife blade
- Axe head
- Chisel
- Scissors blades

**Splitting Tools:**
- Axe (splitting wood)
- Wedge (splitting logs)
- Doorstop

**Holding Tools:**
- Doorstop (self-locking)
- Shims
- Chocks

#### WEDGE DESIGN CONSIDERATIONS:

**Bread Knife (Serrated):**
- Toothed edge
- Requires sawing motion
- Teeth increase effective cutting surface

**Chef's Knife (Smooth):**
- Smooth edge
- Single slicing motion
- Cleaner cut

**Axe:**
- Wide angle for splitting
- Narrow angle for cutting
- Balance between penetration and force

> **[ADD IMAGE: Wedge Applications - Shows knife, axe, doorstop with force vectors and IMA considerations]**

---

### SECTION 2.5: WHEEL AND AXLE EXAMPLES

#### COMMON EXAMPLES:

**Door Knob:**
- Wheel: Knob (large radius)
- Axle: Spindle (small radius)
- IMA = R_knob / R_spindle

**Steering Wheel:**
- Wheel: Steering wheel (large radius)
- Axle: Steering column (small radius)
- High IMA for easy turning

**Windlass:**
- Wheel: Drum (large radius)
- Axle: Shaft (small radius)
- Used for lifting (wells, anchors)

**Bicycle Pedal:**
- Wheel: Pedal crank (large radius)
- Axle: Chainring (small radius)
- Converts foot force to chain force

**Screwdriver:**
- Wheel: Handle (large radius)
- Axle: Shaft (small radius)
- Increases torque applied to screw

**Winch:**
- Wheel: Winch drum
- Axle: Shaft
- Lifting mechanism

> **[ADD IMAGE: Wheel and Axle Examples - Shows door knob, steering wheel, windlass with labeled radii]**

---

### SECTION 2.6: GEAR TYPES

#### SPUR GEAR:
- Straight teeth
- Parallel axes
- Most common
- Efficient power transmission

#### HELICAL GEAR:
- Angled teeth
- Smoother, quieter operation
- Can handle higher loads
- Parallel or crossed axes

#### WORM GEAR:
- Worm (screw) drives gear
- Very high reduction ratio
- Often self-locking
- 90° axis orientation

#### MITER GEAR:
- 90° angle between axes
- Same number of teeth
- Equal speed ratio (1:1)
- Used for direction change

#### RACK AND PINION:
- Converts rotation to linear motion
- Pinion (gear) drives rack (straight bar)
- Used in steering systems

#### HYPoid GEAR:
- Similar to spiral bevel
- Offset axes
- Used in automotive differentials

#### GEAR RATIO CALCULATION:
```
Speed_Ratio = N_driver / N_driven
Torque_Ratio = N_driven / N_driver
```

> **[ADD IMAGE: Gear Types Gallery - Shows all gear types with characteristics labeled]**

---

### SECTION 2.7: COMPOUND MACHINES

#### COMPOUND MACHINE PRINCIPLE:
```
IMA_total = IMA₁ × IMA₂ × IMA₃ × ...
```

**Key Point:** IMAs multiply, but efficiencies also multiply (and always decrease)

#### COMPOUND MACHINE EFFICIENCY:
```
η_total = η₁ × η₂ × η₃ × ...
```

**Important:** Total efficiency is ALWAYS less than individual efficiencies

#### COMMON COMPOUND MACHINES:

**Wheelbarrow:**
- Lever (second class) + Wheel and Axle
- IMA = IMA_lever × IMA_wheel_axle

**Screw Jack:**
- Lever (handle) + Screw
- IMA = IMA_lever × IMA_screw
- Very high IMA possible

**Bicycle:**
- Lever (pedals) + Wheel and Axle + Gears
- Multiple stages

**Can Opener:**
- Lever + Gear + Wheel and Axle
- Multiple mechanical advantages

**Scissors:**
- Two first-class levers
- IMA = IMA₁ × IMA₂ (if considered compound)

#### COMPOUND MACHINE ANALYSIS STEPS:

1. Identify all simple machines in the system
2. Calculate IMA for each machine
3. Multiply IMAs: `IMA_total = IMA₁ × IMA₂ × ...`
4. Calculate efficiency for each stage
5. Multiply efficiencies: `η_total = η₁ × η₂ × ...`
6. Calculate AMA: `AMA_total = IMA_total × η_total`

> **[ADD IMAGE: Compound Machine Examples - Shows wheelbarrow, screw jack, bicycle with labeled simple machine components]**

---

## SECTION 3: QUICK REFERENCE TABLES

### SECTION 3.1: COMMON LEVER CLASSIFICATIONS

| Object | Lever Class | Fulcrum | Load | Effort | IMA |
|--------|-------------|---------|------|--------|-----|
| Scissors | First | Pivot | Material | Handles | Variable |
| Wheelbarrow | Second | Wheel | Contents | Handles | > 1 |
| Nutcracker | Second | Pivot | Nut | Handles | > 1 |
| Tweezers | Third | Pivot | Object | Fingers | < 1 |
| Crowbar | First | Pivot | Object | Handle | > 1 |
| Stapler | Second | Pivot | Paper | Handle | > 1 |
| Bottle opener | Second | Pivot | Cap | Handle | > 1 |
| Human arm | Third | Elbow | Hand | Bicep | < 1 |
| Fishing rod | Third | Reel | Tip | Hand | < 1 |
| Hammer (pulling nail) | First | Pivot | Nail | Handle | > 1 |
| Brake pedal | First | Pivot | Brake | Foot | Variable |
| Shovel | Third | Hand | Dirt | Other hand | < 1 |

---

### SECTION 3.2: STANDARD MECHANICAL ADVANTAGE VALUES

#### TYPICAL IMA RANGES:

**Levers:**
- First class: 0.1 to 10 (variable)
- Second class: 1.5 to 5 (always > 1)
- Third class: 0.1 to 0.9 (always < 1)

**Pulleys:**
- Fixed pulley: 1
- Movable pulley: 2
- Block and tackle: 2, 4, 6, 8, etc.

**Inclined Planes:**
- Gentle slope: 2 to 5
- Moderate slope: 5 to 10
- Steep slope: 10+

**Screws:**
- Fine thread: 50 to 500
- Coarse thread: 20 to 200
- With handle: 100 to 1000+

**Wedges:**
- Thin wedge: 5 to 20
- Thick wedge: 2 to 5

**Wheel and Axle:**
- Door knob: 5 to 10
- Steering wheel: 10 to 20
- Windlass: 5 to 15

**Gears:**
- Single reduction: 2 to 10
- Multiple reduction: 10 to 100+

---

### SECTION 3.3: FRICTION COEFFICIENTS

#### TYPICAL COEFFICIENT OF FRICTION VALUES:

**Static Friction (μ_s):**
- Steel on steel: 0.6 - 0.8
- Wood on wood: 0.4 - 0.6
- Rubber on concrete: 0.7 - 1.0
- Metal on metal (lubricated): 0.1 - 0.2
- Ice on ice: 0.02 - 0.05
- Sand: 0.4 - 0.6

**Kinetic Friction (μ_k):**
- Usually 70-90% of static friction
- Steel on steel: 0.4 - 0.6
- Wood on wood: 0.2 - 0.4

#### ANGLE OF REPOSE (from μ):
```
θ = arctan(μ)
```

Common angles:
- Sand: 30-35°
- Gravel: 35-40°
- Dry soil: 30-45°
- Wet clay: 10-20°

---

### SECTION 3.4: UNIT CONVERSIONS

#### LENGTH:
- 1 m = 100 cm = 1000 mm
- 1 ft = 12 in = 0.3048 m
- 1 in = 2.54 cm = 25.4 mm

#### FORCE:
- 1 N = 0.225 lbf (pounds-force)
- 1 lbf = 4.448 N
- 1 kg = 9.8 N (on Earth)

#### ENERGY/WORK:
- 1 J = 1 N·m
- 1 J = 0.239 cal
- 1 kWh = 3.6 × 10⁶ J

#### POWER:
- 1 W = 1 J/s
- 1 hp = 746 W
- 1 kW = 1000 W

#### ANGLES:
- 180° = π radians
- 1° = π/180 radians
- 1 radian = 180/π ≈ 57.3°

---

### SECTION 3.5: PHYSICAL CONSTANTS

#### GRAVITATIONAL ACCELERATION:
```
g = 9.8 m/s² (standard value used in tests)
g = 32.2 ft/s²
```

#### MATHEMATICAL CONSTANTS:
```
π = 3.14159...
√2 = 1.414...
√3 = 1.732...
```

#### COMMON TRIGONOMETRIC VALUES:
```
sin(0°) = 0          cos(0°) = 1
sin(30°) = 0.5      cos(30°) = 0.866
sin(45°) = 0.707    cos(45°) = 0.707
sin(60°) = 0.866    cos(60°) = 0.5
sin(90°) = 1        cos(90°) = 0

tan(0°) = 0
tan(30°) = 0.577
tan(45°) = 1
tan(60°) = 1.732
```

---

## SECTION 4: PROBLEM-SOLVING FRAMEWORKS

### SECTION 4.1: MECHANICAL ADVANTAGE CALCULATION STRATEGY

#### STEP-BY-STEP APPROACH:

1. **Identify the machine type**
   - Lever, pulley, inclined plane, screw, wedge, wheel-axle, gear

2. **Determine IMA formula**
   - Use appropriate formula for machine type

3. **Identify given values**
   - Extract dimensions, forces, distances from problem

4. **Calculate IMA**
   - Plug values into formula
   - Check units

5. **If asked for AMA:**
   - Use: `AMA = Load / Effort_actual`
   - Or: `AMA = IMA × η`

6. **If asked for efficiency:**
   - Use: `η = AMA / IMA`

#### COMMON MISTAKES TO AVOID:

- **Confusing IMA and AMA:** IMA is ideal (frictionless), AMA is actual
- **Wrong formula:** Using lever formula for pulley, etc.
- **Unit errors:** Mixing meters and centimeters, etc.
- **Sign errors:** Forgetting that third-class levers have IMA < 1

---

### SECTION 4.2: EFFICIENCY PROBLEM APPROACH

#### EFFICIENCY CALCULATION STEPS:

1. **Calculate IMA** (from geometry)
2. **Calculate AMA** (from actual forces: Load/Effort)
3. **Calculate efficiency:** `η = AMA / IMA`

#### ALTERNATIVE METHODS:

**From Work:**
```
η = Work_output / Work_input
η = (Load × Distance_load) / (Effort × Distance_effort)
```

**From Power:**
```
η = Power_output / Power_input
```

#### EFFICIENCY IN COMPOUND MACHINES:

1. Calculate efficiency for each stage
2. Multiply: `η_total = η₁ × η₂ × η₃ × ...`

**Key Point:** Total efficiency is ALWAYS less than individual efficiencies

---

### SECTION 4.3: COMPOUND MACHINE ANALYSIS

#### ANALYSIS PROCEDURE:

1. **Break down into simple machines**
   - Identify each component machine

2. **Calculate IMA for each**
   - Use appropriate formulas

3. **Multiply IMAs**
   ```
   IMA_total = IMA₁ × IMA₂ × IMA₃ × ...
   ```

4. **Calculate efficiency for each stage**
   - If given: Use directly
   - If not given: Assume or calculate from forces

5. **Multiply efficiencies**
   ```
   η_total = η₁ × η₂ × η₃ × ...
   ```

6. **Calculate total AMA**
   ```
   AMA_total = IMA_total × η_total
   ```

7. **Calculate required effort**
   ```
   Effort = Load / AMA_total
   ```

---

### SECTION 4.4: SELF-LOCKING DETERMINATION

#### FOR SCREWS:

1. **Calculate lead angle:**
   ```
   λ = arctan(p / (2πr))
   ```
   Where:
   - p = pitch
   - r = mean radius

2. **Compare to friction coefficient:**
   ```
   If tan(λ) < μ: Self-locking
   If tan(λ) ≥ μ: NOT self-locking (will back-drive)
   ```

3. **Consider efficiency:**
   - Higher efficiency → More likely to back-drive
   - Lower efficiency → More likely self-locking

#### FOR WEDGES:

1. **Determine wedge angle**
2. **Compare to friction**
3. **If friction sufficient:** Self-locking

---

## SECTION 5: VISUAL GUIDES & MENTAL MODELS

### SECTION 5.1: LEVER CLASS DIAGRAMS

> **[ADD IMAGE: Lever Class Comparison - Side-by-side diagrams of all three lever classes showing F, L, E positions with real-world examples]**

**Memory Aid:**
- **First:** Fulcrum in the **First** position (middle)
- **Second:** Load in the **Second** position (middle)
- **Third:** Effort in the **Third** position (middle)

---

### SECTION 5.2: PULLEY SYSTEM CONFIGURATIONS

> **[ADD IMAGE: Pulley System Gallery - Shows fixed, movable, block and tackle, and special tackle types with rope routing and IMA labeled]**

**Counting Ropes Method:**
- Draw arrows showing rope direction
- Count segments that support the load
- Each segment = +1 to IMA

---

### SECTION 5.3: INCLINED PLANE FORCE ANALYSIS

> **[ADD IMAGE: Inclined Plane Force Decomposition - Shows weight vector broken into components parallel and perpendicular to ramp, with friction and normal forces]**

**Force Components:**
- Weight parallel to ramp: `mg sin(θ)` (downhill)
- Weight perpendicular to ramp: `mg cos(θ)` (normal)
- Friction: `μ × mg cos(θ)` (uphill)
- Effort needed: `mg sin(θ) + μ × mg cos(θ)`

---

### SECTION 5.4: SCREW THREAD VISUALIZATION

> **[ADD IMAGE: Screw Thread Anatomy - Shows pitch, lead, diameter, lead angle with single-start and multi-start examples]**

**Key Relationships:**
- Pitch = thread spacing
- Lead = advancement per turn
- Lead angle = arctan(lead / circumference)

---

### SECTION 5.5: COMPOUND MACHINE COMBINATIONS

> **[ADD IMAGE: Compound Machine Breakdowns - Shows wheelbarrow, screw jack, bicycle with labeled simple machine components and IMA calculations]**

---

## SECTION 6: COMMON PITFALLS & TIPS

### SECTION 6.1: FORMULA MISAPPLICATION

#### COMMON ERRORS:

**Using wrong IMA formula:**
- ❌ Using lever formula for pulley
- ✅ Identify machine type first, then use correct formula

**Confusing pitch and lead:**
- ❌ Using pitch when lead is needed (multi-start screws)
- ✅ Lead = Pitch × Number_of_starts

**Wrong lever class identification:**
- ❌ Misidentifying fulcrum position
- ✅ Always find fulcrum first, then determine order

**Incorrect pulley counting:**
- ❌ Counting all rope segments
- ✅ Count only segments supporting the load

---

### SECTION 6.2: IMA VS AMA CONFUSION

#### KEY DISTINCTIONS:

**IMA (Ideal Mechanical Advantage):**
- Depends ONLY on geometry
- Frictionless, ideal conditions
- Always calculable from dimensions

**AMA (Actual Mechanical Advantage):**
- Depends on actual forces
- Includes friction and losses
- Always: `AMA ≤ IMA`

#### COMMON MISTAKES:

- Using IMA when AMA is asked (or vice versa)
- Forgetting that AMA is always less than or equal to IMA
- Calculating efficiency incorrectly: `η = AMA/IMA` (NOT `IMA/AMA`)

---

### SECTION 6.3: EFFICIENCY CALCULATION ERRORS

#### CORRECT FORMULAS:

```
η = AMA / IMA
η = Work_output / Work_input
η = (Load × Distance_load) / (Effort × Distance_effort)
```

#### COMMON ERRORS:

- ❌ `η = IMA / AMA` (backwards!)
- ❌ Using ideal forces instead of actual forces
- ❌ Forgetting that efficiency < 100% always
- ❌ In compound machines: Adding efficiencies instead of multiplying

---

### SECTION 6.4: UNIT CONVERSION MISTAKES

#### COMMON ISSUES:

**Length units:**
- Mixing meters, centimeters, millimeters
- Forgetting feet to meters conversion (1 ft = 0.3048 m)

**Force units:**
- Confusing mass (kg) and force (N)
- On Earth: Weight (N) = mass (kg) × 9.8 m/s²

**Angle units:**
- Using degrees in formulas requiring radians
- Remember: `sin(θ)` and `cos(θ)` use degrees, but angular frequency uses radians

#### CONVERSION CHECKLIST:

- [ ] All lengths in same units
- [ ] Forces in Newtons (or consistent unit)
- [ ] Angles in correct unit (degrees vs radians)
- [ ] Final answer in requested units

---

## SECTION 7: TEST-SPECIFIC STRATEGIES

### SECTION 7.1: UGA TEST FOCUS (Fundamentals)

**Test Characteristics:**
- 24 questions, 24 points
- Focused on core concepts
- Straightforward calculations

**Key Topics:**
- Lever class identification (7 questions!)
- Basic IMA/AMA calculations
- Efficiency fundamentals
- Friction and angle of repose

**Study Strategy:**
- Master lever classes (critical!)
- Know IMA vs AMA definitions
- Practice basic calculations
- Understand efficiency relationship

**Common Question Types:**
- Matching lever classes to objects
- Simple IMA calculations
- Efficiency from given forces
- Angle of repose from friction coefficient

---

### SECTION 7.2: UT AUSTIN TEST FOCUS (Comprehensive)

**Test Characteristics:**
- 119 questions, variable points
- Very broad coverage
- Mix of True/False, MC, calculations
- Strong emphasis on compound machines

**Key Topics:**
- All machine types covered
- Extensive compound machine problems
- Comprehensive lever coverage
- Detailed pulley systems

**Study Strategy:**
- Know ALL machine types thoroughly
- Master compound machine analysis
- Practice multi-step calculations
- Understand relationships between concepts

**Common Question Types:**
- True/False on fundamental concepts
- Compound machine IMA calculations
- Multi-stage efficiency problems
- Gear train calculations

---

### SECTION 7.3: HAWK&HORNET TEST FOCUS (Physics Integration)

**Test Characteristics:**
- ~33 questions, 80.5 points
- Heavy physics integration
- Advanced mechanics concepts
- Dimensional analysis

**Key Topics:**
- Newton's laws applications
- Momentum and energy conservation
- Moment of inertia
- Dimensional analysis
- Advanced inclined plane problems

**Study Strategy:**
- Review fundamental physics
- Understand energy conservation
- Practice dimensional analysis
- Know moment of inertia basics

**Common Question Types:**
- Physics-integrated machine problems
- Energy conservation applications
- Dimensional analysis questions
- Advanced calculations with friction

---

### SECTION 7.4: MVSO TEST FOCUS (Advanced Problem-Solving)

**Test Characteristics:**
- 50 questions, ~200 points
- Extensive problem-solving
- Rotational dynamics
- Advanced pulley systems

**Key Topics:**
- Complex pulley configurations
- Rotational motion
- Banked curves
- Differential pulley systems
- Advanced mechanics

**Study Strategy:**
- Master pulley system analysis
- Understand rotational dynamics
- Practice multi-step derivations
- Know special pulley types (Gun Tackle, Gyn Tackle, etc.)

**Common Question Types:**
- Complex pulley system IMA
- Rotational dynamics problems
- Banked curve calculations
- Differential pulley derivations

---

### SECTION 7.5: RICKARDS TEST FOCUS (Theoretical Depth)

**Test Characteristics:**
- 62 questions, 150 points
- Graduate-level physics
- Differential equations
- Variable mechanical advantage

**Key Topics:**
- Theoretical derivations
- Differential equations (oscillations)
- Variable MA (calculus applications)
- Advanced free response

**Study Strategy:**
- Understand theoretical foundations
- Review calculus applications
- Practice derivations
- Know why formulas work (not just memorization)

**Common Question Types:**
- Derive IMA formulas
- Variable MA with integration
- Differential equation problems
- Theoretical explanations

---

## SECTION 8: DERIVATION QUICK-REFS (For Advanced Questions)

### SECTION 8.1: INCLINED PLANE IMA DERIVATION

#### DERIVATION:

**Starting Point:** Work conservation (ideal machine)
```
Work_input = Work_output
Effort × Distance_effort = Load × Distance_load
```

**For inclined plane:**
- Distance_effort = Length (L)
- Distance_load = Height (h)
- Effort (ideal) = Load × sin(θ) = Load × (h/L)

**Substitute:**
```
Effort × L = Load × h
(Load × h/L) × L = Load × h
Load × h = Load × h ✓
```

**Therefore:**
```
IMA = Load / Effort = Load / (Load × h/L) = L/h
IMA = Length / Height
```

---

### SECTION 8.2: PULLEY IMA DERIVATION

#### DERIVATION (Single Movable Pulley):

**Starting Point:** Work conservation
```
Work_input = Work_output
Effort × Distance_effort = Load × Distance_load
```

**For movable pulley:**
- If rope pulled distance d, load moves distance d/2
- Distance_effort = d
- Distance_load = d/2

**Substitute:**
```
Effort × d = Load × (d/2)
Effort = Load / 2
```

**Therefore:**
```
IMA = Load / Effort = Load / (Load/2) = 2
```

**For multiple pulleys:** Each additional supporting rope segment adds 1 to IMA.

---

### SECTION 8.3: SCREW IMA DERIVATION

#### DERIVATION:

**Starting Point:** Work conservation
```
Work_input = Work_output
Effort × Distance_effort = Load × Distance_load
```

**For screw:**
- Distance_effort = Circumference = 2πR (one turn)
- Distance_load = Pitch = p (advancement per turn)
- Effort applied tangentially at radius R

**Substitute:**
```
Effort × 2πR = Load × p
Effort = Load × p / (2πR)
```

**Therefore:**
```
IMA = Load / Effort = Load / (Load × p/(2πR)) = 2πR / p
IMA = Circumference / Pitch
```

---

### SECTION 8.4: WEDGE IMA DERIVATION

#### DERIVATION (Symmetric Wedge):

**Starting Point:** Force analysis

**For wedge with half-angle α:**
- Input force F_in applied horizontally
- Output force F_out perpendicular to wedge face
- F_out = F_in / sin(α) (from force triangle)

**But IMA = Output_force / Input_force:**
```
IMA = F_out / F_in = (F_in / sin(α)) / F_in = 1 / sin(α)
```

**For small angles:** `sin(α) ≈ tan(α)` (if α is small)

**Also from geometry:** `tan(α) = t / L` (thickness / length)

**Therefore:**
```
IMA ≈ 1 / tan(α) = L / t
IMA = Length / Thickness
```

---

## END OF STUDY BINDER - ESSENTIAL SECTIONS

**Quick Reference Checklist:**
- [ ] Lever classes memorized
- [ ] IMA formulas for all machine types
- [ ] Efficiency relationship understood
- [ ] Friction and angle of repose formulas
- [ ] Compound machine analysis procedure
- [ ] Self-locking conditions
- [ ] Common lever identifications
- [ ] Pulley counting method
- [ ] Unit conversions
- [ ] Test-specific strategies reviewed

**Remember:** Machines multiply force at the expense of distance. Work is conserved (ideal), but efficiency is always less than 100% due to friction!
