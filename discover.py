import usb
import time
import json
import sys

import hubcontrol

NUM_PORTS = 7
PORT_DELAY = 2.5

def load_device_list(filename = "/home/slawek/work/python/mynewt_tests/jsons/device_list.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def identify_device(serial_number, device_map,
                    unknown_devices_file = "/home/slawek/work/python/mynewt_tests/jsons/unknown_devices"):
    device_name = device_map.get(serial_number, {"name": "unknown_device"})
    if device_name["name"] == "unknown_device":
        try:
            with open(unknown_devices_file, "a") as f:
                print(f"Unknown serial number: {serial_number}", file=f)
        except FileNotFoundError:
            pass
    return device_name

def snapshot_devices():
    snapshot = {}
    for dev in usb.core.find(find_all=True):
        try:
            serial = usb.util.get_string(dev, dev.iSerialNumber)
            snapshot[serial] = {
                "vendor_id": f"{dev.idVendor:04x}",
                "product_id": f"{dev.idProduct:04x}",
                "manufacturer": usb.util.get_string(dev, dev.iManufacturer),
                "product": usb.util.get_string(dev, dev.iProduct),
            }
        except Exception:
            continue  # Ignore unreadable devices
    return snapshot

def detect_new_device(before, after):
    # Return any serial number(s) present in after but not in before
    return {s: after[s] for s in after if s not in before}

def probe_port(port, hubcontroller = hubcontrol.HubController()):
    print(f"\nProbing port {port}")
    before = snapshot_devices()

    hubcontroller.set_power(port, True)
    time.sleep(PORT_DELAY)
    after = snapshot_devices()

    new_devices = detect_new_device(before, after)
    if not new_devices:
        print("No new device found.")
    else:
        for serial, info in new_devices.items():
            print(f"Detected new device:")
            print(f"  Serial      : {serial}")
            print(f"  Vendor ID   : {info['vendor_id']}")
            print(f"  Product ID  : {info['product_id']}")
            print(f"  Manufacturer: {info['manufacturer']}")
            print(f"  Product     : {info['product']}")
    hubcontroller.set_power(port, False)
    return new_devices

def map_ports(hubcontroller = hubcontrol.HubController()):
    hubcontroller.set_power('a', False)
    device_map = load_device_list()

    results = {}
    for port in range(1, NUM_PORTS + 1):
        new_dev = probe_port(port, hubcontroller)
        if new_dev:
            results[port] = new_dev

    print("\n--- Port Mapping Result ---")
    ports_list = []
    for port, devs in results.items():
        for serial, info in devs.items():
            identified_device = identify_device(serial, device_map)
            name = identified_device["name"]
            ports_list.append({
                'Port': port,
                'Serial_number': serial,
                'Name': name
            })
            print(f"Port {port}: {serial} - {name}")
    return {
        "Hub serial": hubcontroller.serial,
        "Ports": ports_list
    }

def main(device_map_location = "/home/slawek/work/python/mynewt_tests/jsons/"):
    if sys.argv[1:]:
        hub_serial = sys.argv[1]
    else:
        hub_serial = ""

    hubcontroller = hubcontrol.HubController()
    hubcontroller.serial = hub_serial
    hubcontroller.find_hub()
    device_map = map_ports(hubcontroller)
    with open(f"{device_map_location}device_map.json", "w") as f:
        json.dump(device_map, f, indent=2)

if __name__ == "__main__":
    main()