from pathlib import Path
from src.onboarding_agent import OnboardingAgent

agent = OnboardingAgent()

result = agent.run(
    customer_csv=Path("data/raw/client_d/customers.csv"),
    order_csv=Path("data/raw/client_d/orders.csv"),
    client_name="client_d"
)

print("status:", result["status"])
print("logs:")
for log in result["logs"]:
    print("-", log)

print("\nwarnings:")
for warning in result["warnings"]:
    print("-", warning)

print("\nerrors:")
for error in result["errors"]:
    print("-", error)

print("\nresult keys:")
print(result["results"].keys())