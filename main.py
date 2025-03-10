import json
import math

# Load DLS data from JSON file
with open("dls_data.json", "r") as file:
    dls_data = json.load(file)

def interpolate_resources(dls_table, overs, wickets_lost):
    """Interpolate resource percentage if exact overs value is not found in DLS table."""
    overs = int(overs)
    if str(overs) in dls_table:
        return dls_table[str(overs)].get(str(wickets_lost), 0.0)
    
    valid_overs = sorted(int(k) for k in dls_table.keys())
    lower_overs = max((o for o in valid_overs if o <= overs), default=None)
    higher_overs = min((o for o in valid_overs if o >= overs), default=None)
    
    if lower_overs is None or higher_overs is None or lower_overs == higher_overs:
        return dls_table.get(str(lower_overs), {}).get(str(wickets_lost), 0.0)
    
    lower_value = dls_table[str(lower_overs)].get(str(wickets_lost), 0.0)
    higher_value = dls_table[str(higher_overs)].get(str(wickets_lost), 0.0)
    
    return round(lower_value + (higher_value - lower_value) * ((overs - lower_overs) / (higher_overs - lower_overs)), 1)

def calculate_dls_target(team1_score, team1_overs, team2_overs, team2_wickets, dls_table):
    """Calculate the revised target for Team 2 using DLS method."""
    if team1_score == 0:
        return 0
    
    team1_resources = interpolate_resources(dls_table, team1_overs, 0)
    team2_resources = interpolate_resources(dls_table, team2_overs, team2_wickets)

    if team1_resources == 0:
        return team1_score
    
    target = round(team1_score * (team2_resources / team1_resources))
    return max(1, target)

def calculate_par_score(revised_target, current_overs, total_overs, wickets_lost, dls_table):
    """Calculate the correct par score at the current stage."""
    if current_overs == 0:
        return 0
    
    initial_resources = interpolate_resources(dls_table, total_overs, 0)
    current_resources = interpolate_resources(dls_table, current_overs, wickets_lost)

    if initial_resources == 0:
        return 0
    
    resources_used = initial_resources - current_resources
    return round(revised_target * (resources_used / initial_resources))

def get_input(prompt, input_type, min_value=None, max_value=None):
    """Get valid input from the user."""
    while True:
        try:
            value = input_type(input(prompt))
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}. Try again.")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}. Try again.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main():
    print("Duckworth-Lewis-Stern (DLS) Calculator")
    print("--------------------------------------")

    print("Select match format:")
    print("1. 50-over match (300 balls)")
    print("2. 20-over match (120 balls)")
    print("3. 100-ball match (100 balls)")
    match_format = get_input("Enter choice (1/2/3): ", int, min_value=1, max_value=3)

    if match_format == 1:
        dls_table = dls_data["dls_table_50"]
        max_overs = 50
    elif match_format == 2:
        dls_table = dls_data["dls_table_20"]
        max_overs = 20
    elif match_format == 3:
        dls_table = dls_data["dls_table_100"]
        max_overs = 20

    team1_score = get_input("Enter Team 1's score: ", int, min_value=0)
    
    if match_format in [1, 2]:
        team1_overs = get_input(f"Enter Team 1's total overs (max {max_overs}): ", float, min_value=0, max_value=max_overs)
        team2_overs = get_input(f"Enter Team 2's total overs (reduced innings, max {max_overs}): ", float, min_value=0, max_value=max_overs)
        team2_current_overs = get_input(f"Enter Team 2's current overs (max {team2_overs}): ", float, min_value=0, max_value=team2_overs)
    else:
        team1_overs = get_input("Enter Team 1's total balls (max 100): ", int, min_value=0, max_value=100) / 5
        team2_overs = get_input("Enter Team 2's total balls (reduced innings, max 100): ", int, min_value=0, max_value=100) / 5
        team2_current_overs = get_input("Enter Team 2's current balls faced: ", int, min_value=0, max_value=team2_overs * 5) / 5
    
    team2_current_score = get_input("Enter Team 2's current score: ", int, min_value=0)
    team2_current_wickets = get_input("Enter Team 2's current wickets lost: ", int, min_value=0, max_value=10)
    
    revised_target = calculate_dls_target(team1_score, team1_overs, team2_overs, team2_current_wickets, dls_table)
    par_score = calculate_par_score(revised_target, team2_current_overs, team2_overs, team2_current_wickets, dls_table)
    difference = team2_current_score - par_score
    runs_needed = max(0, revised_target - team2_current_score)
    balls_remaining = (team2_overs * 5) - (team2_current_overs * 5)
    required_run_rate = runs_needed / (balls_remaining / 6) if balls_remaining > 0 else 0
    
    print("\nResults:")
    print(f"Revised Target: {revised_target} | Par Score: {par_score} | Runs Needed: {runs_needed} | Balls Remaining: {balls_remaining} | Required Run Rate: {required_run_rate:.2f}")
    
    if difference < 0:
        print(f"Team 2 is BEHIND the par score by {-difference} runs.")
    elif difference > 0:
        print(f"Team 2 is AHEAD of the par score by {difference} runs.")
    else:
        print("Team 2 is ON PAR with the required score.")

if __name__ == "__main__":
    main()