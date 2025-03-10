import unittest
from main import calculate_dls_target, calculate_par_score, interpolate_resources
import json

# Load DLS data
with open("dls_data.json", "r") as file:
    dls_data = json.load(file)

dls_table_50 = dls_data["dls_table_50"]
dls_table_20 = dls_data["dls_table_20"]
dls_table_100 = dls_data["dls_table_100"]

class TestDLSCalculator(unittest.TestCase):
    
    def test_interpolate_resources(self):
        """Test interpolation of resources in DLS table."""
        cases = [
            (dls_table_50, 45, 2, 81.3),
            (dls_table_50, 30, 5, 43.0),
            (dls_table_20, 15, 3, 67.9),
            (dls_table_100, 60, 2, 68.7)
        ]
        for table, overs, wickets, expected in cases:
            result = interpolate_resources(table, overs, wickets)
            self.assertAlmostEqual(result, expected, delta=expected * 0.07,
                                   msg=f"Interpolated value for overs={overs}, wickets={wickets} incorrect. Got {result}, expected {expected}")

    def test_dls_target(self):
        """Test revised target calculations with various match scenarios."""
        cases = [
            (200, 50, 30, 3, dls_table_50, 128),
            (175, 20, 12, 2, dls_table_20, 127),
            (155, 100, 45, 2, dls_table_100, 122),
            (250, 50, 15, 5, dls_table_50, 111),
            (50, 50, 30, 3, dls_table_50, 32)
        ]
        for t1_score, t1_overs, t2_overs, wickets, table, expected in cases:
            result = calculate_dls_target(t1_score, t1_overs, t2_overs, wickets, table)
            self.assertAlmostEqual(result, expected, delta=expected * 0.07,
                                   msg=f"Target calc error: Got {result}, expected {expected}")

    def test_edge_cases(self):
        """Test extreme boundary cases that could break the logic."""
        cases = [
            (250, 50, 50, 0, dls_table_50, 250),
            (300, 50, 10, 0, dls_table_50, 120),
            (0, 50, 30, 3, dls_table_50, 0)
        ]
        for score, t1_overs, t2_overs, wickets, table, expected in cases:
            result = calculate_dls_target(score, t1_overs, t2_overs, wickets, table)
            self.assertAlmostEqual(result, expected, delta=expected * 0.07,
                                   msg=f"Edge case error: Got {result}, expected {expected}")

    def test_high_pressure_chases(self):
        """Test high-stakes scenarios where teams need high run-rates."""
        cases = [
            (250, 50, 5, 0, dls_table_50, 36),
            (220, 50, 2, 0, dls_table_50, 14)
        ]
        for score, t1_overs, t2_overs, wickets, table, expected in cases:
            result = calculate_dls_target(score, t1_overs, t2_overs, wickets, table)
            self.assertAlmostEqual(result, expected, delta=expected * 0.07,
                                   msg=f"High pressure chase error: Got {result}, expected {expected}")

    def test_par_score(self):
        """Test par score calculations under different conditions."""
        cases = [
            (129, 50, 30, 3, dls_table_50, 33),
            (96, 50, 10, 0, dls_table_50, 29)
        ]
        for t1_score, t1_overs, t2_overs, current_overs, wickets, table, expected_par in cases:
            result = calculate_par_score(t1_score, current_overs, t2_overs, wickets, table)
            self.assertAlmostEqual(result, expected_par, delta=expected_par * 0.07,
                                   msg=f"Par score calc error: Got {result}, expected {expected_par}")

if __name__ == "__main__":
    unittest.main()
