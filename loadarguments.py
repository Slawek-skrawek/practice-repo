import argparse
import os
import targetscripts
# import command as cmd

PROJECTS_DIR = "~/work/myproj"
BSP_DIR_PATH = "/home/slawek/work/myproj/repos/apache-mynewt-core/hw/bsp/"

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Choose board, app and command to be performed",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "board",
        nargs="+",
        help="Name of the board [boards] or 'all_boards' keyword")
    parser.add_argument(
        "app_name",
        help="Name of the application")
    parser.add_argument(
        "command",
        help="Command to be performed on the target. List of commands:\n"
             " full_create  - creates, sets, builds target and creates image\n"
             " create       - creates target, if it does not exist\n"
             " set          - sets targets app, bsp and debug profile\n"
             " build        - builds target\n"
             " create_image - creates image of the built target\n"
             " load         - loads targets image on the device\n")
    parser.add_argument(
        "-f", "--file",
        action="store_true",
        help="interpret board as a file to load boards from instead",
    )
    return parser.parse_args()

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
    args = parse_arguments()
    board_list = args.board
    board_name = board_list[0]
    app_name = args.app_name
    command = args.command

    if args.file:
        board_list = []
        with open(board_name, "r") as f:
            board_list = f.read().split()

    if board_name == "all_boards":
        for entry in os.scandir(BSP_DIR_PATH):
            if entry.is_dir():
                board_name = entry.name
                print(f"\nProcessing target board: {board_name}")
                target_name = targetscripts.create_target_name(board_name, app_name)
                perform_command(target_name, board_name, app_name, command)
                print(f"Done with {board_name}")
                print("-" * 40)
    else:
        for board_name in board_list:
            print(f"\nProcessing target board: {board_name}")
            target_name = targetscripts.create_target_name(board_name, app_name)
            print(f"Board name: {board_name}\nApp name: {app_name}\n"
                  f"Command name: {command}\nTarget name: {target_name}")
            perform_command(target_name, board_name, app_name, command)
            print(f"Done with {board_name}")


if __name__ == "__main__":
    main()
