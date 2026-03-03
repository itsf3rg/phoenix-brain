import sys
import codecs
import re

log_file = r'C:\Users\ryanf\.gemini\antigravity\scratch\GigBoss\backend\incoming_payloads_debug.log'

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

def test_extract_fare(raw_text):
    # Strip hourly bait
    clean_text = re.sub(r'(?i)\$\s*[0-9,.]+\s*(per|/)\s*active\s*h(ou)?rs?', '', raw_text)
    clean_text = re.sub(r'(?i)\$\s*[0-9,.]+\s*/\s*h(ou)?rs?(\s*\(?est\.?\)?\s*)?', '', clean_text)
    clean_text = re.sub(r'(?i)\$\s*[0-9,.]+\s*/\s*mi(le)?s?', '', clean_text)
    
    # NEW: Strip "TODAY $XX.XX" widget
    clean_text = re.sub(r'(?i)today\s*\$\s*[0-9,.]+', '', clean_text)
    
    # Strip explicit surges that have a '+'
    fare_matches = re.finditer(r'(?<!\+)\$\s*([0-9,]+(?:\.[0-9]{2})?)', clean_text)
    fares = []
    for m in fare_matches:
        raw_val = m.group(1).replace(",", "")
        try:
            val = float(raw_val)
            if '.' not in raw_val and val >= 100.0:
                 val = val / 100.0
            fares.append(val)
        except ValueError:
            pass
            
    # NEW: Find the max fare in the list
    if len(fares) > 0:
        return max(fares), fares
    return 0.0, fares

print(f"Testing max() logic on {len(raw_payloads)} payloads...")
for i, raw in enumerate(raw_payloads):
    max_fare, all_fares = test_extract_fare(raw)
    if len(all_fares) > 1:
        print(f"Payload {i} has multiple fares: {all_fares} -> Selected {max_fare}")
