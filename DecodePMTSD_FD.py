def decode_pmtsd(hex_string):
    # Remove colons and convert to bytes
    hex_string = hex_string.replace(":", "").strip()
    data = bytes.fromhex(hex_string)

    # Find the payload length byte - it's after the fixed header and trailing bytes.
    # From your examples, payload length is the byte just before the ASCII payload.
    # We see pattern: last fixed bytes before payload: 08 44
    # Payload length byte is right after that.

    # Find index of sequence 0x08, 0x44
    try:
        idx = data.index(b'\x08\x44') + 2
    except ValueError:
        print("Error: Could not find payload header bytes 08 44")
        return

    if idx >= len(data):
        print("Error: Payload length byte missing")
        return

    payload_length = data[idx]
    payload_start = idx + 1
    payload_end = payload_start + payload_length

    if payload_end > len(data):
        print("Error: Payload length exceeds data length")
        return

    payload_bytes = data[payload_start:payload_end]

    try:
        payload_ascii = payload_bytes.decode('ascii')
    except UnicodeDecodeError:
        print("Error: Payload is not valid ASCII")
        return

    print(f"Payload ASCII: '{payload_ascii}'")

    # Parse key-value pairs from payload separated by '_'
    pairs = payload_ascii.split('_')
    decoded = {}
    for p in pairs:
        if len(p) < 2:
            continue
        key = p[0]
        value = p[1:]
        decoded[key] = value

    print("Decoded values:")
    for k, v in decoded.items():
        print(f"  {k} = {v}")


if __name__ == "__main__":
    print("Paste your hex data (colon separated), or 'exit' to quit:")
    while True:
        user_input = input("> ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue
        decode_pmtsd(user_input)
