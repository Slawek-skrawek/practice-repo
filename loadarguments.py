import argparse
import os
import serial
import targetscripts
# import subprocess
# import loadimages

SERIAL_PORT = '/dev/ttyACM0'
SERIAL_RATE = 115200
ser = serial.Serial(SERIAL_PORT, SERIAL_RATE)

parser = argparse.ArgumentParser(description="Choose board, app and command to be performed")
parser.add_argument("board_name", help="Name of the board or all_boards")
parser.add_argument("app_name", help="Name of the application")
parser.add_argument("command", help="Command to be performed on the target")
args = parser.parse_args()

def perform_command(target_name, board_name, app_name, command):
    if command == "full_create":
        targetscripts.full_create_target(target_name, board_name, app_name)
    elif command == "create":
        targetscripts.create_target(target_name)
    elif command == "set":
        targetscripts.set_target(target_name, board_name, app_name)
    elif command == "build":
        targetscripts.build_target(target_name)
    elif command == "create_image":
        targetscripts.create_image(target_name)
    elif command == "load":
        targetscripts.load_image(target_name)
    else:
        print("Unknown command")

def main():
    board_name = args.board_name
    app_name = args.app_name
    command = args.command

    # targetscripts.run_cmd(f"cd {targetscripts.PROJECTS_DIR}")

    if board_name == "all_boards":
        for entry in os.scandir(targetscripts.BSP_DIR_PATH):
            if entry.is_dir():
                board_name = entry.name
                print(f"\nProcessing target board: {board_name}")
                target_name = targetscripts.create_target_name(board_name, app_name)
                perform_command(target_name, board_name, app_name, command)
                print(f"Done with {board_name}")
                print("-" * 40)
    else:
        print(f"\nProcessing target board: {board_name}")
        target_name = targetscripts.create_target_name(board_name, app_name)
        print(board_name, app_name, command, target_name)
        perform_command(target_name, board_name, app_name, command)
        print(f"Done with {board_name}")

    # if command == "create":
    #     targetscripts.create_target(target_name)
    # elif command == "set":
    #     targetscripts.set_target(target_name, board_name, app_name)
    # elif command == "build":
    #     targetscripts.build_target(target_name)
    # elif command == "create_image":
    #     targetscripts.create_image(target_name)
    # elif command == "load":
    #     targetscripts.load_image(target_name)
    # else:
    #     print("Unknown command")
    # return 0

if __name__ == "__main__":
    main()
