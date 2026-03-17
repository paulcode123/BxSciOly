"""
Analyze who gets top scores in Dynamic Planet, Remote Sensing, and Water Quality
from Yale Invitational 2025-26 and NYC North Regional 2025-26.
"""

# Yale Invitational 2025-26 rosters and results
yale_rosters = {
    "A": {
        "Dynamic Planet": ["Johnny Lin (11th)", "Simeon Chen"],
        "Remote Sensing": ["Itamar Goshen", "Ryan Chen"],
        "Water Quality": ["Noelle Delosreyes", "Cielle Voulgarides"],
    },
    "B": {
        "Dynamic Planet": ["Brandon Lin", "Johnny Lin (10th)"],
        "Remote Sensing": ["Xin Yue Wen", "Vincent Zhao"],
        "Water Quality": ["Xin Yue Wen", "Ethan Wang"],
    }
}

yale_results = {
    "A": {
        "Dynamic Planet": 6,
        "Remote Sensing": 11,
        "Water Quality": 4,
    },
    "B": {
        "Dynamic Planet": 11,
        "Remote Sensing": 20,
        "Water Quality": 9,
    }
}

# NYC North Regional 2025-26 rosters and results
regionals_rosters = {
    "A": {
        "Dynamic Planet": ["Jodi Zheng", "Brandon Lin"],
        "Remote Sensing": ["Yutong Chen", "Itamar Goshen"],
        "Water Quality": ["Yutong Chen", "Noelle Delosreyes"],
    },
    "B": {
        "Dynamic Planet": ["Johnny Lin", "Simeon Chen"],
        "Remote Sensing": ["Linwang Li", "Lyla Quim"],
        "Water Quality": ["Anna Gao", "Xin Yue Wen"],
    }
}

regionals_results = {
    "A": {
        "Dynamic Planet": 3,
        "Remote Sensing": 3,
        "Water Quality": 4,
    },
    "B": {
        "Dynamic Planet": 2,
        "Remote Sensing": 4,
        "Water Quality": 13,
    }
}

def normalize_name(name):
    """Normalize competitor name (remove grade/year indicators)"""
    import re
    name = re.sub(r'\s*\(\d+th\)', '', name)
    return name.strip()

# Analyze each event
events_to_analyze = ["Dynamic Planet", "Remote Sensing", "Water Quality"]

print("=" * 100)
print("TOP PERFORMERS IN DYNAMIC PLANET, REMOTE SENSING, AND WATER QUALITY")
print("From Yale Invitational 2025-26 and NYC North Regional 2025-26")
print("=" * 100)
print()

for event in events_to_analyze:
    print(f"\n{'='*100}")
    print(f"{event.upper()}")
    print(f"{'='*100}")
    
    print(f"{'Competitor':<30} | {'Yale':<15} | {'Regionals':<15} | {'Avg':<10} | {'Best':<10}")
    print("-" * 100)
    
    competitor_data = {}
    
    # Process Yale
    for team in ["A", "B"]:
        if event in yale_rosters[team]:
            placement = yale_results[team].get(event)
            if placement:
                for participant in yale_rosters[team][event]:
                    name = normalize_name(participant)
                    if name not in competitor_data:
                        competitor_data[name] = {"yale": None, "regionals": None}
                    competitor_data[name]["yale"] = placement    
    # Process Regionals
    for team in ["A", "B"]:
        if event in regionals_rosters[team]:
            placement = regionals_results[team].get(event)
            if placement:
                for participant in regionals_rosters[team][event]:
                    name = normalize_name(participant)
                    if name not in competitor_data:
                        competitor_data[name] = {"yale": None, "regionals": None}
                    competitor_data[name]["regionals"] = placement    
    # Calculate averages and sort
    ranked = []
    for name, data in competitor_data.items():
        placements = [p for p in [data["yale"], data["regionals"]] if p is not None]
        if placements:
            avg = sum(placements) / len(placements)
            best = min(placements)
            yale_str = str(data["yale"]) if data["yale"] else "-"
            regionals_str = str(data["regionals"]) if data["regionals"] else "-"
            ranked.append({
                "name": name,
                "yale": yale_str,
                "regionals": regionals_str,
                "avg": avg,
                "best": best,
                "placements": placements
            })
    # Sort by best placement, then average
    ranked.sort(key=lambda x: (x["best"], x["avg"]))
    # Print results
    for comp in ranked:
        print(f"{comp['name']:<30} | {comp['yale']:<15} | {comp['regionals']:<15} | "
              f"{comp['avg']:<10.2f} | {comp['best']:<10}")

print()
print("=" * 100)
