#!/bin/bash
# Small script to avoid typing these long commands

pyang_path="yang/vendor/cisco/xe/1741"

echo "Producing flow containers to augment native"
pyang --format tree --path $pyang_path \
  --output data_ref/xe_flow.txt \
  $pyang_path/Cisco-IOS-XE-flow.yang

# Option 1: Target interfaces, view source groupings
echo "Producing interface groupings"
pyang --format tree --path $pyang_path \
  --output data_ref/xe_intf.txt --tree-print-groupings \
  $pyang_path/Cisco-IOS-XE-interfaces.yang

# Option 2: Target native, filter interfaces from hierarchy
echo "Producing interface containers from native"
pyang --format tree --path $pyang_path \
  --output data_ref/xe_native.txt \
  --tree-path /native/interface/GigabitEthernet \
  $pyang_path/Cisco-IOS-XE-native.yang
