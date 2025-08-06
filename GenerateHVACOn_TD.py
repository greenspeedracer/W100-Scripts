import os

def clean_mac(mac: str, expected_len: int) -> str:
    mac = mac.replace(":", "").replace("-", "").lower()
    if len(mac) != expected_len:
        raise ValueError(f"MAC must be {expected_len} hex digits long (you entered {len(mac)}).")
    return mac

def hex_bytes_to_list_str(byte_data: bytes) -> str:
    return '[' + ','.join(str(b) for b in byte_data) + ']'

def generate_hvac_on_message():
    print("--- HVAC ON Message Builder ---")

    try:
        device_mac = clean_mac(input("Enter TH-S04D MAC (format: 54:EF:44:10:01:2D:D6:31): "), 16)
        hub_mac = clean_mac(input("Enter Hub MAC (format: 54:EF:44:80:71:1A): "), 12)
    except ValueError as e:
        print("Error:", e)
        return

    # Fixed Zigbee prefix + 2 random bytes
    prefix = bytearray.fromhex("aa713244") + os.urandom(2)

    # Static Zigbee middle (do not touch)
    zigbee_header = bytearray.fromhex("02412f6891")

    # 2-byte message ID (random) + static 0x18
    message_id = os.urandom(2)
    message_control = bytearray([0x18])

    # Device and hub MACs
    payload_macs = bytearray.fromhex(device_mac) + bytearray.fromhex("0000") + bytearray.fromhex(hub_mac)

    # Static tail
    payload_tail = bytearray.fromhex("08000844150a0109e7a9bae8b083e58a9f000000000001012a40")

    # Build final frame
    frame = prefix + zigbee_header + message_id + message_control + payload_macs + payload_tail

    # Print outputs
    print("\nGenerated HVAC ON Frame (colon-delimited):")
    print(":".join(f"{b:02x}" for b in frame))

    print("\nZigbee2MQTT payload format:")
    print(hex_bytes_to_list_str(frame))

if __name__ == "__main__":
    generate_hvac_on_message()
