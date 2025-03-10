import json
import importlib

# Force reload of main module to ensure the latest version is used
import main
importlib.reload(main)

from main import DLSCalculator  # Ensure correct import

# Load DLS data
with open("dls_data.json", "r") as file:
    dls_data = json.load(file)

calculator = DLSCalculator(dls_data)

# Test cases
test_cases = [
    (200, 50, 40.0, 3, dls_data["dls_table_50"], 122),
    (150, 30, 25.0, 2, dls_data["dls_table_50"], 96),
    (300, 50, 50.0, 5, dls_data["dls_table_50"], 280),
]

print("\n🚀 Running DLS Debug Test...\n")

for team1_score, team1_overs, team2_overs, team2_wickets, dls_table, expected in test_cases:
    calculated = calculator.calculate_dls_target(team1_score, team1_overs, team2_overs, team2_wickets, dls_table)

    print(f"🔹 Test Case: Team 1 Score = {team1_score}, Overs = {team1_overs}, "
          f"Target for {team2_overs} overs, Wickets Lost = {team2_wickets}")
    print(f"   ➡️ Expected: {expected}")
    print(f"   ✅ Calculated: {calculated}")

    difference = abs(expected - calculated)
    print(f"   ⚖️ Difference: {difference}\n")

print("✅ Debug test completed.")
