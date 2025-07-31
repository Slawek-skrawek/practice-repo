import argparse
import hid
import sys

VENDOR_ID = 0xc0ca
PRODUCT_ID = 0xc001

class CustomParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(
            description="Control power state of individual ports on a selected USB hub",
            formatter_class=argparse.RawTextHelpFormatter)
        self.add_argument(
            '-l', '--list',
            action='store_true',
            help="List attached hub controllers",
            dest="list")
        self.add_argument(
            '-s', '--serial-number',
            type=str,
            help="Specify serial number of the hub controller",
            metavar="SERIAL",
            dest="serial")
        self.add_argument(
            '-d', '--power-down',
            help="Power off selected port (1-8) or all ports (a)",
            metavar="PORT",
            dest="pow_down")
        self.add_argument(
            '-u', '--power-up',
            help="Power on selected port (1-8) or all ports (a)",
            metavar="PORT",
            dest="pow_up")
        self.add_argument(
            '-g', '--get-state',
            help="Get state of selected port (1-8) or all ports (a)",
            metavar="PORT",
            dest="get_state")
        self.add_argument(
            '-p', '--port-set',
            help="Specify ports states in the following format:\n"
                 " - xxxxxxxx - set each port to turn ON (1), OFF (0) or leave it unchanged (x)\n",
            metavar="PORT_SET",
            dest="port_set")

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f"Error: {message[0].upper() + message[1:] if message else ''}.\n")

    def parse(self, arg_ns=None):
        # args = self.parse_args(None, arg_ns)
        return self.parse_args(namespace=arg_ns)


class HubController:
    def __init__(self):
        self.parser = CustomParser()
        self.args = None
        self.vid = VENDOR_ID
        self.pid = PRODUCT_ID
        self.serial = None
        self.hub = None
        self.port_set = list(b"\x05xxxxxxxx")

    @staticmethod
    def list_hubs():
        i = 0
        hubs = hid.enumerate(VENDOR_ID, PRODUCT_ID)
        print("Attached hub controllers:")
        for hub in hubs:
            i = i + 1
            print(f"{i}. Hub controller with serial number: {hub['serial_number']}")
        if i == 0:
            print("No attached hub controllers found.")
        return hubs

    def parse_arguments(self, cli_args=None):
        self.args = self.parser.parse_args(cli_args)
        self.serial = self.args.serial

    def find_hub(self):
        found_hubs = 0
        matching_serial = False
        for hub in hid.enumerate(self.vid, self.pid):
            found_hubs += 1
            ser = hub['serial_number']
            if self.serial:
                if ser == self.serial:
                    self.hub = hub
                    matching_serial = True
                    break
            else:
                self.hub = hub
                self.serial = ser

        if found_hubs == 0:
            self.parser.error("not found any hub controllers")
        elif not matching_serial and self.args and self.args.serial:
            self.parser.error("not found hub controller with matching serial number")
        elif not matching_serial and found_hubs > 1:
            self.parser.error("found multiple hub controllers, provide serial number or detach unwanted hubs")

    def current_port_state(self):
        port = self.args.get_state
        if port == 'a' or port.isdigit() and 1 <= int(port) <= 8:
            path = self.hub['path']
            if path:
                hub = hid.device()
                hub.open_path(path)
                feature_report = hub.get_feature_report(5, 9)
                hub.close()
                if port == 'a':
                    for port in range(1, len(feature_report)):
                        port_state = feature_report[port]
                        print(f"Downstream port {port} on hub {self.serial} "
                              f"is {'ON' if port_state == 49
                              else 'OFF' if port_state == 48 else 'Undefined'}.")
                elif port:
                    port_state = feature_report[int(port)]
                    print(f"Downstream port {int(port)} on hub {self.serial} "
                          f"is {'ON' if port_state == 49
                          else 'OFF' if port_state == 48 else 'Undefined'}.")
            else:
                self.parser.error("hub controller not found")
        else:
            self.parser.error("argument -g/--get_state expects a number (1-8) or a sign (a)")

    def set_cmd_ports(self, port, switch):
        if type(port) is str and port.isdigit():
            port = int(port)
        if port == 'a':
            for i in range(1, len(self.port_set)):
                self.port_set[i] = ord('1' if switch else '0')
        elif port and 1 <= port <= 8:
            self.port_set[int(port)] = ord('1' if switch else '0')
        else:
            self.parser.error("argument -u/--power_up | -d/--power_down "
                              "expects a number (1-8) or a sign (a)")

    def set_cmd_port_set(self, port_set):
        if len(port_set) == 8:
            for index in range(1, len(self.port_set)):
                self.port_set[index] = ord('1' if port_set[index - 1] == '1' else
                                      '0' if port_set[index - 1] == '0' else 'x')
        else:
            self.parser.error("expected 8-character port_set")

    def set_usb_power(self):
        path = self.hub['path']
        cmd = bytes(self.port_set)
        if path:
            hub = hid.device()
            hub.open_path(path)
            hub.send_feature_report(cmd)
            hub.close()
        else:
            self.parser.error("hub controller not found")

    def set_power(self, port, state):
        self.set_cmd_ports(port, state)
        self.set_usb_power()

    def run(self):
        self.parse_arguments()

        arguments = vars(self.args).copy()
        arguments.pop('serial')
        if len(vars(self.args)) == 0 or all(v is None or v == False for v in arguments.values()):
            if self.serial:
                self.parser.error("Argument -s/--serial-number has no usage without another argument")
            self.parser.print_usage()
            exit(1)

        if self.args.list:
            self.list_hubs()

        if self.args.port_set or self.args.pow_up or self.args.pow_down or self.args.get_state:
            self.find_hub()

        if self.args.port_set:
            self.set_cmd_port_set(self.args.port_set)
        if self.args.pow_up:
            self.set_cmd_ports(self.args.pow_up, True)
        if self.args.pow_down:
            self.set_cmd_ports(self.args.pow_down, False)

        if self.args.pow_up or self.args.pow_down or self.args.port_set :
            self.set_usb_power()
        if self.args.get_state:
            self.current_port_state()


def hid_gpio_hub_set_usb_power(vid, pid, sn, port_set):
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
    print(device.get_feature_report(5, 9))
    device.close()

    # Read the flashed versions of hid_gpio and apache-mynewt-core
    # print(device.get_indexed_string(32))
    # print(device.get_indexed_string(33))
    # Read the states of hub ports


def main():
    hubcontroller = HubController()
    hubcontroller.run()


if __name__ == "__main__":
    main()
