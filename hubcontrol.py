import argparse
import hid
import sys

class CustomParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f"Error: {message[0].upper() + message[1:] if message else ''}.\n")

VENDOR_ID = 0xc0ca
PRODUCT_ID = 0xc001

def parse_arguments():
    parser = CustomParser(
        description="Control power state of individual ports on a selected USB hub",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help="List attached hub controllers")
    parser.add_argument(
        '-s', '--serial-number',
        type=str,
        help="Specify serial number of the hub controller",
        metavar="SERIAL")
    parser.add_argument(
        '-d', '--power-down',
        help="Power off selected port (1-8) or all ports (a)",
        metavar="PORT")
    parser.add_argument(
        '-u', '--power-up',
        help="Power on selected port (1-8) or all ports (a)",
        metavar="PORT")
    parser.add_argument(
        '-g', '--get-state',
        help="Get state of selected port (1-8) or all ports (a)",
        metavar="PORT")
    parser.add_argument(
        '-i','--input',
        nargs='+',
        help="Specify port states in one of the following formats:\n"
             " - xxxxxxxx - set each port to turn ON (1), OFF (0) or leave it unchanged (x)\n"
             " - p s      - set port p (1-8) to state s ON (1), OFF (0)",
        metavar="INPUT")

    args = parser.parse_args()

    arguments = vars(args).copy()
    arguments.pop('serial_number')
    if len(vars(args)) == 0 or all(v is None or v == False for v in arguments.values()):
        if args.serial_number:
            parser.error("Argument -s/--serial-number cannot be used without another argument")
        parser.print_usage()
        exit(1)

    serial = None
    port_set = list(b"\x05xxxxxxxx")
    get_state = None
    send_command = False

    if args.list:
        i = 0
        print("Attached hub controllers:")
        for device in hid.enumerate(VENDOR_ID, PRODUCT_ID):
            i = i + 1
            print(f"{i}. Hub controller with serial number: {device['serial_number']}")

    if args.power_up:
        if args.power_up == 'a':
            for i in range(1, len(port_set)):
                port_set[i] = ord('1')
            send_command = True
        elif args.power_up.isdigit() and 1 <= int(args.power_up) <= 8:
            port_set[int(args.power_up)] = ord('1')
            send_command = True
        else:
            parser.error("argument -u/--power_up expects a number (1-8) or a sign (a)")

    if args.power_down:
        if args.power_down == 'a':
            for i in range(1, len(port_set)):
                port_set[i] = ord('0')
            send_command = True
        elif args.power_down.isdigit() and 1 <= int(args.power_down) <= 8:
            port_set[int(args.power_down)] = ord('0')
            send_command = True
        else:
            parser.error("argument -d/--power_down expects a number (1-8) or a sign (a)")

    if args.get_state:
        if args.get_state == 'a' or args.get_state.isdigit() and 1 <= int(args.get_state) <= 8:
            get_state = args.get_state
            send_command = True
        else:
            parser.error("argument -g/--get_state expects a number (1-8) or a sign (a)")

    if args.input:
        if len(args.input) == 1:
            input_set = args.input[0]
            if len(input_set) == 8:
                for index in range(1, len(port_set)):
                    port_set[index] = ord('1' if input_set[index - 1] == '1' else
                                          '0' if input_set[index - 1] == '0' else 'x')
                send_command = True
            else:
                parser.error("expected 8-character port_set")
        elif len(args.input) == 2:
            port_num, state= args.input
            if 1 <= int(port_num) <= 8  and state in ['0', '1', 'x']:
                port_set[int(port_num)] = ord('1' if state == '1' else
                                              '0' if state == '0' else 'x')
                send_command = True
            else:
                parser.error("expected port number (1-8) with state 0, 1 or x")
        else:
            parser.error("expected either a single 8-character port set or state 0, 1 or x with port number (1-8)")

    if send_command:
        found_devices = 0
        matching_serial = False
        for device in hid.enumerate(VENDOR_ID, PRODUCT_ID):
            found_devices += 1
            serial = device['serial_number']
            if args.serial_number:
                if serial == args.serial_number:
                    matching_serial = True
                    break

        if found_devices == 0:
            send_command = False
            parser.error("not found any hub controllers")
        elif not matching_serial and args.serial_number:
            send_command = False
            parser.error("not found hub controller with matching serial number")
        elif not matching_serial and found_devices > 1:
            send_command = False
            parser.error("found multiple hub controllers, provide serial number or detach unwanted hubs")

    if send_command:
        hid_gpio_hub_set_usb_power(VENDOR_ID, PRODUCT_ID, serial, port_set, get_state)

def hid_gpio_hub_set_usb_power(vid, pid, sn, port_set, get_state):
    path = None
    cmd = bytes(port_set)

    for device in hid.enumerate(vid, pid):
        # print(device)
        if device['serial_number'] == sn:
            path = device['path']
            break

    device = hid.device()
    device.open_path(path)
    device.send_feature_report(cmd)
    feature_report = device.get_feature_report(5, 9)
    #print(feature_report)
    if get_state == 'a':
        for port in range(1, len(feature_report)):
            print(f"Downstream port {port} on hub {sn} "
                  f"is {'ON' if feature_report[port] == 49 
                  else 'OFF' if feature_report[port] == 48 else 'Undefined'}.")
    elif get_state:
        port = feature_report[int(get_state)]
        print(f"Downstream port {int(get_state)} on hub {sn} "
              f"is {'ON' if port == 49 
              else 'OFF' if port == 48 else 'Undefined'}.")
    device.close()

    # Read the flashed versions of hid_gpio and apache-mynewt-core
    # print(device.get_indexed_string(32))
    # print(device.get_indexed_string(33))
    # Read the states of hub ports


def main():
    parse_arguments()


if __name__ == "__main__":
    main()
