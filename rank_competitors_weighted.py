"""
Rank competitors based on their event placements in Yale Invitational 2025-26 
and NYC North Regional 2025-26, with emphasis on top placements.
"""

from collections import defaultdict

# Yale Invitational 2025-26 rosters and results
yale_rosters = {
    "A": {
        "Anatomy and Physiology": ["Noelle Delosreyes", "Sophia Zheng"],
        "Astronomy": ["Johnny Lin (11th)", "Itamar Goshen"],
        "Boomilever": ["Atef Istiaque", "Cielle Voulgarides"],
        "Bungee Drop": ["Aidan Wong", "Atef Istiaque"],
        "Chemistry Lab": ["Queenie Tang", "Stanley Zhao"],
        "Circuit Lab": ["Paul Nieuwerburgh", "Lia Skarabot"],
        "Codebusters": ["Queenie Tang", "Andrew Lin", "Simeon Chen"],
        "Designer Genes": ["Stanley Zhao", "Noelle Delosreyes"],
        "Disease Detectives": ["Noelle Delosreyes", "Stanley Zhao"],
        "Dynamic Planet": ["Johnny Lin (11th)", "Simeon Chen"],
        "Electric Vehicle": ["Andrew Lin", "Lia Skarabot"],
        "Entomology": ["Anushka Biswas", "Cielle Voulgarides"],
        "Engineering CAD": ["Paul Nieuwerburgh", "Aidan Wong"],
        "Experimental Design": ["Simeon Chen", "Stanley Zhao", "Ryan Chen"],
        "Forensics": ["Queenie Tang", "Andrew Lin"],
        "Helicopter": ["Aidan Wong", "Atef Istiaque"],
        "Hovercraft": ["Aidan Wong", "Atef Istiaque"],
        "Machines": ["Aidan Wong", "Paul Nieuwerburgh"],
        "Material Science": ["Paul Nieuwerburgh", "Lia Skarabot"],
        "Remote Sensing": ["Itamar Goshen", "Ryan Chen"],
        "Robot Tour": ["Andrew Lin", "Lia Skarabot"],
        "Rocks and Minerals": ["Anushka Biswas", "Itamar Goshen"],
        "Water Quality": ["Noelle Delosreyes", "Cielle Voulgarides"],
    },
    "B": {
        "Anatomy and Physiology": ["Ileene Ng", "Vincent Zhao"],
        "Astronomy": ["Brandon Lin", "Vincent Zhao"],
        "Boomilever": ["Senna Shiau", "Chase Li"],
        "Bungee Drop": ["Wilson Shao", "Chase Li"],
        "Chemistry Lab": ["Wilson Shao", "Vincent Zhao"],
        "Circuit Lab": ["Rishav Banik", "Haylie Leong"],
        "Codebusters": ["Elyn Wang", "Jacob Berner", "Sherman Wong"],
        "Designer Genes": ["Ileene Ng", "Xingtong Chen"],
        "Disease Detectives": ["Ileene Ng", "Xingtong Chen"],
        "Dynamic Planet": ["Brandon Lin", "Johnny Lin (10th)"],
        "Electric Vehicle": ["Wilson Shao", "Rishav Banik"],
        "Entomology": ["Johnny Lin (10th)", "Elyn Wang"],
        "Engineering CAD": ["Ethan Wang", "Wilson Shao"],
        "Experimental Design": ["Sherman Wong", "Xingtong Chen", "Ethan Wang"],
        "Forensics": ["Elyn Wang", "Xin Yue Wen"],
        "Helicopter": ["Haylie Leong", "Senna Shiau"],
        "Hovercraft": ["Haylie Leong", "Chase Li"],
        "Machines": ["Senna Shiau", "Jacob Berner"],
        "Material Science": ["Adeline Nurenie", "Owen Zhang"],
        "Remote Sensing": ["Xin Yue Wen", "Vincent Zhao"],
        "Robot Tour": ["Rishav Banik", "Jacob Berner"],
        "Rocks and Minerals": ["Johnny Lin (10th)", "Chase Li"],
        "Water Quality": ["Xin Yue Wen", "Ethan Wang"],
    }
}

