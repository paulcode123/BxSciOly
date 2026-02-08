# Science Olympiad Test Parsing Rules

## Purpose
Convert Science Olympiad test PDFs into machine-readable, structured text files for study, analysis, and reference purposes. Each question is tagged with metadata including topic, difficulty, format, and point values.

---

## Critical: No Automated Parsing Scripts

**DO NOT** write parser scripts or automation tools. This is intentional.

**Why:** Manual parsing event-by-event ensures:
- Accurate interpretation of question intent and nuance
- Proper topic tagging with domain expertise
- Appropriate difficulty assessment
- Correct identification of question type and format
- Recognition of special cases and anomalies

**Instead:** Follow this 3-step manual process for each event

---

## Step 1: Convert PDF to TXT

Before parsing begins, extract text from each PDF:

```bash
# Using PyMuPDF (recommended)
python extract_pdf_text.py

# Or use other tools (pdftotext, Adobe, etc.)
pdftotext input.pdf output.txt
```

**Requirements:**
- One `.txt` file per PDF
- Save to corresponding `TestsTXT/` subdirectory
- File naming: `[Event Name] [Year] [Division] TEST.txt`
- UTF-8 encoding
- Preserve all text content including headers, footers, page numbers

**What to expect in TXT output:**
- Question numbers and point values
- Full question text (may wrap across lines)
- Answer options (may need cleaning)
- Page headers/footers (will need removal during parsing)
- Formatting artifacts from PDF extraction

---

## Step 2: Create Todo List for Event

Create a task list to track parsing progress:

```
[ ] Read extracted TXT file completely
[ ] Identify all questions and point values
[ ] Determine question format types
[ ] Assign topic tags to each question
[ ] Assess difficulty levels
[ ] Write header section
[ ] Write question blocks (organized by section if needed)
[ ] Validate completeness
[ ] Final review and formatting
```

**Recommended:** Create one todo per test event in your IDE todo system.

---

## Step 3: Manual Parse Event-by-Event

Process one complete event at a time:

