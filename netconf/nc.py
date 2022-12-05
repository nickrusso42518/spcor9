#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Using NETCONF with Openconfig YANG models to manage Ethernet
VLANs on a Cisco NX-OS switch via the always-on Cisco DevNet sandbox.
"""

from lxml.etree import fromstring
from ncclient import manager


def main():
    """
    Execution begins here.
    """
    
    # optional: xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"
    host_os_map = {
        #"sandbox-iosxe-latest-1.cisco.com": { "os": "csr", "u": "developer", "snmp_f": '<native><snmp-server/></native>'},
        #"sandbox-iosxr-1.cisco.com": { "os": "iosxr", "u": "admin", "snmp_f": '<snmp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-snmp-agent-cfg"/>'},
        "sandbox-iosxe-latest-1.cisco.com": { "os": "csr", "u": "developer", "ds": "running", "save": save_config_iosxe},
        #"sandbox-iosxr-1.cisco.com": { "os": "iosxr", "u": "admin", "ds": "candidate", "save": save_config_iosxr},
    }

    for host, attr in host_os_map.items():
        # Dictionary containing keyword arguments (kwargs) for connecting
        # via NETCONF. Because SSH is the underlying transport, there are
        # several minor options to set up.
        connect_params = {
            "host": host,
            "username": attr["u"],
            "password": "C1sco12345",
            "hostkey_verify": False,
            "allow_agent": False,
            "look_for_keys": False,
            "device_params": {"name": attr["os"]},
        }

        with open(f"{attr['os']}_snmp.xml", "r") as handle:
            xpayload = handle.read()

        # Unpack the connect_params dict and use them to connect inside
        # of a "with" context manager. The variable "conn" represents the
        # NETCONF connection to the device.
        with manager.connect(**connect_params) as conn:
            print(f"{host}: NETCONF session connected")
            # gc = conn.get_config(source="running", filter=("subtree", attr["snmp_f"]))
            # with open(f"snmp-{attr['os']}.xml", "w") as handle:

            try:
                config_resp = conn.edit_config(target=attr["ds"], config=xpayload)
            except Exception as exc:
                print()
                breakpoint()
                print()
            print(f"{host}: Successfully modifies {attr['ds']}-config")

            # If config and save operations succeed, print "saved" message
            if config_resp.ok and attr["save"](conn).ok:
                print("{host}: Successfully saved config changes")

        print(f"{host}: NETCONF session disconnected\n\n")


def save_config_iosxe(conn):
    save_rpc = '<cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>'
    save_resp = conn.dispatch(fromstring(save_rpc))
    return save_resp

def save_config_iosxr(conn):
    commit_resp = conn.commit()
    return commit_resp


if __name__ == "__main__":
    main()