yale_results = {
    "A": {
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
    },
    "B": {
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
}

# NYC North Regional 2025-26 rosters and results
regionals_rosters = {
    "A": {
        "Anatomy and Physiology": ["Ileene Ng", "Noelle Delosreyes"],
        "Astronomy": ["Itamar Goshen", "Paul Nieuwerburgh"],
        "Boomilever": ["Jonathan Yip", "Aidan Wong"],
        "Bungee Drop": ["Jin Zhao", "Edison Lee"],
        "Chemistry Lab": ["Queenie Tang", "Morgan Greenfield"],
        "Circuit Lab": ["Paul Nieuwerburgh", "Aaron Krasinski"],
        "Codebusters": ["Queenie Tang", "Edison Lee", "Morgan Greenfield"],
        "Designer Genes": ["Ileene Ng", "Noelle Delosreyes"],
        "Disease Detectives": ["Ileene Ng", "Noelle Delosreyes"],
        "Dynamic Planet": ["Jodi Zheng", "Brandon Lin"],
        "Electric Vehicle": ["Aidan Wong", "Paul Nieuwerburgh"],
        "Entomology": ["Anushka Biswas", "Jodi Zheng"],
        "Experimental Design": ["Jonathan Yip", "Morgan Greenfield", "Brandon Lin"],
        "Forensics": ["Queenie Tang", "Morgan Greenfield"],
        "Helicopter": ["Jin Zhao", "Jonathan Yip"],
        "Hovercraft": ["Jin Zhao", "Edison Lee"],
        "Machines": ["Jonathan Yip", "Aaron Krasinski"],
        "Material Science": ["Brandon Lin", "Aaron Krasinski"],
        "Remote Sensing": ["Yutong Chen", "Itamar Goshen"],
        "Robot Tour": ["Aidan Wong", "Edison Lee"],
        "Rocks and Minerals": ["Anushka Biswas", "Jodi Zheng"],
        "Water Quality": ["Yutong Chen", "Noelle Delosreyes"],
        "Write It Do It": ["Brandon Lin", "Jin Zhao"],
    },
    "B": {
        "Anatomy and Physiology": ["Linwang Li", "Sophia Zheng"],
        "Astronomy": ["Johnny Lin", "Kael Barba"],
        "Boomilever": ["Senna Shiau", "Jerry Zhu"],
        "Bungee Drop": ["Jerry Zhu", "Atef Istiaque"],
        "Chemistry Lab": ["Andrew Lin", "Lyla Quim"],
        "Circuit Lab": ["Linwang Li", "Atef Istiaque"],
        "Codebusters": ["Simeon Chen", "Andrew Lin", "Elyn Wang"],
        "Designer Genes": ["Johnny Lin", "Xin Yue Wen"],
        "Disease Detectives": ["Sherman Wong", "Sophia Zheng"],
        "Dynamic Planet": ["Johnny Lin", "Simeon Chen"],
        "Electric Vehicle": ["Andrew Lin", "Jerry Zhu"],
        "Entomology": ["Johnny Lin", "Elyn Wang"],
        "Experimental Design": ["Simeon Chen", "Anna Gao", "Sherman Wong"],
        "Forensics": ["Simeon Chen", "Xin Yue Wen"],
        "Helicopter": ["Senna Shiau", "Jerry Zhu"],
        "Hovercraft": ["Atef Istiaque", "Senna Shiau"],
        "Machines": ["Linwang Li", "Senna Shiau"],
        "Material Science": ["Kael Barba", "Anna Gao"],
        "Remote Sensing": ["Linwang Li", "Lyla Quim"],
        "Robot Tour": ["Andrew Lin", "Linwang Li"],
        "Rocks and Minerals": ["Lyla Quim", "Johnny Lin"],
        "Water Quality": ["Anna Gao", "Xin Yue Wen"],
        "Write It Do It": ["Jerry Zhu", "Sienna Shiau"],
    }
}

regionals_results = {
    "A": {
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
    },
    "B": {
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
}

def normalize_name(name):
    """Normalize competitor name (remove grade/year indicators)"""
    import re
    name = re.sub(r'\s*\(\d+th\)', '', name)
    return name.strip()

def calculate_weighted_score(placements):
    """
    Calculate weighted score that benefits top placements.
    Uses inverse scoring: 1st = 100 points, 2nd = 50, 3rd = 33.3, etc.
    Then averages and adds bonus for number of top placements.
    """
    if not placements:
        return 0
    
    # Inverse scoring: better placements get exponentially more points
    # Formula: points = 100 / placement
    points = [100.0 / p for p in placements]
    base_score = sum(points) / len(placements)
    
    # Bonus for top placements: count of top 3 finishes
    top_3_count = sum(1 for p in placements if p <= 3)
    top_5_count = sum(1 for p in placements if p <= 5)
    
    # Weighted bonus: top 3 placements worth more
    bonus = (top_3_count * 10) + (top_5_count * 2)
    
    return base_score + bonus

def get_competitor_placements():
    """Build a dictionary of competitor -> list of placements"""
    competitor_details = defaultdict(lambda: {"placements": [], "events": [], "competitions": []})
    
    # Process Yale
    for team in ["A", "B"]:
        for event, participants in yale_rosters[team].items():
            placement = yale_results[team].get(event)
            if placement:
                for participant in participants:
                    name = normalize_name(participant)
                    competitor_details[name]["placements"].append(placement)
                    competitor_details[name]["events"].append(f"{event} (Yale)")
                    competitor_details[name]["competitions"].append("Yale")
    
    # Process Regionals
    for team in ["A", "B"]:
        for event, participants in regionals_rosters[team].items():
            placement = regionals_results[team].get(event)
            if placement:
                for participant in participants:
                    name = normalize_name(participant)
                    competitor_details[name]["placements"].append(placement)
                    competitor_details[name]["events"].append(f"{event} (Regionals)")
                    competitor_details[name]["competitions"].append("Regionals")
    
    return competitor_details

# Get all competitor data
competitor_data = get_competitor_placements()

# Calculate scores and prepare for ranking
ranked_competitors = []
for name, data in competitor_data.items():
    if data["placements"]:
        weighted_score = calculate_weighted_score(data["placements"])
        avg_placement = sum(data["placements"]) / len(data["placements"])
        num_events = len(data["placements"])
        num_competitions = len(set(data["competitions"]))
        top_3_count = sum(1 for p in data["placements"] if p <= 3)
        top_5_count = sum(1 for p in data["placements"] if p <= 5)
        
        ranked_competitors.append({
            "name": name,
            "weighted_score": weighted_score,
            "avg_placement": avg_placement,
            "num_events": num_events,
            "num_competitions": num_competitions,
            "top_3_count": top_3_count,
            "top_5_count": top_5_count,
            "placements": data["placements"],
            "events": data["events"]
        })

# Sort by weighted score (higher is better), then by number of events
ranked_competitors.sort(key=lambda x: (-x["weighted_score"], -x["num_events"]))

# Print top 20
print("=" * 110)
print("TOP 20 STRONGEST COMPETITORS (Weighted for Top Placements)")
print("Based on weighted scoring that emphasizes top placements in Yale Invitational 2025-26 and NYC North Regional 2025-26")
print("=" * 110)
print()

for rank, comp in enumerate(ranked_competitors[:20], 1):
    placements_str = ", ".join(map(str, sorted(comp["placements"])))
    print(f"{rank:2d}. {comp['name']:25s} | Score: {comp['weighted_score']:6.1f} | "
          f"Avg: {comp['avg_placement']:4.2f} | Events: {comp['num_events']:2d} | "
          f"Top 3: {comp['top_3_count']:2d} | Top 5: {comp['top_5_count']:2d} | "
          f"Placements: {placements_str}")

print()
print("=" * 110)
print(f"Total competitors analyzed: {len(ranked_competitors)}")
print("Scoring: Base score = average of (100/placement), Bonus = (Top 3 count × 10) + (Top 5 count × 2)")
print("=" * 110)
