import sys
import codecs
sys.path.append(r'C:\Users\ryanf\.gemini\antigravity\scratch\GigBoss\backend')
from engine.parser import parse_offer_text

log_file = r'C:\Users\ryanf\.gemini\antigravity\scratch\GigBoss\backend\incoming_payloads_debug.log'
out_file = r'C:\Users\ryanf\.gemini\antigravity\scratch\GigBoss\backend\bulk_test_results.txt'

try:
    with codecs.open(log_file, 'r', 'utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print("Log file not found.")
    sys.exit(1)

raw_payloads = []
blocks = content.split("--------------------------------------------------------------------------------")
for block in blocks:
    if "[UBER] RAW:" in block or "[LYFT] RAW:" in block:
        try:
            raw_text = block.split("RAW:")[1].strip()
            if raw_text:
                raw_payloads.append(raw_text)
        except IndexError:
            pass

false_positives = 0
valid_offers = 0

with codecs.open(out_file, 'w', 'utf-8') as out:
    out.write(f"Total payloads to process: {len(raw_payloads)}\n\n")

    for i, raw in enumerate(raw_payloads):
        result = parse_offer_text(raw, "uber")
        
        # We only care about payloads that passed the Triple Check (fare > 0)
        if result["fare"] > 0.0:
            # Heuristic to guess if it's a real offer or a false flag:
            # Real offers usually have the word "Accept", "Match", "UberX", "Exclusive", "Trip Radar"
            is_likely_real = any(keyword in raw.lower() for keyword in ["accept", "match", "uberx", "exclusive", "trip radar", "included"])
            
            if not is_likely_real:
                false_positives += 1
                out.write(f"\n[FALSE FLAG DETECTED - Payload {i}]\n")
                out.write(f"RAW OCR: {raw}\n")
                out.write(f"PARSED: {result}\n")
            else:
                valid_offers += 1
                out.write(f"\n[VALID STR DETECTED - Payload {i}]\n")
                out.write(f"RAW OCR: {raw}\n")
                out.write(f"PARSED: {result}\n")

    out.write(f"\n--- SUMMARY ---\n")
    out.write(f"Total Payloads Analyzed: {len(raw_payloads)}\n")
    out.write(f"Valid Offers Parsed: {valid_offers}\n")
    out.write(f"Potential False Flags Caught: {false_positives}\n")

print("Done. Check bulk_test_results.txt for output.")
