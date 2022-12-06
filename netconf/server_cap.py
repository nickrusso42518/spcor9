#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Using NETCONF with Openconfig YANG models to manage Ethernet
VLANs on a Cisco NX-OS switch via the always-on Cisco DevNet sandbox.
"""

from ncclient import manager


def main():
    """
    Execution begins here.
    """
    
    # Identify the OS of each host so ncclient can properly connect
    host_os_map = {
        "sandbox-iosxe-latest-1.cisco.com": "csr",
        "sandbox-iosxr-1.cisco.com": "iosxr",
    }

    # TEMP
    LOGIN = {"csr": "developer", "iosxr": "admin"}

    for host, os in host_os_map.items():
        # Dictionary containing keyword arguments (kwargs) for connecting
        # via NETCONF. Because SSH is the underlying transport, there are
        # several minor options to set up.
        connect_params = {
            "host": host,
            "username": LOGIN[os],
            "password": "C1sco12345",
            "hostkey_verify": False,
            "allow_agent": False,
            "look_for_keys": False,
            "device_params": {"name": os},
        }

        # Unpack the connect_params dict and use them to connect inside
        # of a "with" context manager. The variable "conn" represents the
        # NETCONF connection to the device.
        with manager.connect(**connect_params) as conn:
            print(f"{host}: NETCONF session connected")

            # Create new files for each host to enumerate server capabilities.
            # Then, use Linux tools like grep to search for items of interest.
            with open (f"{host}_scap.txt", "w") as handle:
                handle.write("\n".join(conn.server_capabilities))

        # Indicate disconnection when "with" context ends
        print(f"{host}: NETCONF session disconnected\n")


if __name__ == "__main__":
    main()
