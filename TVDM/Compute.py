import uuid
from libvirtManager import ComputeManager

class Compute(object):

	def __init__(self, config):
		self.computeManager = ComputeManager(config) 

	def instantiateNF(self, nfID, nfProperties):
		'''
		Instantiate a network function. 
		nfID is the ID to identify the NF in the database.
		nfProperties is a map with the properties of the VM.
                The JSON format is: 
                {
                memory:memory requirement(KiB)
                vcpu:numeber of core needed
                interfaces:[list of interfaces]
		}	
		'''
		name = str(uuid.uuid4())
		diskInformation = self.computeManager.getDiskInfo(nfID, name)
		nfProperties['disk'] = diskInformation
		self.computeManager.instantiateNF(name, nfProperties)
		return name

	def deleteNF(self, nfID):
		'''
		Delete a NF
		nfID = ID to identify the NF on the NED
		'''
		self.computeManager.deleteNF(nfID)
