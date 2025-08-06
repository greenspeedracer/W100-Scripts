def prompt_mac(prompt_text, default=None):
    while True:
        mac_input = input(f"{prompt_text}{f' [{default}]' if default else ''}: ").strip().lower()
        if not mac_input and default:
            return [int(b, 16) for b in default.split(":")]
        parts = mac_input.split(":")
        if len(parts) == 8 and all(len(p) == 2 and all(c in '0123456789abcdef' for c in p) for p in parts):
            return [int(p, 16) for p in parts]
        print("Invalid MAC address. Must be 8 bytes like: 54:ef:44:10:01:2d:d6:31")

def prompt_int(prompt_text, default=None):
    while True:
        try:
            raw = input(f"{prompt_text}{f' [{default}]' if default is not None else ''}: ").strip()
            if raw == '' and default is not None:
                return default
            return int(raw, 0)
        except ValueError:
            print("Enter a valid number (decimal or hex, like 0x3f)")

def generate_message(frame_id, seq, target_mac):
    base = [
        0xaa, 0x71, 0x1c, 0x44, 0x69, 0x1c, 0x04, 0x41,
        0x19, 0x68, 0x91,
        frame_id & 0xFF,
        seq & 0xFF,
        0x18,
        *target_mac,
    ]
    while len(base) < 34:
        base.append(0x00)
    return base

def main():
    print("=== Aqara TH-S04D HVAC OFF Message Generator (colon+array output) ===")

    default_target_mac = "54:ef:44:10:01:2d:d6:31"
    target_mac = prompt_mac("Enter target MAC (device)", default=default_target_mac)

    start_frame = prompt_int("Starting Frame ID (e.g., 0xb8)", default=0xb8)
    start_seq = prompt_int("Starting Sequence (e.g., 0x3e)", default=0x3e)

    count = prompt_int("How many messages to generate?", default=1)
    auto_inc = input("Auto-increment Frame ID and Sequence for each message? (y/n) [y]: ").strip().lower() != 'n'

    print("\nGenerated Message(s):")
    for i in range(count):
        fid = (start_frame + i) & 0xFF if auto_inc else start_frame
        seq = (start_seq + i) & 0xFF if auto_inc else start_seq
        frame = generate_message(fid, seq, target_mac)
        colon_format = ":".join(f"{b:02x}" for b in frame)
        array_format = "[" + ",".join(str(b) for b in frame) + "]"
        print(f"{i+1:>2}: {colon_format}")
        print(f"    {array_format}")

if __name__ == "__main__":
    main()
