#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Using NETCONF with Openconfig YANG models to manage Ethernet
VLANs on a Cisco NX-OS switch via the always-on Cisco DevNet sandbox.
"""

import json
import xmltodict
from lxml.etree import fromstring
from ncclient import manager
from ncclient.operations import RaiseMode


def main():
    """
    Execution begins here.
    """
    
    host_os_map = {
        "R1": "csr",  # iosxe for physical devices
        "R2": "iosxr",
    }
    
    for host, os in host_os_map.items()
        # Dictionary containing keyword arguments (kwargs) for connecting
        # via NETCONF. Because SSH is the underlying transport, there are
        # several minor options to set up.
        connect_params = {
            "host": host,
            "username": "developer",
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
            print("NETCONF session connected")

            # Perform the update, and if success, print a message
            config_resp = config_snmp(conn, "snmp_config.json")

            # If config and save operations succeed, print "saved" message
            if config_resp.ok and save_config_nxos(conn).ok:
                print("Successfully saved running-config to startup-config")

    print("NETCONF session disconnected")


def config_snmp(conn, filename):
    """
    Updates switchports with new config based on YAML file. Expects that the
    NETCONF connection is already open and that all data is valid. Feel
    free to add more data validation here as a challenge.
    """

    with open(filename, "r") as handle:
        snmp_config = json.load(handle)

    # Assemble the XML payload by "unparsing" the JSON dict (JSON --> XML)
    xpayload = xmltodict.unparse(snmp_config)
    config_resp = conn.edit_config(target="running", config=xpayload)
    print("Successfully updated running-config")

    if save_config_nxos(conn).ok:
        print("Successfully saved running-config to startup-config")

    return config_resp


def save_config_nxos(conn):
    """
    Save config on Cisco NX-OS is complex and requires a custom RPC.
    Reference the NX-OS programmability documentation for further details.
    """

    save_xmlns = "http://cisco.com/ns/yang/cisco-nx-os-device"
    save_rpc = f"""
        <copy_running_config_src xmlns="{save_xmlns}">
             <startup-config/>
        </copy_running_config_src>
    """
    save_resp = conn.dispatch(fromstring(save_rpc))
    return save_resp


if __name__ == "__main__":
    main()
