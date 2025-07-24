import usb

# Find all connected USB devices
devices = usb.core.find(find_all=True)

for device in devices:
    print(f"Device: ID {device.idVendor:04x}:{device.idProduct:04x}")
    try:
        manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else "N/A"
        product = usb.util.get_string(device, device.iProduct) if device.iProduct else "N/A"
        serial = usb.util.get_string(device, device.iSerialNumber) if device.iSerialNumber else "N/A"
        print(f" |Manufacturer: {manufacturer}")
        print(f" |Product: {product}")
        print(f" |Serial Number: {serial}")
    except usb.core.USBError as e:
        print(f"  Could not retrieve descriptors: {e}")
    except ValueError as e:
        print(f"  Descriptor error: {e}")