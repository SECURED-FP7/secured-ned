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


#Parameters for the setup script

IP_VERIFIER=10.5.22.228 #To change with the verifier IP
IP_IPSec_Endpoint=10.2.2.254/16 #IP of the IPSec Endpoint should contains the IP Addresses of the user and the PSA avoid to be on the sam net of the user
IP_PSCM=10.2.2.253/16 #IP of the PSCM should be the same of the client
IP_User_NAT=10.2.2.252/16 #IP of the NAT used by the IPSec endpoint
NET_IPSec_CLIENT=10.2.0.0/16 #NET address of the client connected through IPSec

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


#Clean of the used bridge

ovs-vsctl --if-exists del-br brNat
ovs-vsctl --if-exists del-br brData
ovs-vsctl --if-exists del-br brCtl
kill `cat tvdm.pid` `cat pscm.pid`
kill -9 `cat /var/lib/dnsmasq/nedDHCP.pid` > /dev/null 2>&1
kill -9 `cat /var/lib/dnsmasq/userDHCP.pid` > /dev/null 2>&1
killall arping
ip netns del orchNet > /dev/null 2>&1
ip netns del natNs > /dev/null 2>&1
ip netns del ctrlNs > /dev/null 2>&1
ip rule flush
ip rule add from all lookup 220 pref 220
ip rule add from all lookup main pref 32766
ip rule add from all lookup default pref 32767
cp rt_tables /etc/iproute2/rt_tables
ip xfrm policy flush
ip xfrm state flush
iptables -F

#This command will be used to generate the basic bridges and the various  ports

echo "250 tapIPSEC" >> /etc/iproute2/rt_tables
ovs-vsctl add-br brNat
ovs-vsctl add-br brData
ovs-vsctl add-br brCtl
ovs-vsctl add-port brData tapIPSEC -- set Interface tapIPSEC type=internal
ovs-vsctl add-port brNat tapBr -- set Interface tapBr type=internal
ovs-vsctl add-port brNat tapExt -- set Interface tapExt type=internal
ovs-vsctl add-port brData tapPSCM -- set Interface tapPSCM type=internal
ovs-vsctl add-port brData tapNAT -- set Interface tapNAT type=internal
ovs-vsctl add-port brCtl tapOrch -- set Interface tapOrch type=internal
ovs-vsctl add-port brCtl tapDHCP -- set Interface tapDHCP type=internal
ovs-vsctl add-port brCtl tapCtl -- set Interface tapCtl type=internal

#Add default network namespace
mkdir -p /var/run/netns
ln -s /proc/1/ns/net /var/run/netns/default

#Configure the network
ip netns add orchNet
ip netns add natNs
ip link set tapOrch netns orchNet
ip link set tapCtl netns natNs
ip link set tapDHCP netns orchNet
ip link set tapNAT netns natNs
ip link set tapBr netns natNs
ifconfig tapIPSEC $IP_IPSec_Endpoint
ifconfig tapExt 192.168.0.1/24
ip netns exec natNs ifconfig tapNAT $IP_User_NAT
ip netns exec natNs ifconfig tapBr 192.168.0.2/24
ip netns exec orchNet ifconfig tapOrch 192.168.1.1/24
ip netns exec orchNet ifconfig tapDHCP 192.168.1.254/24
ip netns exec natNs ifconfig tapCtl 192.168.1.3/24

#ip netns exec pscmNs
ifconfig tapPSCM $IP_PSCM
ip netns exec orchNet ifconfig lo up
ip netns exec orchNet ip route add default via 192.168.1.3 dev tapOrch
mkdir -p /var/lib/dnsmasq/
echo "" > /var/lib/dnsmasq/nedDHCP.host
ip netns exec orchNet dnsmasq --conf-file=default.conf
ip netns exec natNs route add default gw 192.168.0.1 tapBr
ip route add $NET_IPSec_CLIENT dev tapIPSEC src `echo $IP_IPSec_Endpoint | sed 's/\/[0-9]*[0-9]//'` table tapIPSEC
ip route add default via `echo $IP_User_NAT | sed 's/\/[0-9]*[0-9]//'` dev tapIPSEC table tapIPSEC
ip rule add from $NET_IPSec_CLIENT table tapIPSEC
ip rule add to $NET_IPSec_CLIENT table tapIPSEC

IPSECport=$(ovs-ofctl show brData | grep tapIPSEC | awk '{print $1}' | sed -e 's/\([0-9]\).*/\1/')
NATport=$(ovs-ofctl show brData | grep tapNAT | awk '{print $1}' | sed -e 's/\([0-9]\).*/\1/')

ovs-ofctl del-flows brData
ovs-ofctl add-flow brData priority=1,in_port=$IPSECport,dl_type=0x806,actions=output:$NATport
ovs-ofctl add-flow brData priority=1,in_port=$NATport,dl_type=0x806,actions=output:$IPSECport
ovs-ofctl add-flow brData priority=1,in_port=$IPSECport,dl_type=0x800,actions=output:$NATport
ovs-ofctl add-flow brData priority=1,in_port=$NATport,dl_type=0x800,nw_src=$IP_VERIFIER,actions=output:$IPSECport

ip rule add from $IP_VERIFIER to $NET_IPSec_CLIENT table tapIPSEC pref 1
ip rule add from $NET_IPSec_CLIENT to $IP_VERIFIER table tapIPSEC pref 1


iptables --table nat --append POSTROUTING --out-interface $1 -j MASQUERADE
iptables --append FORWARD --in-interface tapExt -j ACCEPT
iptables -t mangle -A POSTROUTING -p tcp --tcp-flags SYN,RST SYN -o $1 -j TCPMSS --set-mss 1300

ip netns exec natNs iptables --table nat --append POSTROUTING --out-interface tapBr -j MASQUERADE
ip netns exec natNs iptables --append FORWARD --in-interface tapNAT -j ACCEPT
ip netns exec natNs iptables --append FORWARD --in-interface tapCtlExt -j ACCEPT

# Start PSCM and TVDM

ip netns exec orchNet gunicorn -b 192.168.1.1:8080 --pythonpath TVDM mainIPSEC:app -p tvdm.pid -D
gunicorn -b `echo $IP_PSCM | sed 's/\/[0-9]*[0-9]//'`:8080 --pythonpath PSCM main:app -p pscm.pid -D
