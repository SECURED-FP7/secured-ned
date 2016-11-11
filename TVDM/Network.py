import uuid
import commands
from netaddr import *
import random
import subprocess
import copy

class Network(object):
	"""
	Class that contains all the method for the network operation inside the NED
	"""
	def __init__(self, configure):
		self.vlanID = 0
		self.managingNetwork = IPNetwork(configure.MANAGING_NETWORK_ADDRESS)
		self.psaNetwork = IPNetwork(configure.PSA_NETWORK_ADDRESS)
		self.nextPSAIP = 0
		self.userNetwork = IPNetwork(configure.USER_NETWORK_ADDRESS)
		self.userInterfaceNetwork = IPNetwork(configure.USER_INTERFACE_NETWORK_ADDRESS)
		self.nextManageIP = 100
		self.nextUserIP = 1
		self.script_location = configure.SCRIPT_LOCATION
		self.nextTableID = 100
		self.userGatewayAddr = configure.GATEWAY_IP

	def generatePort(self, bridgeName):
		"""
		Generate a port on a bridge
		"""
		generated = str(uuid.uuid4())
		interfaceName = "tap" + generated[:12]
		commands.createNewPort(bridgeName, interfaceName)
		return interfaceName

	def deletePort(self, bridgeName, portName):
		"""
		Delete a port from a bridge
		"""
		commands.deletePort(bridgeName, portName)

	def generateVMPort(self):
		"""
		Generate a port name for a VM
		"""
		generated = str(uuid.uuid4())
		interfaceName = "tap" + generated[:12]
		return interfaceName

	def getNewVLANID(self):
		"""
		Return a new VLAN ID to use
		"""
		self.vlanID = self.vlanID + 1
		return self.vlanID

	def generateRoutingTable(self, netInterface):
		"""
		Generate a new routing table
		"""
		newID = self.nextTableID
		self.nextTableID = self.nextTableID + 1
		commands.generateNewTable(newID, netInterface)
		ipAddr = str(self.userInterfaceNetwork[self.nextUserIP])
		self.nextUserIP = self.nextUserIP + 1
		commands.configureInterface(netInterface, netNs='default')
		commands.configureInterface(netInterface[:11], netNs='default', ipAddr=ipAddr, prefix=str(self.userNetwork.prefixlen), broadcast=str(self.userNetwork.broadcast))
		subprocess.Popen("ip netns exec default iptables -t mangle -A POSTROUTING -p tcp --tcp-flags SYN,RST SYN -o "+netInterface[:11]+" -j TCPMSS --set-mss 1300", shell=True)
		commands.addRoute(table=netInterface, addr=str(self.userNetwork), dev=netInterface[:11], src=ipAddr, netNs="default")
		commands.addRoute(table=netInterface, default=True, addr=self.userGatewayAddr, dev=netInterface[:11], netNs="default")
		return ipAddr

	def configureNewIPOnDHCP(self, mac, token):
		"""
		Configure a new IP on the DHCP
		"""
		self.nextManageIP = self.nextManageIP + 1
		ipAddr = str(self.managingNetwork[self.nextManageIP])
		PSCIp = mac+",id:"+token+"PSC,"+ipAddr
		subprocess.Popen("ip netns exec default bash " + self.script_location +"addIP.sh " + PSCIp, stdout=subprocess.PIPE, shell=True)
		return ipAddr

	def getPSAnewAddress(self):
		"""
		Return a new IP address for a PSA
		"""
		self.nextPSAIP = self.nextPSAIP + 1
		ipAddr = str(self.psaNetwork[self.nextPSAIP])
		return ipAddr

	def generateMACaddress(self):
		"""
		Generate a MAC address
		"""
		mac = [ 0x00, 0x16, 0x3e,
			random.randint(0x00, 0x7f),
			random.randint(0x00, 0xff),
			random.randint(0x00, 0xff)]
		return ':'.join(map(lambda x: "%02x" % x, mac))

	def generateFlow(self, bridgeName, flow):
		"""
		Generate a flow on the bridge
		"""
		newFlow = copy.deepcopy(flow)
		if 'in_port' in flow['match'].keys():
			newFlow['match']['in_port'] = commands.findPort(bridgeName, flow['match']['in_port'])
		if 'output' in flow['action'].keys():
			newFlow['action']['output'] = commands.findPort(bridgeName, flow['action']['output'])
		commands.generateFlow(newFlow, bridgeName)

	def deleteFlow(self, bridgeName, flow):
		"""
		Delete a flow on the bridge
		"""
		newFlow = copy.deepcopy(flow)
		if 'in_port' in flow['match'].keys():
			newFlow['match']['in_port'] = commands.findPort(bridgeName, flow['match']['in_port'])
		commands.deleteFlow(newFlow, bridgeName)
