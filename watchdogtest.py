import os
import threading
import targetscripts

import serial

SERIAL_PORT = '/dev/ttyACM0'
SERIAL_RATE = 115200

ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)

print("Hello World!")

project_path = "/home/slawek/work/myproj"
board_type = "nordic_pca10040"
app_name = "watchdog"
target_name = f"{board_type}-{app_name}"

done = threading.Event()
os.chdir(project_path)

def watchdog_search():
    print("Watchdog test started.")
    dog = 0
    while True:
        reading = ser.readline()
        reading = reading.decode('utf-8', errors="ignore")
        print("    " + reading, end='')
        if "Reset reason: Watchdog" in reading:
            dog += 1
            print(f"Watchdog found! Dogs found: {dog}\nTest passed.")
            done.set()
            break

def watchdog_test():
    targetscripts.load_image(target_name)
    t = threading.Thread(target=watchdog_search(), daemon=True)
    t.start()
    if not done.wait(60):
        print("Timeout: Watchdog not found.\n"
              "Watchdog test failed.")

def main():
    watchdog_test()

if __name__ == "__main__":
    main()