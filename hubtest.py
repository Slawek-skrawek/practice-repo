import argparse
from traceback import print_tb

import hid

PORT_STATE_UP = 1
PORT_STATE_DOWN = 0
PORT_STATE_ERROR = 255
PORT_STATE_DICT = {0: "DOWN", 1: "UP", 255: "ERROR"}

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Control power state of individual ports on a selected USB hub",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-i','--input',
        nargs='+',
        help="Specify port states in one of the following formats:\n"
             " - xxxxxxxx - set each port to turn ON (1), OFF (0) or leave it unchanged (x)\n"
             " - p s      - set port p (1-8) to state s ON (1), OFF (0)",
        metavar="INPUT")
    parser.add_argument(
        '-s', '--serial-number',
        type=str,
        help="Specify serial number of the hub controller",
        metavar="SERIAL")
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help="List attached hub controllers")
    parser.add_argument(
        '-d', '--power-down',
        type=int,
        help="Power off selected port (1-8)",
        metavar="PORT")
    parser.add_argument(
        '-u', '--power-up',
        type=int,
        help="Power on selected port (1-8)",
        metavar="PORT")
    parser.add_argument(
        '-g', '--get-state',
        type=int,
        help="Get state of selected port (1-8)",
        metavar="PORT")

    args = parser.parse_args()

    port_set = list(b"\x05xxxxxxxx")
    send_comand = False

    # print("Aha: " + str(args.serial_number) + " :ok")
    if args.serial_number:
        print(args.serial_number)
        for device in hid.enumerate():
            if device['serial_number'] == args.serial_number:
                print(device['path'])
                path = device['path']

    if args.list:
        i = 0
        print("Attached hub controllers:")
        for device in hid.enumerate(0xc0ca, 0xc001):
            i = i + 1
            print(f"{i}. Hub controller with serial number: {device['serial_number']}")

    if args.power_up:
        if 1 <= args.power_up <= 8:
            port_set[int(args.power_up)] = ord('1')
            send_comand = True

    if args.power_down:
        if 1 <= args.power_down <= 8:
            port_set[int(args.power_down)] = ord('0')
            send_comand = True

    # if args.get_state:

    if args.input:
        if len(args.input) == 1:
            input_set = args.input[0]
            if len(input_set) == 8:
                for index in range(1, len(port_set)):
                    port_set[index] = ord('1' if input_set[index - 1] == '1' else
                                          '0' if input_set[index - 1] == '0' else 'x')
                send_comand = True
            else:
                parser.error("Expected 8-character port_set")
        elif len(args.input) == 2:
            port_num, state= args.input
            if 1 <= int(port_num) <= 8  and state in ['0', '1', 'x']:
                port_set[int(port_num)] = ord('1' if state == '1' else
                                              '0' if state == '0' else 'x')
                send_comand = True
            else:
                parser.error("Expected state 0, 1 or x with port number <1,8>.")
        else:
            parser.error("Expected either a single 8-character port set or state 0, 1 or x with port number <1,8>.")

    if send_comand:
        hid_gpio_hub_set_usb_power(0xc0ca, 0xc001, args.serial_number, port_set)

def hid_gpio_hub_set_usb_power(vid, pid, sn, port_set):
    path = None
    cmd = bytes(port_set)

    for device in hid.enumerate(vid, pid):
        print(device)
        path = device['path']

    device = hid.device()
    device.open_path(path)
    device.send_feature_report(cmd)
    print(device.get_feature_report(5, 9))
    device.close()

    # Read the flashed versions of hid_gpio and apache-mynewt-core
    # print(device.get_indexed_string(32))
    # print(device.get_indexed_string(33))
    # Read the states of hub ports


def main():
    parse_arguments()
    # hid_gpio_hub_set_usb_power(0xc0ca, 0xc001)


if __name__ == "__main__":
    main()
