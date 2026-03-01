from pydantic import BaseModel
from typing import Optional

class RideOffer(BaseModel):
    platform: str
    fare: float
    distance_miles: float
    pickup_minutes: int
    dropoff_location: str
    
# Phoenix Geography Multipliers
# We penalize trips to the far West/East Valley due to dead miles coming back.
# We boost trips to Sky Harbor, Scottsdale, and downtown Phoenix.
PHOENIX_ZONES = {
    "Sky Harbor Airport": 1.5,
    "Downtown Phoenix": 1.2,
    "Scottsdale": 1.3,
    "Tempe": 1.2,
    "Mesa": 1.0,
    "Chandler": 1.0,
    "Glendale": 0.9,
    "Peoria": 0.8,
    "Surprise": 0.6,    # High risk of dead miles
    "Goodyear": 0.6,    # High risk of dead miles
    "Buckeye": 0.4,     # Very high risk of dead miles
    "Apache Junction": 0.5,
    "Unknown": 1.0
}

def evaluate_ride(offer: RideOffer) -> dict:
    # 1. Base profitability (Dollars per mile)
    # Total distance estimation if not provided directly (assuming 3 min/mile for pickup)
    total_estimated_miles = offer.distance_miles + (offer.pickup_minutes / 3.0)
    
    if total_estimated_miles <= 0:
        base_score = 0
    else:
        dollars_per_mile = offer.fare / total_estimated_miles
        # Score out of 100 based on a baseline of $1.50/mile being a "100"
        base_score = min((dollars_per_mile / 1.50) * 100, 100)
    
    # 2. Apply Phoenix Zone Multiplier
    # Use exact match or default to Unknown (1.0)
    multiplier = 1.0
    for zone, multi in PHOENIX_ZONES.items():
        if zone.lower() in offer.dropoff_location.lower():
            multiplier = multi
            break
            
    final_score = base_score * multiplier
    
    # 3. Decision Logic
    # If final score > 75: ACCEPT
    # If final score < 50: DECLINE
    # Else: IGNORE (Let driver decide / wait for surge)
    
    decision = "IGNORE"
    if final_score >= 75.0:
        decision = "ACCEPT"
    elif final_score < 50.0:
        decision = "DECLINE"
        
    return {
        "score": round(final_score, 2),
        "decision": decision,
        "reasoning": f"Base DPM: ${dollars_per_mile:.2f}/mi. Zone Multiplier: {multiplier}x"
    }
