import re

def parse_offer_text(raw_text: str, platform: str = "uber") -> dict:
    """
    Advanced text parsing based on latest 2026 UI heuristics.
    Strips noise, prevents surge/hourly collisions, handles Lyft grids and Uber parens.
    """
    
    # 0. Text Gate / False Positive Filter
    # Prevent Lyft background map POIs (e.g. "$26 Lyft 8 min away AZA") from causing false $0 pings
    if platform.lower() == "lyft":
        if not re.search(r'(?i)\b(accept|reject|incl)\b', raw_text):
             return { "fare": 0.0, "pickup_miles": 0.0, "trip_miles": 0.0, "pickup_minutes": 0, "total_minutes": 0 }
    
    # 1. Cleanse rates (Uber: $/active hr, Lyft: $/hour est, $/mi)
    # PROJECT PHOENIX: Bait Filter - strip "per active hour" promos before fare extraction
    clean_text = re.sub(r'(?i)\$\s*[0-9,.]+\s*(per|/)\s*active\s*h(ou)?rs?', '', raw_text)
    clean_text = re.sub(r'(?i)\$\s*[0-9,.]+\s*/\s*h(ou)?rs?(\s*\(?est\.?\)?\s*)?', '', clean_text)
    clean_text = re.sub(r'(?i)\$\s*[0-9,.]+\s*/\s*mi(le)?s?', '', clean_text)
    
    # Resolve Google ML Kit duplicate period bleed (e.g. "1..2 mi" -> "1.2 mi")
    clean_text = clean_text.replace('..', '.')
    
    # PROJECT PHOENIX: Strip "TODAY's Earnings" widget so it doesn't contaminate the max() fare
    clean_text = re.sub(r'(?i)today\s*\$\s*[0-9,.]+', '', clean_text)

    # 2. Extract Fare
    # PROJECT PHOENIX: Negative lookbehind (?<!\+) ensures we ignore Map Surges (+$3.50)
    fare_matches = re.finditer(r'(?<!\+)\$\s*([0-9,]+(?:\.[0-9]{2})?)', clean_text)
    fares = []
    for m in fare_matches:
        raw_val = m.group(1).replace(",", "")
        try:
            val = float(raw_val)
            # OCR Decimal Restoration: If ML Kit missed the period (e.g. $744 -> $7.44)
            if '.' not in raw_val and val >= 100.0:
                 val = val / 100.0
            fares.append(val)
        except ValueError:
            pass
            
    fare = 0.0
    if fares:
        # PHOENIX V2: Upfront Fare = Base + Surge. Ergo, the true upfront fare is ALWAYS the max() dollar value on the screen.
        fare = max(fares)

    # 3. Extract Distances
    # Matches "5.0 mi", "(1.6 mi)", "3.2 mi". The parentheses will be ignored.
    distance_matches = re.finditer(r'(?i)([\d,\.]+(?:\.\d+)?)\s*mi(les?)?\b', clean_text)
    distances = []
    for m in distance_matches:
        try:
            distances.append(float(m.group(1).replace(",", "")))
        except ValueError:
            pass
            
    pickup_miles = 0.0
    trip_miles = 0.0
    if len(distances) >= 2:
        pickup_miles = min(distances)  # Usually pickup is shorter
        trip_miles = max(distances)    # Usually trip is longer
    elif len(distances) == 1:
        trip_miles = distances[0]
        
    # 4. Extract Times
    time_matches = re.finditer(r'(?i)([\d,\.]+)\s*min(s|utes?)?\b', clean_text)
    times = []
    for m in time_matches:
        try:
            times.append(int(m.group(1).replace(",", "").split('.')[0]))
        except ValueError:
            pass
            
    pickup_minutes = 0
    estimated_trip_minutes = 0

    if len(times) >= 2:
        pickup_minutes = min(times)
        estimated_trip_minutes = max(times)
    elif len(times) == 1:
        estimated_trip_minutes = times[0]
        
    # Fallback to Phoenix Grid metric (2 mins/mile) if we couldn't parse the trip time but have a distance
    if estimated_trip_minutes == 0 and trip_miles > 0:
        estimated_trip_minutes = int(trip_miles * 2.0)
        
    total_m = pickup_minutes + estimated_trip_minutes
    total_expected_miles = pickup_miles + trip_miles

    # PROJECT PHOENIX: The Quadruple Check
    # 1. Fast Strict Rejection: Filter out known junk keywords (e.g., Share rides)
    invalid_offer_keywords = ["share", "share (2)", "uber share", "pool"]
    if any(keyword in raw_text.lower() for keyword in invalid_offer_keywords):
        print(f"[REJECT_INVALID_PLATFORM] Payload contains a restricted ride type.")
        return {'fare': 0.0, 'pickup_miles': 0.0, 'trip_miles': 0.0, 'total_miles': 0.0, 'pickup_minutes': 0, 'total_minutes': 0}

    # 2. Quadruple Check: Ensure context matches a real offer to defeat background Heatmap false flags
    # We purposefully exclude "Accept" because it appears on navigation screens too often.
    valid_offer_keywords = ["uberx", "trip radar", "exclusive", "premium", "comfort", "xl"]
    
    if not any(keyword in raw_text.lower() for keyword in valid_offer_keywords):
        if platform.lower() == 'uber':
            print(f"[REJECT_NO_CONTEXT] Payload did not contain a valid Offer Keyword.")
            return {'fare': 0.0, 'pickup_miles': 0.0, 'trip_miles': 0.0, 'total_miles': 0.0, 'pickup_minutes': 0, 'total_minutes': 0}

    if fare > 0.0 and total_expected_miles > 0.0 and total_m > 0:
        return {
            "fare": fare,
            "pickup_miles": pickup_miles,
            "trip_miles": trip_miles,
            "total_miles": round(total_expected_miles, 2),
            "pickup_minutes": pickup_minutes,
            "total_minutes": total_m,
        }
    else:
        # Fails the constraints, this is just background UI noise.
        return { "fare": 0.0, "pickup_miles": 0.0, "trip_miles": 0.0, "total_miles": 0.0, "pickup_minutes": 0, "total_minutes": 0 }
