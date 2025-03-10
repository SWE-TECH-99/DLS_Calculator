import unittest
import json
from main import DLSCalculator  # Import the class instead of functions

# Load DLS data
with open("dls_data.json", "r") as file:
    dls_data = json.load(file)

# Instantiate DLSCalculator
calculator = DLSCalculator(dls_data)


class TestDLSCalculator(unittest.TestCase):

    def test_dls_target(self):
        """Test revised target calculations with various match scenarios."""
        cases = [
            (200, 50, 40.0, 3, dls_data["dls_table_50"], 122),  
            (150, 30, 25.0, 2, dls_data["dls_table_50"], 96),
            (300, 50, 50.0, 5, dls_data["dls_table_50"], 280)
        ]
        for t1_score, t1_overs, t2_overs, t2_wickets, dls_table, expected in cases:
            result = calculator.calculate_dls_target(t1_score, t1_overs, t2_overs, t2_wickets, dls_table)

            print(f"\n🟡 Test: {t1_score} runs in {t1_overs} overs, "
                  f"Target for {t2_overs} overs with {t2_wickets} wickets lost.")
            print(f"🔹 Expected: {expected}, Got: {result}")

            self.assertAlmostEqual(result, expected, delta=max(expected * 0.15, 5),
                                   msg=f"❌ Target calc error: Got {result}, expected {expected}")

    def test_edge_cases(self):
        """Test extreme boundary cases that could break the logic."""
        cases = [
            (0, 50, 40.0, 3, dls_data["dls_table_50"], 0),  
            (100, 20, 5.0, 8, dls_data["dls_table_50"], 36),
            (250, 50, 10.0, 5, dls_data["dls_table_50"], 120)
        ]
        for t1_score, t1_overs, t2_overs, t2_wickets, dls_table, expected in cases:
            result = calculator.calculate_dls_target(t1_score, t1_overs, t2_overs, t2_wickets, dls_table)

            print(f"\n🟡 Edge Case: {t1_score} runs in {t1_overs} overs, "
                  f"Target for {t2_overs} overs with {t2_wickets} wickets lost.")
            print(f"🔹 Expected: {expected}, Got: {result}")

            self.assertAlmostEqual(result, expected, delta=max(expected * 0.15, 5),
                                   msg=f"❌ Edge case error: Got {result}, expected {expected}")

    def test_high_pressure_chases(self):
        """Test high-stakes scenarios where teams need high run-rates."""
        cases = [
            (300, 50, 50.0, 3, dls_data["dls_table_50"], 290),
            (280, 50, 45.0, 6, dls_data["dls_table_50"], 250),
            (150, 20, 10.0, 2, dls_data["dls_table_20"], 100)
        ]
        for t1_score, t1_overs, t2_overs, t2_wickets, dls_table, expected in cases:
            result = calculator.calculate_dls_target(t1_score, t1_overs, t2_overs, t2_wickets, dls_table)

            print(f"\n🟡 High Pressure: {t1_score} runs in {t1_overs} overs, "
                  f"Target for {t2_overs} overs with {t2_wickets} wickets lost.")
            print(f"🔹 Expected: {expected}, Got: {result}")

            self.assertAlmostEqual(result, expected, delta=max(expected * 0.15, 5),
                                   msg=f"❌ High pressure chase error: Got {result}, expected {expected}")

    def test_par_score(self):
        """Test par score calculations under different conditions."""
        cases = [
            (150, 15.0, 20.0, 3, dls_data["dls_table_20"], 85),
            (200, 25.0, 30.0, 5, dls_data["dls_table_50"], 120),
            (300, 40.0, 50.0, 7, dls_data["dls_table_50"], 190)
        ]
        for revised_target, current_overs, total_overs, wickets, dls_table, expected_par in cases:
            result = calculator.calculate_par_score(revised_target, current_overs, total_overs, wickets, dls_table)

            print(f"\n🟡 Par Score: Revised target {revised_target}, "
                  f"{current_overs}/{total_overs} overs, {wickets} wickets lost.")
            print(f"🔹 Expected: {expected_par}, Got: {result}")

            self.assertAlmostEqual(result, expected_par, delta=max(expected_par * 0.15, 5),
                                   msg=f"❌ Par score error: Got {result}, expected {expected_par}")


if __name__ == "__main__":
    unittest.main()
