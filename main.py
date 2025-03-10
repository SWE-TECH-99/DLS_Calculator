import json
import logging
from typing import Dict

# Configure logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DLSCalculator:
    def __init__(self, dls_data: Dict[str, Dict[str, Dict[str, float]]]):
        """Initialize the calculator with DLS tables."""
        self.dls_data = dls_data

    def interpolate_resources(self, dls_table: Dict[str, Dict[str, float]], overs: float, wickets_lost: int) -> float:
        """High-precision interpolation for resource percentage based on overs and wickets lost."""
        try:
            overs_int = int(overs)
            remaining_balls = int((overs - overs_int) * 6)

            # 🚀 **Step 1: Exact match if available**
            if str(overs_int) in dls_table:
                full_over_resource = dls_table[str(overs_int)].get(str(wickets_lost), 0.0)

                if remaining_balls == 0:
                    return full_over_resource  # No interpolation needed

                # Check next-over resource
                next_over = str(overs_int + 1)
                if next_over in dls_table:
                    next_over_resource = dls_table[next_over].get(str(wickets_lost), 0.0)

                    # **Fix: Use weighted ball-by-ball interpolation**
                    interpolated_value = full_over_resource + ((next_over_resource - full_over_resource) * (remaining_balls / 6))
                    return round(interpolated_value, 2)

                return full_over_resource  # No next-over data

            # 🚀 **Step 2: Handle missing overs (Fallback)**
            available_overs = sorted(int(k) for k in dls_table.keys())
            lower_overs = max((o for o in available_overs if o <= overs), default=None)
            higher_overs = min((o for o in available_overs if o >= overs), default=None)

            if lower_overs is None or higher_overs is None:
                return dls_table.get(str(lower_overs), {}).get(str(wickets_lost), 0.0)

            # Get the closest available values
            lower_value = dls_table[str(lower_overs)].get(str(wickets_lost), 0.0)
            higher_value = dls_table[str(higher_overs)].get(str(wickets_lost), 0.0)

            # ✅ **Fix: Wicket penalty model (ICC-based)**
            # - Wickets should **not** reduce resources linearly
            # - ICC Model suggests **gradual drop-off per wicket**
            wicket_penalty = max(0.65, 1 - (wickets_lost ** 1.1 * 0.015))
            lower_value *= wicket_penalty
            higher_value *= wicket_penalty

            # **Final accurate interpolation**
            interpolated_value = lower_value + ((higher_value - lower_value) * ((overs - lower_overs) / (higher_overs - lower_overs)))
            return round(interpolated_value, 2)

        except Exception as e:
            logging.error(f"Error in interpolate_resources: {e}")
            return 0.0



    def calculate_dls_target(self, team1_score: int, team1_overs: float, team2_overs: float, team2_wickets: int, dls_table: Dict[str, Dict[str, float]]) -> int:
        """Calculate the revised target for Team 2 using the DLS method."""
        try:
            if team1_score == 0:
                return 0

            team1_resources = self.interpolate_resources(dls_table, team1_overs, 0)
            team2_resources = self.interpolate_resources(dls_table, team2_overs, team2_wickets)

            logging.info(f"📊 Team 1 Resources: {team1_resources}, Team 2 Resources: {team2_resources}")

            if team1_resources == 0:
                return team1_score  # If no resources available, return same score

            target = round(team1_score * (team2_resources / team1_resources))

            logging.info(f"🎯 Calculated Target: {target}")

            return max(1, target)
        except Exception as e:
            logging.error(f"Error in calculate_dls_target: {e}")
            return team1_score

    def calculate_par_score(self, revised_target: int, current_overs: float, total_overs: float, wickets_lost: int, dls_table: Dict[str, Dict[str, float]]) -> int:
        """Calculate the correct par score at the current stage."""
        try:
            if current_overs == 0:
                return 0

            initial_resources = self.interpolate_resources(dls_table, total_overs, 0)
            current_resources = self.interpolate_resources(dls_table, current_overs, wickets_lost)

            if initial_resources == 0:
                return 0  # Avoid division by zero

            resources_used = initial_resources - current_resources

            if resources_used <= 0:
                return 0  # Ensure par score is never negative

            par_score = round(revised_target * (resources_used / initial_resources))

            logging.info(f"📊 Par Score Calculation -> Revised Target: {revised_target}, "
                         f"Resources Used: {resources_used}, Initial Resources: {initial_resources}, Par Score: {par_score}")

            return par_score
        except Exception as e:
            logging.error(f"Error in calculate_par_score: {e}")
            return 0

def load_dls_data():
    """Load DLS data from JSON file."""
    try:
        with open("dls_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error("DLS data file not found!")
        return {}
    except json.JSONDecodeError:
        logging.error("Error decoding JSON data.")
        return {}

def main():
    try:
        print("🏏 Duckworth-Lewis-Stern (DLS) Calculator")
        print("--------------------------------------")

        dls_data = load_dls_data()
        calculator = DLSCalculator(dls_data)

        print("📌 Select match format:")
        print("1. 50-over match")
        print("2. 20-over match")
        print("3. 100-ball match")

        match_format = int(input("Enter choice (1/2/3): "))
        if match_format == 1:
            dls_table = dls_data["dls_table_50"]
            max_overs = 50
        elif match_format == 2:
            dls_table = dls_data["dls_table_20"]
            max_overs = 20
        elif match_format == 3:
            dls_table = dls_data["dls_table_100"]
            max_overs = 20
        else:
            logging.error("❌ Invalid match format selected.")
            return

        team1_score = int(input("Enter Team 1's score: "))
        team1_overs = float(input(f"Enter Team 1's total overs (max {max_overs}): "))
        team2_overs = float(input(f"Enter Team 2's total overs (max {max_overs}): "))
        team2_current_overs = float(input(f"Enter Team 2's current overs (max {team2_overs}): "))
        team2_current_score = int(input("Enter Team 2's current score: "))
        team2_current_wickets = int(input("Enter Team 2's current wickets lost (0-10): "))

        revised_target = calculator.calculate_dls_target(team1_score, team1_overs, team2_overs, team2_current_wickets, dls_table)
        par_score = calculator.calculate_par_score(revised_target, team2_current_overs, team2_overs, team2_current_wickets, dls_table)
        difference = team2_current_score - par_score
        runs_needed = max(0, revised_target - team2_current_score)
        balls_remaining = int((team2_overs * 6) - (team2_current_overs * 6))
        required_run_rate = runs_needed / (balls_remaining / 6) if balls_remaining > 0 else 0

        print("\n🏆 **Match Status:**")
        print(f"🎯 Revised Target: {revised_target}")
        print(f"📊 Par Score: {par_score}")
        print(f"📌 Runs Needed: {runs_needed}")
        print(f"🕒 Balls Remaining: {balls_remaining}")
        print(f"⚡ Required Run Rate: {required_run_rate:.2f}")

        if difference < 0:
            print(f"❌ Team 2 is BEHIND the par score by {-difference} runs.")
        elif difference > 0:
            print(f"✅ Team 2 is AHEAD of the par score by {difference} runs.")
        else:
            print("⏳ Team 2 is ON PAR with the required score.")

    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")

if __name__ == "__main__":
    main()
