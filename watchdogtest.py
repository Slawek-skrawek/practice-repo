import os
import subprocess
import threading
from time import sleep

import serial

SERIAL_PORT = '/dev/ttyACM0'
SERIAL_RATE = 115200

ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)

print("Hello World!")

project_path = "/home/slawek/work/myproj"
board_type = "nordic_pca10040"
app_name = "watchdog"
target_name = f"{board_type}-{app_name}"

os.chdir(project_path)


def create_and_set():
    subprocess.check_call(f'newt target create {target_name}',
                          env=None, cwd=project_path, shell=True, executable='/bin/bash')
    subprocess.check_call(f'newt target set {target_name} app=apps/{app_name}',
                          env=None, cwd=project_path, shell=True, executable='/bin/bash')
    subprocess.check_call(f'newt target set {target_name} bsp=@apache-mynewt-core/hw/bsp/{board_type}',
                          env=None, cwd=project_path, shell=True, executable='/bin/bash')
    subprocess.check_call(f'newt target set {target_name} build_profile=debug',
                          env=None, cwd=project_path, shell=True, executable='/bin/bash')

def create_img():
    subprocess.check_call(f'newt create-image {target_name} timestamp',
                          env=None, cwd=project_path, shell=True, executable='/bin/bash')

def load_img():
    subprocess.check_call(f'newt load {target_name}',
                          env=None, cwd=project_path, shell=True, executable='/bin/bash')



def watchdog_test():
    print("Watchdog test started.")
    dog = 0
    # line = 1
    while True:
        reading = ser.readline()
        reading = reading.decode('utf-8', errors="ignore")
        print("    " + reading, end='')
        if "Reset reason: Watchdog" in reading:
            dog += 1
            print(f"Watchdog found! Dogs found: {dog}\nTest passed.")
            done.set()
            break
        # else:
        #     line += 1
        # if line > 6:
        #     print(f"Watchdog failed! Dogs found: {dog}\nTest failed.")
        #     break

# create_and_set()
# create_img()
load_img()

done = threading.Event()
t = threading.Thread(target=watchdog_test, daemon=True)
t.start()
if not done.wait(60):
    print("Timeout: Watchdog not found.\n"
          "Watchdog test failed.")
# watchdog_test()
