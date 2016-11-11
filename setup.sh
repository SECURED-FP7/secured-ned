#!/bin/bash

# File:				setup.sh 
#
# Description:		
#					Script to set the environment to run the basic NED prototype software.
#					It instatiates virtual switches, setup the network configuration of the virtual interfaces,
#					sets the appropriate flows in the switches, then it finally starts up the PSCM and TVDM.
#					Run this as administrator!
#
# Params:			
#					- $1 physical network interface with internet access
#                   - $2 [opt] interface to which physical devices are connected
#
# Authors:			Roberto Bonafiglia, Francesco Ciaccia

# It requires to give the name of the port connected to the internet
[ $# -eq 0 ] && { echo "Usage: $0 internetPort [externalClientsPort]"; exit 1; }

# Integrity check for provided interfaces names
ifconfig | grep -q $1
[ $? -ne 0 ] && { echo "Interface $1 not found"; exit 1; }

if [ $# -eq 2 ] 
then
	ifconfig | grep -q $2
	[ $? -ne 0 ] && { echo "Interface $2 not found"; exit 1; }
fi 

#Reset the environment
for i in $(virsh list --all | awk '{print $2}' | tail -n +3)
	do
		virsh destroy $i
		virsh undefine $i
	done

ovs-vsctl --if-exists del-br brNat
ovs-vsctl --if-exists del-br brUsers
ovs-vsctl --if-exists del-br brData
ovs-vsctl --if-exists del-br brCtl
kill `cat tvdm.pid` `cat pscm.pid`
#kill -s SIGKILL `cat /var/lib/dnsmasq/nedDHCP.pid` #> /dev/null 2>&1
kill -9 `cat /var/lib/dnsmasq/nedDHCP.pid` > /dev/null 2>&1
#kill -s SIGKILL `cat /var/lib/dnsmasq/userDHCP.pid`
kill -9 `cat /var/lib/dnsmasq/userDHCP.pid` > /dev/null 2>&1
ip netns del orchNet > /dev/null 2>&1
ip netns del pscmNs > /dev/null 2>&1
ip netns del dhcpNs > /dev/null 2>&1
ip netns del natNs > /dev/null 2>&1
ip netns del ctrlNs > /dev/null 2>&1

#This command will be used to generate the basic bridges and the various  ports

ovs-vsctl add-br brNat
ovs-vsctl add-br brUsers
ovs-vsctl add-br brData
ovs-vsctl add-br brCtl
ovs-vsctl add-port brData tapIPSEC -- set Interface tapIPSEC type=patch options:peer=patch_tapIPSEC
ovs-vsctl add-port brUsers patch_tapIPSEC -- set Interface patch_tapIPSEC type=patch options:peer=tapIPSEC
ovs-vsctl add-port brNat tapBr -- set Interface tapBr type=internal
ovs-vsctl add-port brNat tapExt -- set Interface tapExt type=internal
#ovs-vsctl add-port brData tapIPSEC -- set Interface tapIPSEC type=internal
ovs-vsctl add-port brData tapPSCM -- set Interface tapPSCM type=internal
ovs-vsctl add-port brData tapNAT -- set Interface tapNAT type=internal
ovs-vsctl add-port brCtl tapOrch -- set Interface tapOrch type=internal
ovs-vsctl add-port brCtl tapDHCP -- set Interface tapDHCP type=internal
ovs-vsctl add-port brCtl tapCtl -- set Interface tapCtl type=internal

mkdir -p /var/run/netns
ln -s /proc/1/ns/net /var/run/netns/default
#Configure the network
ip netns add orchNet
ip netns add pscmNs
ip netns add natNs
ip link set tapOrch netns orchNet
ip link set tapCtl netns natNs
ip link set tapDHCP netns orchNet
ip link set tapPSCM netns pscmNs
ip link set tapNAT netns natNs
ip link set tapBr netns natNs
#ifconfig tapIPSEC 10.2.2.254/24
ifconfig tapExt 192.168.0.1/24
ip netns exec natNs ifconfig tapNAT 10.2.2.252/16
ip netns exec natNs ifconfig tapBr 192.168.0.2/24
ip netns exec orchNet ifconfig tapOrch 192.168.1.1/24
ip netns exec orchNet ifconfig tapDHCP 192.168.1.254/24
ip netns exec natNs ifconfig tapCtl 192.168.1.3/24
ip netns exec pscmNs ifconfig tapPSCM 10.2.2.253/24
ip netns exec orchNet ifconfig lo up
ip netns exec orchNet ip route add default via 192.168.1.3 dev tapOrch
ip netns exec pscmNs ifconfig lo up
mkdir -p /var/lib/dnsmasq/
echo "" > /var/lib/dnsmasq/nedDHCP.host
ip netns exec orchNet dnsmasq --conf-file=default.conf
ip netns exec natNs route add default gw 192.168.0.1 tapBr
#ip route add 10.2.2.0/24 dev tapIPSEC src 10.2.2.254 table tapIPSEC
#ip route add default via 10.2.2.252 dev tapIPSEC table tapIPSEC
#ip rule add from 10.2.2.0/24 table tapIPSEC
#ip rule add to 10.2.2.0/24 table tapIPSEC

IPSECport=$(ovs-ofctl show brData | grep tapIPSEC | awk '{print $1}' | sed -e 's/\([0-9]\).*/\1/')
NATport=$(ovs-ofctl show brData | grep tapNAT | awk '{print $1}' | sed -e 's/\([0-9]\).*/\1/')
PSCMport=$(ovs-ofctl show brData | grep tapPSCM | awk '{print $1}' | sed -e 's/\([0-9]\).*/\1/')
ovs-ofctl del-flows brData
ovs-ofctl add-flow brData priority=1,in_port=$IPSECport,dl_type=0x806,actions=output:$NATport
ovs-ofctl add-flow brData priority=1,in_port=$NATport,dl_type=0x806,actions=output:$IPSECport
#ovs-ofctl add-flow brData priority=1,in_port=$IPSECport,dl_type=0x800,actions=output:$NATport
#ovs-ofctl add-flow brData priority=1,in_port=$NATport,dl_type=0x800,actions=output:$IPSECport

# flows to reach PSCM
ovs-ofctl add-flow brData priority=5,in_port=$IPSECport,dl_type=0x800,nw_dst=10.2.2.253,actions=output:$PSCMport
ovs-ofctl add-flow brData priority=5,in_port=$IPSECport,dl_type=0x806,nw_dst=10.2.2.253,actions=output:$PSCMport
ovs-ofctl add-flow brData priority=5,in_port=$PSCMport,dl_type=0x800,actions=output:$IPSECport
ovs-ofctl add-flow brData priority=5,in_port=$PSCMport,dl_type=0x806,actions=output:$IPSECport

iptables --table nat --append POSTROUTING --out-interface $1 -j MASQUERADE
iptables --append FORWARD --in-interface tapExt -j ACCEPT

ip netns exec natNs iptables --table nat --append POSTROUTING --out-interface tapBr -j MASQUERADE
ip netns exec natNs iptables --append FORWARD --in-interface tapNAT -j ACCEPT
ip netns exec natNs iptables --append FORWARD --in-interface tapCtlExt -j ACCEPT

# Start PSCM and TVDM

ip netns exec orchNet gunicorn -b 192.168.1.1:8080  --pythonpath TVDM main:app -p tvdm.pid -D
ip netns exec pscmNs gunicorn -b 10.2.2.253:8080 --pythonpath PSCM main:app -p pscm.pid -D


# Integration testbed setup

# Test user namespace including a DHCP for externally connected devices
# Creates a separate namespace with an IP in the 10.2.2.0/24 addressing space.
# The namespace is then connected to the brUsers switch. 
# If a physical interface is passed as second parameter it is plugged in the brUsers so
# that clients can connect to the DHCP server

ip netns add dhcpNs
ip netns exec dhcpNs ip link set dev lo up
ovs-vsctl add-port brUsers usrDHCP_port -- set Interface usrDHCP_port type=internal
ip link set usrDHCP_port netns dhcpNs
ip netns exec dhcpNs ip link set dev usrDHCP_port up
ip netns exec dhcpNs ip addr add 10.2.2.128/24 dev usrDHCP_port


if [ $# -eq 2 ] 
then
	# this means testing clients will be connected to a physical interface of the machine
	# the physical interface is plugged into the brUsers aggregation bridge
	ifconfig $2 0.0.0.0 					# set the external interface as L2
	ovs-vsctl add-port brUsers $2 			# add port to virtual switch
	
	# Users' DHCP assigns IPs in the 10.2.2.0/25 addressing space
	# DG tapNAT = 10.2.2.252
	# DNS Google = 8.8.8.8
	echo "" > /var/lib/dnsmasq/userDHCP.host
	ip netns exec dhcpNs dnsmasq --conf-file=userNet.conf
fi

# Test control plane namespace
# Creates a separate namespace with an IP in the 192.168.1.0/24 addressing space.
# The namespace is then connected to the brCtl switch. 
ip netns add ctrlNs
ip netns exec ctrlNs ip link set dev lo up
ovs-vsctl add-port brCtl ctrl_port -- set Interface ctrl_port type=internal
ip link set ctrl_port netns ctrlNs
ip netns exec ctrlNs ip link set dev ctrl_port up
ip netns exec ctrlNs ip addr add 192.168.1.250/24 dev ctrl_port


#Download PSAs of users that are not in the NED from the PSAR
#python download_images.py

