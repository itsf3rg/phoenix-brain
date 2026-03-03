import requests
import time

URL = "http://127.0.0.1:8000/parse_and_evaluate"

payloads = [
    {
        "raw_text": "UberX Exclusive $12.08 $32.95/active hr (est.) 4.80 +$5.00 included 14 min (6.0 mi) ... 7 mins (1.8 mi) ... Accept",
        "description": "Hourly Bait + Heatmap Surge (Profitable enough, ~1.50/mi)",
        "platform": "uber"
    },
    {
        "raw_text": "UberX Exclusive Verified ✔ $11.50 $32.95/active hr (est.) 4.80 +$4.00 included 15 mins (5.0 mi) trip ... 4 mins (1.6 mi) away ... Accept",
        "description": "2026 Uber Exclusive with Parens & Surge",
        "platform": "uber"
    },
    {
        "raw_text": "Trip Radar UberX $22.40 45 mins (23.2 mi) Total Match",
        "description": "2026 Uber Trip Radar ListView",
        "platform": "uber"
    },
    {
        "raw_text": "5.5 $0.93 $25.80 5.0 $14.16 $20.50/hour est. rate for this ride 7 min • 3.2 mi 15 min • 10.3 mi Accept",
        "description": "2026 Lyft Stats Grid & Hourly Label",
        "platform": "lyft"
    },
    {
        "raw_text": "Lyft Shared $8.50 25 mins (15.0 mi) ... 2 mins (1.0 mi) ... Accept",
        "description": "Lyft Shared Offer (Decline Target, ~0.53/mi)",
        "platform": "lyft"
    }
]

print("Injecting test offers into GigBoss Brain...")
for p in payloads:
    print(f"\nSending: {p['description']}")
    try:
        response = requests.post(URL, json={"raw_text": p["raw_text"], "platform": p["platform"]})
        if response.status_code == 200:
            data = response.json()
            if "evaluation" in data and "decision" in data["evaluation"]:
                if data["evaluation"]["decision"] == "REJECT":
                    print(f"Rejected: {data.get('reason', 'No reason provided')}")
                else:
                    print(f"Fare: ${data['offer']['fare']}, Score: {data['evaluation']['score']}, Decision: {data['evaluation']['decision']}")
            elif "status" in data and data["status"] == "rejected":
                 print(f"Rejected: {data.get('reason', 'No reason provided')}")
            else:
                 print(f"Response: {data}")
            print("Check the Web Dashboard to see the live forensic analysis!")
        else:
            print(f"Failed to process: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to Brain. Make sure you run 'backend/run.ps1' first!")
        break
    
    time.sleep(3) # Wait between offers so user can see them appear in the dashboard
