import csv
from collections import Counter

# Read the CSV file
data = []
with open('member_names_ids_20250923_165639.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = list(reader)

# Extract bxscioly numbers
bxscioly_numbers = [row['bxscioly_number'] for row in data]

# Count occurrences
counts = Counter(bxscioly_numbers)

# Find duplicates
duplicates = {k: v for k, v in counts.items() if v > 1}

print(f"Total members: {len(data)}")
print(f"Unique bxscioly numbers: {len(counts)}")
print(f"Duplicates found: {len(duplicates)}")

if duplicates:
    print("\nDuplicate bxscioly numbers:")
    for num, count in duplicates.items():
        print(f"  {num}: {count} members")
        
        # Show which members have this duplicate ID
        members_with_duplicate = [row for row in data if row['bxscioly_number'] == num]
        for member in members_with_duplicate:
            print(f"    - {member['firstName']} {member['lastName']} (ID: {member['id']})")
else:
    print("\n✅ No duplicate bxscioly numbers found!")
    print("All members have unique bxscioly identifiers.")












