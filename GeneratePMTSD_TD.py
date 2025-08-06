import random

def calculate_checksum(packet_bytes):
    return sum(packet_bytes) & 0xFF

def get_mac_input():
    mac_str = input("Enter MAC address (format: 54:EF:44:80:71:1A): ").strip()
    try:
        mac_bytes = [int(b, 16) for b in mac_str.split(":")]
        if len(mac_bytes) != 6:
            raise ValueError
        return mac_bytes
    except ValueError:
        print("Invalid MAC address format.")
        exit(1)

def get_user_input():
    power = int(input("Enter Power State (0 = On, 1 = Off): "))
    mode = int(input("Enter Mode (0=Cooling, 1=Heating, 2=Auto): "))
    temp = int(input("Enter Target Temperature (Celsius): "))
    speed = int(input("Enter Fan Speed (0=Auto, 1=Low, 2=Medium, 3=High): "))
    display = int(input("Enter Display? (0=Unknown, 1=Unknown): "))
    return power, mode, temp, speed, display

def build_pmtsd_string(power, mode, temp, speed, display):
    return f"P{power}_M{mode}_T{temp}_S{speed}_D{display}"

def encode_pmtsd_string(pmtsd):
    return [ord(c) for c in pmtsd]

def build_packet(power, mode, temp, speed, display, mac_bytes):
    pmtsd_str = build_pmtsd_string(power, mode, temp, speed, display)
    pmtsd_bytes = encode_pmtsd_string(pmtsd_str)
    pmtsd_len = len(pmtsd_bytes)

    packet = [
        0xAA, 0x71, 0x1F, 0x44,
        0x00, 0x00, 0x05, 0x41, 0x1C,
        0x00, 0x00, *mac_bytes,
        0x08, 0x00, 0x08, 0x44, pmtsd_len
    ] + pmtsd_bytes

    counter = random.randint(0x00, 0xFF)
    packet[4] = counter

    checksum = calculate_checksum(packet)
    packet[5] = checksum

    return packet, pmtsd_str, counter, checksum

def main():
    mac_bytes = get_mac_input()
    power, mode, temp, speed, display = get_user_input()
    packet, pmtsd_str, counter, checksum = build_packet(power, mode, temp, speed, display, mac_bytes)

    print(f"\nConstructed PMTSD String: {pmtsd_str}")
    print(f"Counter used: 0x{counter:02X}")
    print(f"Checksum:     0x{checksum:02X}")

    # Comma-delimited integer list
    comma_format = f"[{','.join(str(b) for b in packet)}]"

    # Colon-delimited hex string
    colon_format = ':'.join(f"{b:02x}" for b in packet)

    print("\nFinal Payload (colon-delimited hex):")
    print(colon_format)

    print("\nFinal Payload (Python list):")
    print(comma_format)

if __name__ == "__main__":
    main()
