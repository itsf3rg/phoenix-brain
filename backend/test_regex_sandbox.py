from engine.parser import parse_offer_text
import re

raw_test = "[UBER] RAW: D AVE 3:29 SANTA RANDE N 35TH AVE 2 UberX Exclusive $14.61 $21.91/active hr (est.) 23 min (5.8 mi) I-17-s * 4.85 9 +$8.75 included W Osborn Rd, Phoenix 16 mins (4.5 mi) AVE Avg. wait time at pickup: l min LO BH6T N W Indian School Rd, Phoenix Accept 7H AVE 7A X CENTRAL AVE NCENTRAL AVE"

print("--- EXECUTING PARSER ---")
result = parse_offer_text(raw_test, "uber")
print(result)

print("\n--- REGEX TRACE ---")
# Strip noise
clean_text = re.sub(r'(?i)\$\s*[0-9,.]+\s*(per|/)\s*active\s*h(ou)?rs?', '', raw_test)
clean_text = re.sub(r'(?i)\$\s*[0-9,.]+\s*/\s*h(ou)?rs?(\s*\(?est\.?\)?\s*)?', '', clean_text)
clean_text = re.sub(r'(?i)\$\s*[0-9,.]+\s*/\s*mi(le)?s?', '', clean_text)
clean_text = clean_text.replace('..', '.')
clean_text = re.sub(r'(?i)today\s*\$\s*[0-9,.]+', '', clean_text)
print("CLEAN TEXT:", clean_text)

time_matches = re.finditer(r'(?i)([\d,\.]+)\s*min(s|utes?)?\b', clean_text)
print("TIMES:", [m.group(1) for m in time_matches])

distance_matches = re.finditer(r'(?i)([\d,\.]+(?:\.\d+)?)\s*mi(les?)?\b', clean_text)
print("DISTANCES:", [m.group(1) for m in distance_matches])
