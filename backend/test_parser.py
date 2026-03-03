import sys
import json
sys.path.append(r'C:\Users\ryanf\.gemini\antigravity\scratch\GigBoss\backend')
from engine.parser import parse_offer_text

test_cases = [
    {
        "name": "Live Offer 1: True Distances are Cumulative, not Bounds",
        "raw": "TI 2:37 APOLLO HEIGHTS Glendale BELAIRE MARYVALE $13.77 60 2 UberX Exclusive 10 $20.65/active hr (est.) 7 min (1.9 mi) I-17-S +$475 * 4.98 ) +$3.25 included W Thomas Rd, Phoenix +$4.7. Accept Avg. wait time at pickup: 1 min 32 mins (18.3 mi) N Litchfield Rd, Goodyear ll 77 CANTO +$5.75 Phoenix X 17 TI U H FO",
        "expected_fare": 13.77,
        "expected_pickup_miles": 1.9,
        "expected_trip_miles": 18.3,
        "expected_total_miles": 20.2 # THIS should be the exact sum
    },
    {
        "name": "Live Offer 2: Bleeding Map Surge without the Plus Symbol",
        "raw": "2:38 .25 $3.50 TH AVE 1% AHL6I N N 371 A WCAMELBACKRD +$4.75 IAN SCHOOLRD Unlock Gold VE Encanto Park 2 17% O NATRAL AVE NCENTRAL AVE K +$5.75 +$3.25 next trip LateOoday NZTHST Japanese Rriendship Garden E-CAMELBACK RD LS HLL N 5 ill (77 < !! 371 pts",
        "expected_fare": 0.0, # There is NO UPFRONT FARE HERE. It's just a background map. But ML Kit read "+$3.50" as "$3.50". 
        "expected_pickup_miles": 0.0,
        "expected_trip_miles": 0.0
    }
]

for t in test_cases:
    print(f"\n--- Testing: {t['name']} ---")
    result = parse_offer_text(t['raw'], "uber")
    print(json.dumps(result, indent=2))
