import subprocess


def addIPrule(table, addressFrom=None, addressTo=None, pref=None, netns=None):
	'''
	Add an IP rule for a table
	'''
	command = ""
	if netns is not None:
		command = command + "ip netns exec " + netns + " ip rule add"
	else:
		command = command + "ip rule add"
	if addressFrom is not None:
		command = command + " from " + addressFrom
	if addressTo is not None:
		command = command + " to " + addressTo
	command = command + " table " + table
	if pref is not None:
		command = command + " pref " + str(pref)
	subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

def delIPrule(table, addressFrom=None, addressTo=None, pref=None, netns=None):
	'''
	Add an IP rule for a table
	'''
	command = ""
	if netns is not None:
		command = command + "ip netns exec " + netns + " ip rule del"
	else:
		command = command + "ip rule del"
	if addressFrom is not None:
		command = command + " from " + addressFrom
	if addressTo is not None:
		command = command + " to " + addressTo
	command = command + " table " + table
	if pref is not None:
		command = command + " pref " + str(pref)
	subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

def createNewPort(bridgeName, portName, netNs='default'):
	'''
	Create a new interface on a bridge
	'''
	subprocess.Popen("ip netns exec " + netNs + " ip link add " + portName + " type veth peer name " + portName[:11], stdout=subprocess.PIPE, shell=True).wait()
	subprocess.Popen("ovs-vsctl add-port " + bridgeName + " " + portName, stdout=subprocess.PIPE, shell=True).wait()

def deletePort(bridgeName, portName, netNs='default'):
	'''
	Create a new interface on a bridge
	'''
        subprocess.Popen("ovs-vsctl del-port " + bridgeName + " " + portName, stdout=subprocess.PIPE, shell=True)
	subprocess.Popen("ip netns exec " + netNs + " ip link del " + portName, stdout=subprocess.PIPE, shell=True)

def configureInterface(portName, netNs=None, ipAddr=None, addToNetNs=False, prefix=None, broadcast=None):
	'''
	Configure an interface with an IP address and insert into a specific network namespace
	'''
	if addToNetNs and netNs is not None:
		subprocess.Popen("ip link set " + portName + " netns " + netNs, stdout=subprocess.PIPE, shell=True).wait()
	if ipAddr is not None:
		if netNs is not None:
			subprocess.Popen("ip netns exec "+ netNs +" ip addr add " + ipAddr + "/"+prefix+" broadcast "+broadcast+ " dev " + portName, stdout=subprocess.PIPE, shell=True).wait()
		else:
			subprocess.Popen("ip addr add " + ipAddr + "/"+prefix+" broadcast "+broadcast+" dev " + portName, stdout=subprocess.PIPE, shell=True).wait()

	if netNs is not None:
		subprocess.Popen("ip netns exec "+ netNs +" ip link set " + portName + " up", stdout=subprocess.PIPE, shell=True).wait()
	else:
		subprocess.Popen("ip link set " + portName + " up", stdout=subprocess.PIPE, shell=True).wait()

def generateNewTable(tableID, interface):
	'''
	Generate a new routing table
	'''
	subprocess.Popen("echo \""+str(tableID)+" "+interface+"\" >> /etc/iproute2/rt_tables", shell=True)

def addRoute(table, addr, dev, default=False, src=None, netNs=None):
	'''
	Add a route on the given routing table
	'''
	command = ""
	if netNs is not None:
		command = command + "ip netns exec " + netNs + " ip route add"
	else:
		command = command + "ip route add"
	if default:
		command = command + " default via"
	command = command + " " + addr + " dev " + dev
	if src is not None:
		command = command + " src " + src
	command = command + " table " + table
	subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

def generateFlow(flowJSON, bridgeName):
	'''
	Generates a flow on a bridge
	INPUT JSON:
	{
	priority: flow priority
	match: {map of match key->value}
	action: {map of actions key->value}
	}
	'''
	command = "ovs-ofctl add-flow " + bridgeName + " "
	noFirst = False
	if 'priority' in flowJSON.keys():
		priority = flowJSON['priority']
	else:
		priority = 1
	command = command + "priority=" + str(priority)
	noFirst = True
	for match in flowJSON['match'].keys():
		if noFirst:
			command = command + ","
		command = command + match + "=" + flowJSON['match'][match]
		noFirst = True
	command = command + ",actions="
	noFirst = False
	for action in flowJSON['action'].keys():
		if noFirst:
			command = command +","
		command = command + action + ":" + flowJSON['action'][action]
		noFirst = True
	subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

def deleteFlow(flowJSON, bridgeName):
	'''
	Deletes a flow on a bridge
	INPUT JSON:
	{
	match: {map of match key->value}
	}
	'''
	command = "ovs-ofctl del-flows " + bridgeName + " "
	noFirst = False
	for match in flowJSON['match'].keys():
		if noFirst:
			command = command + ","
		command = command + match + "=" + flowJSON['match'][match]
		noFirst = True
	subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

def findPort(bridgeName, portName):
	'''
	Find port number on a bridge
	'''
	proc = subprocess.Popen("ovs-ofctl show " + bridgeName +" | grep " + portName, stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	return out.split("(").pop(0).split().pop(0)
