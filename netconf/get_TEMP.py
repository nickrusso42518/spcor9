#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Using NETCONF with Openconfig YANG models to manage Ethernet
VLANs on a Cisco NX-OS switch via the always-on Cisco DevNet sandbox.
"""

from lxml.etree import fromstring
from ncclient import manager
from ncclient.operations import RPCError


def main():
    """
    Execution begins here.
    """

    # Include OS, target datastore, and save_config function reference per host
    host_os_map = {
        "sandbox-iosxe-latest-1.cisco.com": {
            "os": "csr",
            "u": "developer",
            "ds": "running",
            "save": save_config_iosxe,
        },
        "sandbox-iosxr-1.cisco.com": {
            "os": "iosxr",
            "u": "admin",
            "ds": "candidate",
            "save": save_config_iosxr,
        },
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


        # Unpack the connect_params dict and use them to connect inside
        # of a "with" context manager. The variable "conn" represents the
        # NETCONF connection to the device.
        with manager.connect(**connect_params) as conn:
            print(f"{host}: NETCONF session connected")
            get_resp = conn.get_config(source="running")
            with open(f"{host}.txt", "w") as handle:
                handle.write(get_resp.xml)

        # Indicate disconnection when "with" context ends
        print(f"{host}: NETCONF session disconnected\n")


def save_config_iosxe(conn):
    """
    Copy running-config to startup-config on IOS-XE devices. This requires
    a custom RPC specific to IOS-XE.
    """

    save_rpc = '<cisco-ia:save-config xmlns:cisco-ia="http://cisco.com/yang/cisco-ia"/>'
    save_resp = conn.dispatch(fromstring(save_rpc))
    return save_resp


def save_config_iosxr(conn):
    """
    Commit candidate-config to running-config on IOS-XR devices. This is a
    standard NETCONF RPC with nothing special required.
    """

    commit_resp = conn.commit()
    return commit_resp


if __name__ == "__main__":
    main()
