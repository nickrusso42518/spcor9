#!/usr/bin/env python

"""
Author: Nick Russo
Purpose: Using RESTCONF with IOS-XE specific YANG models to configure NetFlow
policies on a Cisco IOS-XE router via the always-on Cisco DevNet sandbox.
"""

import json
import httpx


def main():
    """
    Execution begins here.
    """

    # The API path below is what the DevNet sandbox uses for API testing,
    # which may change in the future. Be sure to check the IP address as
    # I suspect this changes frequently. See here for more details:
    # https://developer.cisco.com/site/ios-xe
    api_path = "https://ios-xe-mgmt-latest.cisco.com:443/restconf"

    # Create 2-tuple for "basic" authentication using Cisco DevNet credentials.
    # No fancy tokens needed to get basic RESTCONF working on Cisco IOS-XE.
    auth = ("developer", "C1sco12345")

    # Read declarative state with the YANG-modeled, JSON-encoded data to add
    with open("nf_config.json", "r") as handle:
        netflow_data = json.load(handle)

    # Create HTTP headers to indicate YANG/JSON data being sent and received.
    post_headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json, application/yang-data.errors+json",
    }

    # Open long-lived TLS sessions to improve performance. Also, disable
    # certificate validation as sandbox uses self-signed certificates.
    with httpx.Client(verify=False) as client:

        # Issue HTTP PUT request to modify the NetFlow config.
        netflow_add_resp = client.put(
            f"{api_path}/data/Cisco-IOS-XE-native:native/flow",
            headers=post_headers,
            auth=auth,
            json=netflow_data["main_config"],
        )

        # Raise error if request failed; otherwise, do nothing
        netflow_add_resp.raise_for_status()

        # Apply NetFlow to interfaces
        # Issue HTTP PUT request to modify the NetFlow config.
        intf_id = 1
        netflow_path = f"interface/Loopback/{intf_id}/ip/flow"
        netflow_intf_resp = client.put(
            f"{api_path}/data/Cisco-IOS-XE-native:native/{netflow_path}",
            headers=post_headers,
            auth=auth,
            json=netflow_data["intf_apply"],
        )
        netflow_intf_resp.raise_for_status()

        # Save configuration to ensure the changes persist across reboots.
        save_config_resp = client.post(
            f"{api_path}/operations/cisco-ia:save-config",
            headers=post_headers,
            auth=auth,
        )

        # If successful, indicate so, or print error message
        if save_config_resp.is_success:
            print("Saved configuration")
        else:
            print("Save config FAILED")


if __name__ == "__main__":
    main()
