import os
import subprocess
import traceback
import serial

SERIAL_PORT = '/dev/ttyACM0'
SERIAL_RATE = 115200
ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)

# Path containing the Mynewt project
PROJECTS_DIR = "~/work/myproj"
board_type = "nordic_pca10040"
app_name = "blinky"
target_name = f"{board_type}-{app_name}"

def run_cmd(cmd, check=True):
    """Runs a shell command and returns (success, output)."""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        traceback.print_exc()
        return False, e.stderr


def main():
    run_cmd(f"cd {PROJECTS_DIR}")
    print(f"Loading target: {target_name}")
    success, output = run_cmd(f"newt load {target_name}", check=False)
    print(output)
    if not success:
        print(f" Load failed for {target_name}:\n{output}")
        return


if __name__ == "__main__":
    main()
