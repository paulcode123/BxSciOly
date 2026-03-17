"""
Analyze event strength based on placements from Yale Invitational 2025-26 
and NYC North Regional 2025-26 for Teams A and B.
"""

# Yale Invitational 2025-26 placements
yale_team_a = {
    "Anatomy and Physiology": 2,
    "Astronomy": 3,
    "Boomilever": 15,
    "Bungee Drop": 15,
    "Chemistry Lab": 2,
    "Circuit Lab": 17,
    "Codebusters": 4,
    "Designer Genes": 4,
    "Disease Detectives": 2,
    "Dynamic Planet": 6,
    "Electric Vehicle": 6,
    "Engineering CAD": 20,
    "Entomology": 16,
    "Experimental Design": 5,
    "Forensics": 3,
    "Helicopter": 9,
    "Hovercraft": 12,
    "Machines": 15,
    "Materials Science": 20,
    "Remote Sensing": 11,
    "Robot Tour": 8,
    "Rocks and Minerals": 4,
    "Water Quality": 4,
}

yale_team_b = {
    "Anatomy and Physiology": 1,
    "Astronomy": 8,
    "Boomilever": 10,
    "Bungee Drop": 20,
    "Chemistry Lab": 19,
    "Circuit Lab": 16,
    "Codebusters": 13,
    "Designer Genes": 9,
    "Disease Detectives": 6,
    "Dynamic Planet": 11,
    "Electric Vehicle": 3,
    "Engineering CAD": 23,
    "Entomology": 5,
    "Experimental Design": 14,
    "Forensics": 2,
    "Helicopter": 4,
    "Hovercraft": 14,
    "Machines": 34,
    "Materials Science": 4,
    "Remote Sensing": 20,
    "Robot Tour": 19,
    "Rocks and Minerals": 12,
    "Water Quality": 9,
}

# NYC North Regional 2025-26 placements
regionals_team_a = {
    "Anatomy and Physiology": 2,
    "Astronomy": 5,
    "Boomilever": 2,
    "Bungee Drop": 4,
    "Chemistry Lab": 6,
    "Circuit Lab": 8,
    "Codebusters": 1,
    "Designer Genes": 1,
    "Disease Detectives": 3,
    "Dynamic Planet": 3,
    "Electric Vehicle": 11,
    "Entomology": 12,
    "Experimental Design": 3,
    "Forensics": 8,
    "Helicopter": 6,
    "Hovercraft": 5,
    "Machines": 5,
    "Materials Science": 5,
    "Remote Sensing": 3,
    "Robot Tour": 4,
    "Rocks and Minerals": 3,
    "Water Quality": 4,
    "Write It Do It": 3,
}

regionals_team_b = {
    "Anatomy and Physiology": 1,
    "Astronomy": 8,
    "Boomilever": 3,
    "Bungee Drop": 8,
    "Chemistry Lab": 2,
    "Circuit Lab": 6,
    "Codebusters": 4,
    "Designer Genes": 2,
    "Disease Detectives": 4,
    "Dynamic Planet": 2,
    "Electric Vehicle": 8,
    "Entomology": 2,
    "Experimental Design": 2,
    "Forensics": 2,
    "Helicopter": 1,
    "Hovercraft": 3,
    "Machines": 4,
    "Materials Science": 2,
    "Remote Sensing": 4,
    "Robot Tour": 10,
    "Rocks and Minerals": 4,
    "Water Quality": 13,
    "Write It Do It": 12,
}

# Get all unique events
all_events = set(yale_team_a.keys()) | set(yale_team_b.keys()) | set(regionals_team_a.keys()) | set(regionals_team_b.keys())

# Calculate average placements for each event
event_averages = {}

for event in all_events:
    placements = []
    
    # Add placements from each competition/team combination
    if event in yale_team_a:
        placements.append(yale_team_a[event])
    if event in yale_team_b:
        placements.append(yale_team_b[event])
    if event in regionals_team_a:
        placements.append(regionals_team_a[event])
    if event in regionals_team_b:
        placements.append(regionals_team_b[event])
    
    if placements:
        avg_placement = sum(placements) / len(placements)
        event_averages[event] = {
            "average": avg_placement,
            "placements": placements,
            "count": len(placements)
        }

# Sort events by average placement (lower is better/stronger)
sorted_events = sorted(event_averages.items(), key=lambda x: x[1]["average"])

# Print results
print("=" * 80)
print("EVENT STRENGTH RANKING (Strongest to Weakest)")
print("Based on average placements from Yale Invitational 2025-26 and NYC North Regional 2025-26")
print("(Teams A & B combined)")
print("=" * 80)
print()

for rank, (event, data) in enumerate(sorted_events, 1):
    placements_str = ", ".join(map(str, data["placements"]))
    print(f"{rank:2d}. {event:30s} | Avg: {data['average']:5.2f} | Placements: {placements_str}")

print()
print("=" * 80)
print("Summary Statistics:")
print(f"Total events analyzed: {len(sorted_events)}")
print(f"Strongest event: {sorted_events[0][0]} (avg: {sorted_events[0][1]['average']:.2f})")
print(f"Weakest event: {sorted_events[-1][0]} (avg: {sorted_events[-1][1]['average']:.2f})")
print("=" * 80)
