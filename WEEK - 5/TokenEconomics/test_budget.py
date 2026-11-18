import unittest
from budget import FeatureBudget


class TestFeatureBudget(unittest.TestCase):

    def setUp(self):
        self.budget = FeatureBudget(
            input_price=0.30,
            output_price=1.20,
            requests_per_day=2000,
            avg_input_tokens=1200,
            avg_output_tokens=300,
            peak_requests_per_minute=30,
            rpm_limit=60,
            tpm_limit=100000,
            monthly_budget=50,
            daily_budget=2,
            safety_margin=0.20
        )

    def test_cost_estimate(self):
        results = self.budget.calculate()

        self.assertEqual(results["input_tokens"], 2400000)
        self.assertEqual(results["output_tokens"], 600000)
        self.assertEqual(results["total_tokens"], 3000000)
        self.assertAlmostEqual(results["daily_cost"], 1.44)
        self.assertAlmostEqual(results["monthly_cost"], 43.20)

    def test_capacity_passes(self):
        results = self.budget.calculate()

        self.assertLessEqual(results["peak_rpm"], self.budget.rpm_limit)
        self.assertLessEqual(results["peak_tpm"], self.budget.tpm_limit)

    def test_rpm_limit_fails(self):
        self.budget.peak_requests_per_minute = 100
        results = self.budget.calculate()

        self.assertGreater(results["peak_rpm"], self.budget.rpm_limit)

    def test_monthly_budget_fails(self):
        self.budget.monthly_budget = 40
        results = self.budget.calculate()

        self.assertGreater(
            results["monthly_cost"] * (1 + self.budget.safety_margin),
            self.budget.monthly_budget
        )


if __name__ == "__main__":
    unittest.main()