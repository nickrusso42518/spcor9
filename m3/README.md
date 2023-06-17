# Configuring NetFlow with RESTCONF
Reference the YANG trees displayed in module 2. The `data_ref/` directory
contains an example NetFlow capture using Python's `netflow` package.

Noteworthy config:
```
alias exec nf show flow monitor FLOW_MONITOR_IPV4 cache format table
flow record FLOW_RECORD_IPV4
 match ipv4 destination address
 match ipv4 dscp
 match ipv4 source address
 match transport destination-port
 match transport source-port
 collect counter bytes
 collect counter packets
flow exporter FLOW_EXPORTER
 destination 192.168.5.22
 source Loopback0
 transport udp 2055
flow monitor FLOW_MONITOR_IPV4
 exporter FLOW_EXPORTER
 record FLOW_RECORD_IPV4
interface GigabitEthernet2.3078
 ip flow monitor FLOW_MONITOR_IPV4 input
```

Collection:
```
python -m netflow.collector -p 2055 -D
ctrl+c to stop
gunzip (filename).gz
```
