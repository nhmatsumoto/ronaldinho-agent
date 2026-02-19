import sys
import json
import math

def calculate_npv(rate, cashflows):
    return sum(cf / (1 + rate)**i for i, cf in enumerate(cashflows))

def calculate_roi(gain, cost):
    if cost == 0: return 0
    return (gain - cost) / cost

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No action specified"}))
        return

    action = sys.argv[1]
    try:
        if action == "npv":
            rate = float(sys.argv[2])
            cashflows = [float(x) for x in sys.argv[3:]]
            result = calculate_npv(rate, cashflows)
            print(json.dumps({"npv": round(result, 2)}))
        elif action == "roi":
            gain = float(sys.argv[2])
            cost = float(sys.argv[3])
            result = calculate_roi(gain, cost)
            print(json.dumps({"roi": f"{round(result * 100, 2)}%"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
