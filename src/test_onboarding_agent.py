from pathlib import Path
from src.onboarding_agent import OnboardingAgent

agent = OnboardingAgent()

test_cases = [
    {
        "client_name": "client_a",
        "customer_csv": Path("data/raw/client_a/customers.csv"),
        "order_csv": Path("data/raw/client_a/orders.csv"),
    },
    {
        "client_name": "client_b",
        "customer_csv": Path("data/raw/client_b/customers.csv"),
        "order_csv": Path("data/raw/client_b/orders.csv"),
    },
    {
        "client_name": "client_c",
        "customer_csv": Path("data/raw/client_c/customers.csv"),
        "order_csv": Path("data/raw/client_c/orders.csv"),
    },
]

for case in test_cases:
    print(f"\n===== Testing {case['client_name']} =====")

    result = agent.run(
        customer_csv=case["customer_csv"],
        order_csv=case["order_csv"],
        client_name=case["client_name"]
    )

    print("status:", result["status"])
    print("result keys:", result["results"].keys())
    print("logs:")
    print("warnings:", result["warnings"])
    for log in result["logs"]:
        print(log)

    if result["errors"]:
        print("errors:", result["errors"])

    