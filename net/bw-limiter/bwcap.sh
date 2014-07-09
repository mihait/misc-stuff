#!/bin/bash

# Limit tcp 8081 network traffic to 10Mbit (in/out) on a FE Link 
# using ifb

# Created by Mihai Tianu


modprobe ifb
ip link set dev ifb0 up

tc qdisc del dev eth0 root    1>/dev/null 2>&1
tc qdisc del dev eth0 ingress 1>/dev/null 2>&1
tc qdisc del dev ifb0 root    1>/dev/null 2>&1

[[ "$1" == stop ]] && exit 0

tc qdisc add dev eth0 handle ffff: ingress
tc filter add dev eth0 parent ffff: protocol ip u32 match u32 0 0 action mirred egress redirect dev ifb0

tc qdisc add dev ifb0 root handle 1: htb default 10 r2q 1
tc class add dev ifb0 parent 1: classid 1:1   htb rate 100mbit quantum 1536
tc class add dev ifb0 parent 1:1 classid 1:10 htb rate  90mbit quantum 1536
tc class add dev ifb0 parent 1:1 classid 1:11 htb rate  10mbit quantum 1536

tc filter add dev ifb0 parent 1: protocol ip prio 16 u32 match ip dport 8081 0xffff match ip protocol 0x6 0xff flowid 1:11
tc qdisc add dev ifb0 parent 1:10 sfq perturb 10
tc qdisc add dev ifb0 parent 1:11 sfq perturb 10


tc qdisc add dev eth0 root handle 1: htb default 11 r2q 1
tc class add dev eth0 parent 1: classid 1:1   htb rate 100mbit quantum 1536
tc class add dev eth0 parent 1:1 classid 1:10 htb rate  90mbit quantum 1536
tc class add dev eth0 parent 1:1 classid 1:11 htb rate  10mbit quantum 1536

tc filter add dev eth0 parent 1: protocol ip prio 16 u32 match ip sport 8081 0xffff match ip protocol 0x6 0xff flowid 1:11
tc qdisc  add dev eth0 parent 1:10 sfq perturb 10
tc qdisc  add dev eth0 parent 1:11 sfq perturb 10




