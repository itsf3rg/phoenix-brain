from models.offer import RideOffer

def calculate_score(offer: RideOffer) -> dict:
    """
    Evaluates the profitability of an offer based on the Phoenix market mechanics.
    Metrics:
    - $/mi: Fare / Total Miles (Target >= 1.20)
    - $/hr: Fare / (Total Minutes / 60) (Target >= 30.00)
    """
    if offer.total_miles <= 0 or offer.total_minutes <= 0:
        return {"score": 0, "decision": "DECLINE", "reason": "Invalid distance/time metrics"}

    dollars_per_mile = offer.fare / offer.total_miles
    dollars_per_hour = (offer.fare / offer.total_minutes) * 60

    base_score = 0
    if dollars_per_mile >= 1.20 and dollars_per_hour >= 30.0:
        base_score = 80
    elif dollars_per_mile >= 0.85 and dollars_per_hour >= 20.0:
        base_score = 50
    else:
        base_score = 10

    # Multiplier applies market-specific logic
    multiplier = 1.0
    final_score = min(base_score * multiplier, 100.0)

    decision = "IGNORE"
    if final_score >= 75:
        decision = "ACCEPT"
    elif final_score < 40:
        decision = "DECLINE"

    return {
        "score": final_score,
        "decision": decision,
        "dollars_per_mile": round(dollars_per_mile, 2),
        "dollars_per_hour": round(dollars_per_hour, 2)
    }
