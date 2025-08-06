import re

def hex_to_bytes(hex_string):
    hex_string = hex_string.replace(":", "").replace(" ", "").lower()
    if len(hex_string) % 2 != 0:
        print("Invalid hex string length")
        return None
    try:
        return bytes.fromhex(hex_string)
    except ValueError:
        print("Invalid hex string")
        return None

def decode_p(p):
    return "On" if p == "0" else "Off"

def decode_m(m):
    return {"0":"Cooling","1":"Heating","2":"Auto"}.get(m, "Unknown")

def decode_s(s):
    return {"0":"Auto","1":"Low","2":"Medium","3":"High"}.get(s, "Unknown")

def decode_d(d):
    return "Unknown"  # no known mapping yet

def find_full_pmt_sd(ascii_str):
    pattern = re.compile(r'P([01])_M([012])_T(1[0-9]|2[0-9]|3[0-5]|[0-9])_S([0-3])_D([01])')
    return pattern.findall(ascii_str)

def find_individual_fields(ascii_str):
    # Find all individual fields like P0, M1, T23, S0, D1 etc.
    pattern = re.compile(r'(P|M|T|S|D)(\d{1,2})')
    return pattern.findall(ascii_str)

def main():
    while True:
        s = input("Enter hex string (or 'e' to exit): ").strip()
        if s.lower() == 'e':
            break

        data = hex_to_bytes(s)
        if not data:
            continue

        ascii_str = data.decode('ascii', errors='ignore')

        print("\n=== Searching for full PMTSD ASCII patterns ===")
        full_patterns = find_full_pmt_sd(ascii_str)
        if full_patterns:
            for idx, (p,m,t,s,d) in enumerate(full_patterns, start=1):
                print(f"Full pattern {idx}: P={p} ({decode_p(p)}), M={m} ({decode_m(m)}), T={t}°C, S={s} ({decode_s(s)}), D={d} ({decode_d(d)})")
        else:
            print("No full PMTSD sequences found.")

        print("\n=== Searching individual PMTSD fields ===")
        individual_fields = find_individual_fields(ascii_str)
        if individual_fields:
            for i, (field, val) in enumerate(individual_fields, start=1):
                if field == "P":
                    print(f"Field {i}: P (Power) = {val} ({decode_p(val)})")
                elif field == "M":
                    print(f"Field {i}: M (Mode) = {val} ({decode_m(val)})")
                elif field == "T":
                    print(f"Field {i}: T (Temp) = {val}°C")
                elif field == "S":
                    print(f"Field {i}: S (Fan) = {val} ({decode_s(val)})")
                elif field == "D":
                    print(f"Field {i}: D (Display) = {val} ({decode_d(val)})")
        else:
            print("No individual PMTSD fields found.")

        print("\n---\n")

if __name__ == "__main__":
    main()
