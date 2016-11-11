#! /bin/bash

echo $1 >> /var/lib/dnsmasq/nedDHCP.host
#ip netns exec orchNet service dhcpd restart
pid=$(cat /var/lib/dnsmasq/nedDHCP.pid)
kill -1 $pid
#killall dnsmasq
#ip netns exec orchNet dnsmasq --no-hosts --no-resolv --strict-order --log-dhcp --dhcp-range=192.168.1.100,192.168.1.200 --interface=tapDHCP --except-interface=lo --dhcp-hostsfile=/home/ned/pythonScript/Orchestrator/hosts
