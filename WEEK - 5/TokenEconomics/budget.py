import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class FeatureBudget:
    input_price: float
    output_price: float
    requests_per_day: int
    avg_input_tokens: int
    avg_output_tokens: int
    peak_requests_per_minute: int
    rpm_limit: int
    tpm_limit: int
    monthly_budget: float
    daily_budget: float
    safety_margin: float

    @classmethod
    def from_env(cls):
        return cls(
            input_price=float(os.getenv("INPUT_PRICE_PER_MILLION")),
            output_price=float(os.getenv("OUTPUT_PRICE_PER_MILLION")),
            requests_per_day=int(os.getenv("REQUESTS_PER_DAY")),
            avg_input_tokens=int(os.getenv("AVG_INPUT_TOKENS")),
            avg_output_tokens=int(os.getenv("AVG_OUTPUT_TOKENS")),
            peak_requests_per_minute=int(os.getenv("PEAK_REQUESTS_PER_MINUTE")),
            rpm_limit=int(os.getenv("RPM_LIMIT")),
            tpm_limit=int(os.getenv("TPM_LIMIT")),
            monthly_budget=float(os.getenv("MONTHLY_BUDGET_USD")),
            daily_budget=float(os.getenv("DAILY_BUDGET_USD")),
            safety_margin=float(os.getenv("SAFETY_MARGIN_PERCENT")) / 100
        )

    def calculate(self):
        input_tokens = self.requests_per_day * self.avg_input_tokens
        output_tokens = self.requests_per_day * self.avg_output_tokens
        total_tokens = input_tokens + output_tokens

        daily_cost = (
            input_tokens / 1_000_000 * self.input_price
            + output_tokens / 1_000_000 * self.output_price
        )

        monthly_cost = daily_cost * 30

        peak_rpm = self.peak_requests_per_minute * (1 + self.safety_margin)
        peak_tpm = (
            self.peak_requests_per_minute
            * (self.avg_input_tokens + self.avg_output_tokens)
            * (1 + self.safety_margin)
        )

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "daily_cost": daily_cost,
            "monthly_cost": monthly_cost,
            "peak_rpm": peak_rpm,
            "peak_tpm": peak_tpm
        }

    def check_limits(self, results):
        print("\n--- LIMIT CHECK ---")

        rpm_ok = results["peak_rpm"] <= self.rpm_limit
        tpm_ok = results["peak_tpm"] <= self.tpm_limit
        daily_ok = results["daily_cost"] * (1 + self.safety_margin) <= self.daily_budget
        monthly_ok = results["monthly_cost"] * (1 + self.safety_margin) <= self.monthly_budget

        print(f"RPM: {'PASS' if rpm_ok else 'REVIEW'}")
        print(f"TPM: {'PASS' if tpm_ok else 'REVIEW'}")
        print(f"Daily Budget: {'PASS' if daily_ok else 'REVIEW'}")
        print(f"Monthly Budget: {'PASS' if monthly_ok else 'REVIEW'}")

        if all([rpm_ok, tpm_ok, daily_ok, monthly_ok]):
            print("\nGO: Feature is within all limits.")
        else:
            print("\nNO-GO: Review the limits before deployment.")

    def report(self):
        results = self.calculate()

        print("\n===== TOKEN ECONOMICS REPORT =====")
        print(f"Input Tokens/Day: {results['input_tokens']:,}")
        print(f"Output Tokens/Day: {results['output_tokens']:,}")
        print(f"Total Tokens/Day: {results['total_tokens']:,}")
        print(f"Daily Cost: ${results['daily_cost']:.2f}")
        print(f"Monthly Cost: ${results['monthly_cost']:.2f}")
        print(f"Peak RPM with Margin: {results['peak_rpm']:.0f}")
        print(f"Peak TPM with Margin: {results['peak_tpm']:.0f}")

        self.check_limits(results)


if __name__ == "__main__":
    budget = FeatureBudget.from_env()
    budget.report()