1. **Read the TXT file thoroughly** (don't skim)
   - Understand the overall test structure
   - Note any special sections or themes
   - Identify formatting patterns

2. **Manually extract and structure each question** 
   - Do NOT use find/replace scripts
   - Type/copy question blocks with proper metadata
   - Read answer key if available
   - Verify against original text

3. **Assign topic tags** based on question content
   - Use domain knowledge
   - Be specific (3-level hierarchy)
   - Recognize connections to other topics

4. **Determine difficulty** through careful analysis
   - Consider prerequisite knowledge
   - Evaluate step complexity
   - Compare similar questions

5. **Write parsed TXT file** in target format
   - Follow structure rules exactly
   - Maintain consistent formatting
   - Include all metadata fields

6. **Review and validate**
   - Compare question count to original
   - Verify all point values sum correctly
   - Check for completeness and accuracy
   - Proofread topic tags and difficulty assignments

---

## Workflow Overview

```
PDF Files
   ↓
[Step 1: PDF → TXT Conversion]
   ↓
TXT Files (raw extracted text)
   ↓
[Step 2: Create Todo for Event]
   ↓
[Step 3: Manual Parse Event-by-Event]
   - Read TXT thoroughly
   - Extract questions with metadata
   - Assign topics and difficulty
   - Write parsed output
   ↓
Parsed TXT Files (machine-readable, tagged)
```

---

## File Structure

### Output File Naming
```
MVSO Invite 2025 [EVENT_NAME] C TEST.txt
```
- Location: `/TestBase/TestsParsed/`
- Format: `.txt` (plaintext)
- Naming: Match original PDF filename exactly

### Header Section (Lines 1-5)
```
EVENT: [Official event name]
SOURCE: [Tournament/competition source]
FORMAT: [Total questions] questions ([question types])
TOTAL POINTS: [Sum of all points]
```

Example:
```
EVENT: Anatomy and Physiology
SOURCE: MVSO Invite 2025 (Div. C)
FORMAT: 57 questions (50 MC @ 1pt, 3 MC multi-select @ 3pts, 3 FRQ @ 5pts each)
TOTAL POINTS: 70
```

**How to determine these values:**
- **EVENT**: Official event name from test or competition guide
- **SOURCE**: Tournament name, year, and division (usually "Div. C")
- **FORMAT**: Count all questions, group by format and point value
- **TOTAL POINTS**: Sum all individual question point values

---

## Question Format Structure

### Standard Question Block
```
---QUESTION [ID]---
ID: [Number] | POINTS: [X.XX] | FORMAT: [Type]
TOPIC: [Category] | [Subcategory] | [Specific topic]
DIFFICULTY: [Level]
QUESTION: [Full question text]
OPTIONS:
A) [Option text]
B) [Option text]
C) [Option text]
D) [Option text]
CORRECT_ANSWER: [Letter] (or description if not MC)
```

### Multi-Select Question (Mark ALL correct)
```
---QUESTION [ID]---
ID: [Number] | POINTS: [X.XX] | FORMAT: MC (multi-select)
TOPIC: [Topic tags]
DIFFICULTY: [Level]
QUESTION: [Full question text]
OPTIONS:
A) [Option]
B) [Option]
C) [Option]
D) [Option]
CORRECT_ANSWERS: [A, B, D] (comma-separated)
```

### Fill-in-the-Blank
```
---QUESTION [ID]---
ID: [Number] | POINTS: [X.XX] | FORMAT: Fill-in-blank
TOPIC: [Topics]
DIFFICULTY: [Level]
QUESTION: [Question with blanks described]
ANSWER: [Correct answer text]
```

### Free Response / Essay
```
---QUESTION [ID]---
ID: [Number] | POINTS: [X.XX] | FORMAT: Free Response
TOPIC: [Topics]
DIFFICULTY: [Level]
QUESTION: [Question text, include constraints if any]
ANSWER: [Concise correct answer or key points]
```

### Calculation / Problem-Solving
```
---QUESTION [ID]---
ID: [Number] | POINTS: [X.XX] | FORMAT: Calculation | [Sub-type]
TOPIC: [Physics/Math/Science category] | [Specific concept]
DIFFICULTY: [Level]
QUESTION: [Problem text with given values]
CALCULATION: [Relevant formulas and methodology]
```

### True/False
```
---QUESTION [ID]---
ID: [Number] | POINTS: [X.XX] | FORMAT: True/False
TOPIC: [Topic]
DIFFICULTY: [Level]
QUESTION: [Statement]
ANSWER: [TRUE or FALSE]
```

### Image Analysis/Identification
```
---QUESTION [ID]---
ID: [Number] | POINTS: [X.XX] | FORMAT: [Image analysis / Organism identification]
TOPIC: [Topic category]
DIFFICULTY: [Level]
QUESTION: [Description of image or identification task]
ANSWER: [Correct identification, if known]
```

### Matching
```
---QUESTIONS [ID-ID]---
ID: [Range] | POINTS: [X.XX] each | FORMAT: Matching / [Type]
TOPIC: [Topic]
DIFFICULTY: [Level]

MATCHING_ITEMS:
[Item 1] → [Answer A]
[Item 2] → [Answer B]
```

---

## Topic Tagging Rules

### Format
```
TOPIC: [Category] | [Subcategory] | [Specific concept]
```

### Requirements
- **Primary Category**: Broad discipline (e.g., Neuroscience, Orbital Mechanics, Chemistry)
- **Secondary Category**: Medium specificity (e.g., Synaptic plasticity, Circular orbits, Equilibrium)
- **Tertiary Category**: High specificity (e.g., NMDA receptors, Kepler's third law, Le Chatelier)
- Use **pipe (|)** separators
- Capitalize first letter of each major concept
- Use **specific terminology** from the test content
- Include **technical terms** students should recognize

### Examples
```
TOPIC: Neuroanatomy | Spinal cord | Motor pathways
TOPIC: Orbital Mechanics | Kepler's laws | Period-semimajor axis relation
TOPIC: Equilibrium | Complex ion formation | Le Chatelier's principle
TOPIC: Stellar Astrophysics | Variable stars | Pulsation mechanism
```

---

## Difficulty Levels

Use ONE of these levels:
- **Easy**: Basic recall, straightforward application
- **Medium**: Requires understanding, some synthesis
- **High**: Complex reasoning, multi-step thinking
- **Very High**: Integration of multiple concepts, advanced problem-solving

Assignment guidelines:
- Straightforward MC recall → Easy
- Requires conceptual understanding → Medium
- Multi-step calculations or synthesis → High
- Derivations, complex scenarios, edge cases → Very High

---

## Format Types

Standardized format designations:

**Multiple Choice:**
- `MC` - Single correct answer
- `MC (multi-select)` - Mark ALL correct answers
- `MC (multi-select - mark ALL)` - When explicitly stated in test

**Question Types:**
- `Fill-in-blank` - Single blank
- `Fill-in-blank (multiple blanks)` - Multiple blanks in one question
- `Fill-in-blank (N blanks - [description])` - N specific blanks with context
- `Free Response` - Essay/short answer
- `Free Response / [Subcategory]` - Free response with specific type
- `Calculation` - Math/physics problem
- `Calculation / [Type]` - Calculation with specific context
- `True/False` - Boolean answer
- `[Analysis Type]` - Image analysis, organism identification, diagram interpretation
- `Matching` or `Matching / [Type]` - Match items to answers
- `Derivation` - Show work proving equation or relationship

---

## Point Values

Record exact point values from test:
```
POINTS: [X.XX]
```

Examples: `POINTS: 1.00`, `POINTS: 3.00`, `POINTS: 2.50`, `POINTS: 5.00`, `POINTS: 0.01`

---

## Special Cases

### Questions with Diagrams
```
QUESTION: [Description referencing diagram] [diagram reference noted]
```
Note: Actual diagram images not included; referenced descriptively

### Abbreviated Questions (long options)
```
QUESTION: [Full question text]
OPTIONS:
A) [First option - abbreviated if very long]
B) [Second option]
... (etc)
CORRECT_ANSWER: [Letter]
```

### Questions with Multiple Parts
```
---QUESTION [ID]---
ID: [Number] | POINTS: [X.XX] | FORMAT: Free Response / [Type]
TOPIC: [Topics]
DIFFICULTY: [Level]
QUESTION: 
(a) [Part 1 question]
(b) [Part 2 question]
(c) [Part 3 question]
ANSWER: 
(a) [Part 1 answer]
(b) [Part 2 answer]
(c) [Part 3 answer]
```

### Range Questions (e.g., "Questions 1-10 refer to image X")
```
---QUESTIONS [ID-ID] (SHARED CONTEXT)---
ID: [Range] | POINTS: [X.XX] each | FORMAT: [Type]
TOPIC: [Shared topic]
CONTEXT: [Shared information/image description]

[Individual questions listed with simplified format]
```

### Section Headers
```
---SECTION [N]: [SECTION NAME]---
[Brief description of section content]
```
Use before groups of related questions.

---

## Quality Standards

### Completeness Checklist
- [ ] Every question from original test included
- [ ] Question numbering matches original test
- [ ] All point values accurate
- [ ] All options/answers present and complete
- [ ] Topic tags are specific and meaningful
- [ ] Difficulty appropriately assigned
- [ ] Format type correctly identified
- [ ] Correct answers verified against answer key (if available)

### Accuracy Requirements
- [ ] Question text matches original exactly
- [ ] No spelling/grammar corrections to original test wording
- [ ] Mathematical symbols preserved (subscripts, superscripts, Greek letters)
- [ ] Chemical formulas exact
- [ ] Proper terminology from test maintained

### Formatting Standards
- [ ] Consistent indentation (3 spaces for sub-items)
- [ ] Pipe separators (|) used in headers
- [ ] Dashes (---) for section breaks
- [ ] Blank lines between question blocks
- [ ] Header format consistent across all questions
- [ ] No trailing whitespace

---

## Handling Special Content

### Mathematical/Scientific Notation
Preserve exact notation:
- Subscripts/superscripts as superscript notation (e.g., `10⁻⁵`, `H₂O`, `CO₂`)
- Greek letters (α, β, γ, Δ, λ, μ, etc.)
- Special symbols (∞, ±, ≈, ≠, √, π)
- Chemical formulas (NO₃⁻, SO₄²⁻, Ca²⁺)

### Units
- Include units from original question
- Use standard abbreviations (m/s, kg, eV, J, etc.)
- Preserve fractional units (km/s, m²/s²)

### Equations and Formulas
Use markdown-style notation:
```
E = mc²
v = √(GM/r)
pH = -log[H⁺]
```

### Data Tables
Preserve table structure when relevant:
```
[Column 1] | [Column 2] | [Column 3]
-----------|-----------|----------
Value A    | Value B    | Value C
```

---

## Calculation Question Template

For quantitative problems, include:

```
---QUESTION [ID]---
ID: [Number] | POINTS: [X.XX] | FORMAT: Calculation | [Problem Type]
TOPIC: [Category] | [Subcategory] | [Concept]
DIFFICULTY: [Level]
QUESTION: [Full problem text with given values]
CALCULATION: [Formula(s) used] 
[Intermediate steps if helpful for understanding]
[Final answer format if not standard]
```

Example:
```
---QUESTION 52---
ID: 52 | POINTS: 3.00 | FORMAT: Calculation | Stefan-Boltzmann Law
TOPIC: Stellar Astrophysics | Luminosity | Radiation
DIFFICULTY: High
QUESTION: Star with R=0.1R☉ and λpeak=700nm. Temperature in Kelvin?
CALCULATION: Wien's displacement law: T = λmax * b / λpeak = (2.898 × 10⁻³ m·K) / (700 × 10⁻⁹ m) ≈ 4140 K
```

---

## File Validation Checklist

Before finalizing each test file:

- [ ] File saved with correct naming convention
- [ ] Header section complete and accurate
- [ ] Total question count matches
- [ ] All questions numbered sequentially
- [ ] Each question has all required metadata fields
- [ ] Topics are specific and informative
- [ ] Difficulty levels distributed reasonably
- [ ] No incomplete or malformed questions
- [ ] Special characters rendered correctly
- [ ] File encoding is UTF-8
- [ ] No trailing blank lines

---

## Examples by Event

### Example 1: Multiple Choice (Astronomy)
```
---QUESTION 1---
ID: 1 | POINTS: 3.00 | FORMAT: MC
TOPIC: Stellar Astrophysics | Energy production | Nuclear fusion
DIFFICULTY: High
QUESTION: Which process dominates energy production in massive star near main-sequence end?
OPTIONS:
A) Proton-proton chain
B) CNO cycle
C) Triple-alpha process
D) Neutron capture
CORRECT_ANSWER: B
```

### Example 2: Free Response (Anatomy)
```
---QUESTION 55---
ID: 55 | POINTS: 5.00 | FORMAT: Free Response
TOPIC: Neuroscience | Synaptic integration | Synaptic plasticity | NMDA receptors
DIFFICULTY: Very High
QUESTION: Explain how temporal vs spatial summation determines action-potential initiation at axon initial segment. Include dendritic cable properties, inhibitory shunting (GABA_A), and NMDA receptor coincidence detection in Hebbian LTP.
```

### Example 3: Calculation (Physics)
```
---QUESTION 45---
ID: 45 | POINTS: 3.00 | FORMAT: Calculation | Mass transfer
TOPIC: Binary systems | Mass accretion | Orbital evolution | Transfer rate
DIFFICULTY: Very High
QUESTION: Assume supernova in 10 billion years; more massive component is 0.8M☉ and gaining mass from smaller component. What is mass transfer rate in kg/s?
CALCULATION: ΔM/Δt = [total mass change] / [time period]
```

---

## Notes for Future Parsing

1. **Consistency**: Maintain format across all events
2. **Ambiguity**: When question text is ambiguous, preserve ambiguity from original
3. **Incomplete Information**: If answer key unavailable, mark as `[Answer not provided]`
4. **Images**: Describe image content; actual images not stored
5. **Updates**: If test is updated, create new version with date suffix
6. **Versioning**: Consider adding VERSION field to header if test modifications needed

---

## Todo Template for Parsing Session

Create a structured task list when starting to parse a new tournament:

```
[ ] Tournament Setup
  [ ] Collect all PDFs for tournament
  [ ] Create /TestsTXT/ subdirectory
  [ ] Create /TestsParsed/ subdirectory
  [ ] Copy PARSING_RULES.md to project root

[ ] Event 1: [Event Name]
  [ ] PDF → TXT conversion
  [ ] Read TXT file completely
  [ ] Identify all questions
  [ ] Write parsed file
  [ ] Validate completeness

[ ] Event 2: [Event Name]
  [ ] PDF → TXT conversion
  [ ] Read TXT file completely
  [ ] Identify all questions
  [ ] Write parsed file
  [ ] Validate completeness

... (repeat for each event)

[ ] Final Review
  [ ] All events completed
  [ ] File naming consistent
  [ ] Header sections accurate
  [ ] All questions formatted consistently
  [ ] Total points calculations verified
```

---

## Maintenance

### Adding Questions
- Use template matching existing format
- Maintain sequential ID numbering
- Update TOTAL POINTS in header
- Update FORMAT summary in header

### Correcting Errors
- Preserve original test wording
- Note corrections in version comment if applicable
- Verify difficulty after any changes

### Re-parsing a Test
- Keep original TXT file for reference
- Create new parsed file with version suffix if needed
- Document changes made
- Verify all questions still present

---

## Common Pitfalls to Avoid

1. **Using automation**: Scripts introduce errors; manual review is essential
2. **Skipping the TXT step**: Always convert PDF to TXT first for accuracy
3. **Inconsistent formatting**: Follow templates exactly for all questions
4. **Vague topics**: Be specific—3-level hierarchy required
5. **Difficulty guessing**: Assess based on content, not position
6. **Missing metadata**: Every question needs ID, POINTS, FORMAT, TOPIC, DIFFICULTY
7. **Point calculation errors**: Verify TOTAL POINTS by adding all individual question values
8. **Incomplete answer options**: Ensure all options A-D (or more) included

---

## Quality Checklist Before Finalizing

Before saving a parsed file, verify:

- [ ] File created in `/TestsParsed/` with correct naming
- [ ] Header section complete and accurate
- [ ] Question count matches original test
- [ ] All questions numbered sequentially (no gaps)
- [ ] Every question has all 6 required metadata fields
- [ ] Topics are specific and technical
- [ ] Difficulty levels assigned thoughtfully
- [ ] Answer key correct (verify against original if possible)
- [ ] No incomplete or truncated questions
- [ ] Special characters render properly (Greek letters, subscripts, etc.)
- [ ] Consistent formatting throughout
- [ ] TOTAL POINTS calculation verified

---

**Last Updated**: January 2026
**Status**: Methodology documented for future parsing
**Total Tests Parsed (Reference)**: 11 events, 617 questions (MVSO Invite 2025)
