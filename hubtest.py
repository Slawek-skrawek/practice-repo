import argparse
import hid

def parse_args():
    parser = argparse.ArgumentParser(description="Turn on and off chosen ports on a HUB",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("input",
                        nargs='+',
                        help="Either:\n"
                             " - xxxxxxxx - set which ports to turn ON-1/OFF-0 or leave untouched-x\n"
                             " - s p      - set chosen port (p) to turn ON-1/OFF-0 (s)")

    args = parser.parse_args()

    if len(args.input) == 1:
        port_set = args.input[0]
        if len(port_set) == 8:
            return 'port_set', port_set
        else:
            parser.error("Expected 8-character port_set")
    elif len(args.input) == 2:
        switch, port_num = args.input
        if 1 <= int(port_num) <= 8  and switch in ['0', '1', 'x']:
            return 'port_choice', [port_num, switch]
        else:
            parser.error("Expected switch 0, 1 or x and port number <1,8>.")
    else:
        parser.error("Provide either a single ports set or chosen port number with ON/OFF.")


def hid_gpio_hub_set_usb_power(vid, pid):
    kind, value = parse_args()
    path = None
    cmd = b"\x05xxxxxxxx"
    # cmd = b"\x05"
    # cmd = b"\x0500000000"
    # index = int(port)

    # if 1 <= index <= len(cmd) - 1:
    #     cmd_list = list(cmd)
    #     cmd_list[index] = ord('1' if on else '0')
    #     cmd = bytes(cmd_list)

    cmd_list = list(cmd)
    if kind == 'port_set':
        for index in range(1, len(cmd)):
            cmd_list[index] = ord('1' if value[index - 1] == '1' else
                                  '0' if  value[index - 1] == '0' else 'x')
        cmd = bytes(cmd_list)
    elif kind == 'port_choice':
        cmd_list[int(value[0])] = ord('1' if value[1] == '1' else
                                   '0' if value[1] == '0' else 'x')
        # cmd_list[int(value[0])] = ord(value[1])
        cmd = bytes(cmd_list)
    else:
        raise ValueError(f"Unknown port number {value}")

    for device in hid.enumerate(vid, pid):
        print(device)
        path = device['path']

    device = hid.device()
    device.open_path(path)
    device.send_feature_report(cmd)
    device.close()

    # Read the flashed versions of hid_gpio and apache-mynewt-core
    # print(device.get_indexed_string(32))
    # print(device.get_indexed_string(33))
    # Read the states of hub ports
    # print(device.get_feature_report(5, 9))


def main():
    hid_gpio_hub_set_usb_power(0xc0ca, 0xc001)


if __name__ == "__main__":
    main()
