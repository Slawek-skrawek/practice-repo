import datetime
import threading
import time
import serial
import serial.tools.list_ports
import pyudev
import json
import hubcontrol
import targetscripts

SERIAL_PORT = '/dev/ttyACM0'
SERIAL_RATE = 115200
PORT_DELAY = 2

done = threading.Event()
context = pyudev.Context()

def watchdog_search(board_serial):
    print("Watchdog test started.")
    ports = serial.tools.list_ports.comports()
    ser = serial
    for port in ports:
        if 'ttyACM' in port.device:
            device = pyudev.Devices.from_device_file(context, port.device)
            device_serial = device.get('ID_SERIAL_SHORT')
            if device_serial == board_serial:
                ser = serial.Serial(port.device, SERIAL_RATE)

    reading = True
    while reading and ser.is_open:
        try:
            reading = ser.readline()
            reading = reading.decode('utf-8', errors="ignore")
            print("    " + reading, end='')
            if "Reset reason: Watchdog" in reading:
                print(f"Watchdog found!\nTest passed.")
                done.set()
                break
        except serial.serialutil.SerialException:
            reading = False
            print("Serial exception occurred.\nReading from serial failed.\n")

def watchdog_test(board_name, board_serial):
    target_name = targetscripts.create_target_name(board_name, "watchdog")
    targetscripts.load_image(target_name)
    done.clear()
    t = threading.Thread(target=watchdog_search, args=(board_serial, ), daemon=True)
    t.start()
    if not done.wait(60):
        print("Timeout: Watchdog not found.\n"
              "Watchdog test failed.")
    return done.is_set()


def watchdogs_hub(device_map_location = "/home/slawek/work/python/mynewt_tests/jsons/"):
    with open(f"{device_map_location}device_map.json", "r") as f:
        device_map = json.load(f)
    ports = device_map["Ports"]
    hub_serial = device_map["Hub serial"]
    hubcontrol.set_power(False, 'a', hub_serial)
    time.sleep(PORT_DELAY)

    board_pass = []
    for port in ports:
        board_name = port["Name"]
        board_serial = port['Serial_number']
        number = port["Port"]
        hubcontrol.set_power(True, number, hub_serial)
        time.sleep(PORT_DELAY)

        board_pass.append({
            "Port": number,
            "Board name": board_name,
            "Board serial": board_serial,
            "Test passed": watchdog_test(board_name, board_serial)
        })
        hubcontrol.set_power(False, number, hub_serial)
        time.sleep(PORT_DELAY)

    watchdog_test_result = {
        "Hub serial": hub_serial,
        "Watchdog tests": board_pass
    }
    now = (datetime.date.today())
    with open(f"{device_map_location}watchdog_test{now}.json", "w") as f:
        json.dump(watchdog_test_result, f, indent=2)

def main():
    watchdogs_hub()

if __name__ == "__main__":
    main()