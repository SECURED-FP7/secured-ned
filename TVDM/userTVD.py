import commands
from manifestManager import ManifestManager

class UserTVD(object):
	'''
	User TVD class in case of IPSEC NED configuration
	'''

	def __init__(self, userName, vlanID, networkManager, computeManager, config, logger):
		self.logger = logger
		self.networkManager = networkManager
		userInterface = self.networkManager.generatePort('brData')
                self.interfaceIP = self.networkManager.generateRoutingTable(userInterface)
		self.userName = userName
		self.userIP = []
		self.userInterface = userInterface
		self.vlanID = vlanID
		self.pscAddr = None
		self.psc = None
		self.generatedFlows = []
		self.computeManager = computeManager
		self.config = config
		self.psaList = []
		self.psaIPaddresses = {}
		self.manifestManager = ManifestManager(config)

	def addNewIP(self, newIP):
	        '''
            	Add a new machine on the TVD with the given IP
	        '''
		self.userIP.append(newIP)
		commands.addIPrule(table=self.userInterface, addressFrom=newIP+"/32", pref=2, netns="default")
		commands.addIPrule(table=self.userInterface, addressTo=newIP+"/32", pref=2, netns="default")

	def delUserIP(self, newIP):
	        '''
        	Remove the flow for the given IP
        	'''
		self.userIP.remove(newIP)
		commands.delIPrule(table=self.userInterface, addressFrom=newIP+"/32", pref=2, netns="default")
		commands.delIPrule(table=self.userInterface, addressTo=newIP+"/32", pref=2, netns="default")

	def setPSC(self, newPSC, pscAddr):
                '''
	        Configure the PSC of the TVD
	        '''
		self.psc = newPSC
		self.pscAddr = pscAddr
		self.logger.info("User " + self.userName + " PSC addr: "+ pscAddr)

	def generatePSCflows(self):
        	'''
	        Generete the flow for the PSC
        	'''
		flow = {}
		flow['priority'] = "10"
		match = {}
		match['in_port'] = self.userInterface
		match['dl_type'] = "0x0806"
		match['nw_dst'] = self.config.PSC_DP_IF_IP
		flow['match'] = match
		action = {}
		action['output'] = self.psc['interfaces'][2]['name']
		flow['action'] = action
		self.networkManager.generateFlow('brData', flow)
		self.generatedFlows.append(flow)

		flow = {}
		flow['priority'] = "10"
		match = {}
		match['in_port'] = self.userInterface
		match['dl_type'] = "0x0800"
		match['nw_dst'] = self.config.PSC_DP_IF_IP
		flow['match'] = match
		action = {}
		action['output'] = self.psc['interfaces'][2]['name']
		flow['action'] = action
		self.networkManager.generateFlow('brData', flow)
		self.generatedFlows.append(flow)

		flow = {}
		match = {}
		match['in_port'] = self.psc['interfaces'][2]['name']
		flow['match'] = match
		action = {}
		action['output'] = self.userInterface 
		flow['action'] = action
		self.networkManager.generateFlow('brData', flow)
		self.generatedFlows.append(flow)

	def deleteAllTVD(self):
	        '''
        	Delete the TVD
	        '''
		self.logger.info("Deleting " + self.userName + " TVD")
		for ip in self.userIP:
			self.deleteTVD(ip)

	def deleteTVD(self, IPaddr):
        	'''
	        Remove an IP from the TVD in case of the last IP the TVD will be deleted
        	'''
		self.logger.info("Removing IP "+ IPaddr)
		self.delUserIP(IPaddr)
		if len(self.userIP) > 0:
			return False
		
		for flow in self.generatedFlows:
			self.networkManager.deleteFlow('brData', flow)

		self.logger.info("Deleting the user Interface")
		self.networkManager.deletePort('brData', self.userInterface)

		self.logger.info("Deleting PSC")
		if self.psc is not None:
			self.computeManager.deleteNF(self.psc['name'])
		
		self.logger.info("Deleting PSA")
		for psa in self.psaList:
			self.computeManager.deleteNF(psa['name'])
		
		logLine = "PSA:"
		for ipAddr in self.psaIPaddresses.values():
			logLine = logLine + " " + ipAddr
		logLine = logLine + ", PSC: "+ self.pscAddr + " removed"
		self.logger.info(logLine)
		return True

	def associateIPPSA(self,psaID):
	        '''
        	Associate an IP on a PSA
            	'''
		ipAddr = self.networkManager.getPSAnewAddress()
		self.psaIPaddresses[psaID] = ipAddr
		self.logger.info("User " + self.userName + " PSA "+psaID+" addr: "+ ipAddr)

	def definePSA(self, psaID):
        	'''
	        Define a new PSA for the TVD
        	'''
		manifest = self.manifestManager.getManifest(psaID)
        	properties = {}
	        properties['memory'] = manifest['memory']
	        properties['vcpu'] = manifest['vcpu']
	        properties['interfaces'] = []

	        interface = {}
	        interface['bridge'] = "brData"
	        interface['name'] = self.networkManager.generateVMPort()
	        properties['interfaces'].append(interface)

		interface = {}
	        interface['bridge'] = "brData"
	        interface['name'] = self.networkManager.generateVMPort()
	        properties['interfaces'].append(interface)

	        interface = {}
	        interface['vlan'] = self.vlanID
	        interface['bridge'] = "brCtl"
	        interface['name'] = self.networkManager.generateVMPort()
	        properties['interfaces'].append(interface)

		return properties

	def instantiatePSA(self, PSAList):
        	'''
	        Instantiate the PSAs for the TVD
        	'''
		for psa in PSAList:
			psaProperties = self.definePSA(psa['id'])
			psaName = self.computeManager.instantiateNF(psa['id'], psaProperties)
			psaProperties['name'] = psaName
			self.psaList.append(psaProperties)
		lastInterface = self.userInterface
		for psa in self.psaList:
			flow = {}
                	match = {}
                	match['in_port'] = lastInterface
                	flow['match'] = match
                	action = {}
                	action['output'] = psa['interfaces'][0]['name']
                	flow['action'] = action
                	self.networkManager.generateFlow('brData', flow)
                	self.generatedFlows.append(flow)
			flow = {}
                	match = {}
                	match['in_port'] = psa['interfaces'][0]['name']
                	flow['match'] = match
                	action = {}
                	action['output'] = lastInterface
                	flow['action'] = action
                	self.networkManager.generateFlow('brData', flow)
                	self.generatedFlows.append(flow)
			lastInterface = psa['interfaces'][1]['name']
		flow = {}
                match = {}
                match['in_port'] = lastInterface
                flow['match'] = match
                action = {}
                action['output'] = self.config.EXIT_INTERFACE
                flow['action'] = action
                self.networkManager.generateFlow('brData', flow)
                self.generatedFlows.append(flow)

		flow = {}
		flow['priority'] = "10"
		match = {}
		match['in_port'] = self.config.EXIT_INTERFACE
		match['dl_type'] = "0x0806"
		match['nw_dst'] = self.interfaceIP
		flow['match'] = match
		action = {}
		action['output'] = lastInterface
		flow['action'] = action
		self.networkManager.generateFlow('brData', flow)
		self.generatedFlows.append(flow)

		flow = {}
		flow['priority'] = "10"
		match = {}
		match['in_port'] = self.config.EXIT_INTERFACE
		match['dl_type'] = "0x0800"
		match['nw_dst'] = self.interfaceIP
		flow['match'] = match
		action = {}
		action['output'] = lastInterface
		flow['action'] = action
		self.networkManager.generateFlow('brData', flow)
		self.generatedFlows.append(flow)

		for ipAddr in self.psaIPaddresses.values():
			flow = {}
			flow['priority'] = "10"
			match = {}
			match['in_port'] = self.config.EXIT_INTERFACE
			match['dl_type'] = "0x0806"
			match['nw_dst'] = ipAddr
			flow['match'] = match
			action = {}
			action['output'] = lastInterface
			flow['action'] = action
			self.networkManager.generateFlow('brData', flow)
			self.generatedFlows.append(flow)

			flow = {}
			flow['priority'] = "10"
			match = {}
			match['in_port'] = self.config.EXIT_INTERFACE
			match['dl_type'] = "0x0800"
			match['nw_dst'] = ipAddr
			flow['match'] = match
			action = {}
			action['output'] = lastInterface
			flow['action'] = action
			self.networkManager.generateFlow('brData', flow)
			self.generatedFlows.append(flow)
