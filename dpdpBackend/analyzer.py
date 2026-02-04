import re
import csv
import sys
import os

# --- 1. The "Virus Definitions" (Regex Patterns) ---
# These are the "signatures" we are looking for.
PATTERNS = {
    "AADHAAR_NUM": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "PAN_CARD": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"),
    # FIXED: Added (?:) so it doesn't just capture the prefix
    "INDIAN_MOBILE": re.compile(r"\b(?:(?:\+91[\-\s]?)?[6-9]\d{9})\b") 
}

# --- 2. The Core Scanner Function ---
def scan_text_for_pii(text_chunk, line_number="Unknown"):
    """
    Scans a single string (text_chunk) for all defined patterns.
    Returns a list of findings.
    """
    findings = []
    for pii_type, pattern in PATTERNS.items():
        matches = pattern.findall(text_chunk)
        for match in matches:
            # If match is a tuple (common in complex regex), join it
            if isinstance(match, tuple):
                match = "".join(match)
            
            # Redact the data for the report (Privacy by Design!)
            # We show only last 4 digits: "********1234"
            redacted = "*" * (len(match) - 4) + match[-4:]
            
            findings.append({
                "type": pii_type,
                "value_masked": redacted,
                "line": line_number
            })
    return findings

# --- 3. File Handlers ---

def process_csv(file_path):
    print(f"[*] Scanning CSV: {file_path}...")
    leaks = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            for row_idx, row in enumerate(reader):
                # Convert the whole row to a single string to scan it
                row_text = " ".join(row)
                row_leaks = scan_text_for_pii(row_text, line_number=row_idx+1)
                leaks.extend(row_leaks)
    except Exception as e:
        print(f"[!] Error reading CSV: {e}")
    return leaks

def process_sql_dump(file_path):
    print(f"[*] Scanning SQL Dump: {file_path}...")
    leaks = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # SQL dumps can be huge (GBs). We read line by line to avoid crashing RAM.
            for line_idx, line in enumerate(f):
                line_leaks = scan_text_for_pii(line, line_number=line_idx+1)
                leaks.extend(line_leaks)
    except Exception as e:
        print(f"[!] Error reading SQL: {e}")
    return leaks

# --- 4. The Main Execution ---
if __name__ == "__main__":
    # Simple CLI interface
    if len(sys.argv) < 2:
        print("Usage: python pii_scanner.py <filename>")
        sys.exit(1)

    target_file = sys.argv[1]
    
    if not os.path.exists(target_file):
        print(f"[!] File not found: {target_file}")
        sys.exit(1)

    # Detect file type
    findings = []
    if target_file.endswith('.csv'):
        findings = process_csv(target_file)
    elif target_file.endswith('.sql') or target_file.endswith('.txt'):
        findings = process_sql_dump(target_file)
    else:
        print("[!] Unsupported file type. Please use .csv, .sql, or .txt")
        sys.exit(1)

    # --- 5. The Report ---
    print("\n" + "="*30)
    print("   DPDP COMPLIANCE REPORT   ")
    print("="*30)
    
    if not findings:
        print("✅ No PII found. File appears safe.")
    else:
        print(f"⚠️  DANGER: Found {len(findings)} Potential Data Leaks!")
        print("-" * 30)
        print(f"{'TYPE':<15} | {'LINE':<5} | {'MASKED VALUE'}")
        print("-" * 30)
        for f in findings:
            print(f"{f['type']:<15} | {f['line']:<5} | {f['value_masked']}")
        
        print("\n[!] Recommendation: Encrypt these fields immediately.")