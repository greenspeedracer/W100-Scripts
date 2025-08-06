def parse_lumi_packet(hex_str):
    # Clean and parse the colon-delimited string into integers
    hex_str = hex_str.strip().replace(" ", "")
    bytes_list = [int(b, 16) for b in hex_str.split(":")]

    if len(bytes_list) < 9:
        raise ValueError("Input is too short to contain a valid Lumi header")

    # Extract header
    header = bytes_list[:9]
    aa, msg_type, length_plus_3, integrity, counter, action, flag_41, length = header[0], header[1], header[2], header[3], header[4], header[5], header[6], header[8]

    print("🧱 Lumi Header:")
    print(f"  Start Byte     : 0x{aa:02X}")
    print(f"  Msg Type       : 0x{msg_type:02X}")
    print(f"  Length + 3     : 0x{length_plus_3:02X} → Payload length: {length_plus_3 - 3}")
    print(f"  Integrity Byte : 0x{integrity:02X}")
    print(f"  Counter        : 0x{counter:02X}")
    print(f"  Action         : 0x{action:02X}")
    print(f"  0x41 Flag      : 0x{flag_41:02X}")
    print(f"  Length Field   : 0x{length:02X}")

    # Next 2 bytes should be 0x00, 0x00
    if bytes_list[9] != 0x00 or bytes_list[10] != 0x00:
        print("\n⚠️ Warning: Expected 0x00 0x00 after header, got something else.")
    
    # MAC is next 6 bytes after 0x00, 0x00
    mac_start = 11
    mac_end = mac_start + 6
    mac = bytes_list[mac_start:mac_end]
    mac_str = ":".join(f"{b:02x}" for b in mac)

    print("\n🔍 MAC Address:")
    print(f"  {mac_str}")

    # Rest is payload chunk
    payload_chunk = bytes_list[mac_end:]

    print("\n📦 Payload Chunk:")
    print(f"  Raw (hex) : {' '.join(f'{b:02X}' for b in payload_chunk)}")
    print(f"  As bytes  : {payload_chunk}")
    
    return {
        "header": header,
        "mac": mac,
        "payload_chunk": payload_chunk
    }

# --- Run interactively ---
if __name__ == "__main__":
    hex_input = input("Paste colon-delimited hex string: ")
    try:
        parse_lumi_packet(hex_input)
    except Exception as e:
        print(f"\n❌ Error: {e}")
