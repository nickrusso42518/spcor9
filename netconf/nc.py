#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Using NETCONF with Openconfig YANG models to manage Ethernet
VLANs on a Cisco NX-OS switch via the always-on Cisco DevNet sandbox.
"""

import json
import xmltodict
from lxml.etree import tostring, fromstring
from ncclient import manager
from ncclient.operations import RaiseMode


def main():
    """
    Execution begins here.
    """
    
    # optional: xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native"
    host_os_map = {
        "sandbox-iosxe-latest-1.cisco.com": { "os": "csr", "u": "developer", "snmp_f": '<native><snmp-server/></native>'},
        "sandbox-iosxr-1.cisco.com": { "os": "iosxr", "u": "admin", "snmp_f": '<snmp xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-snmp-agent-cfg"/>'},
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
            gc = conn.get_config(source="running", filter=("subtree", attr["snmp_f"]))
            with open(f"snmp-{attr['os']}.xml", "w") as handle:
                pretty_xml = gc.xml
                handle.write(pretty_xml)
                print(pretty_xml)
            continue

            # Perform the update, and if success, print a message
            config_resp = config_snmp(conn, "snmp_config.json")

            # If config and save operations succeed, print "saved" message
            if config_resp.ok and save_config_nxos(conn).ok:
                print("Successfully saved running-config to startup-config")

        print(f"{host}: NETCONF session disconnected")


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
