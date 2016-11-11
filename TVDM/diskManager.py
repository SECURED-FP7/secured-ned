import subprocess
from manifestManager import ManifestManager


class DiskManager(object):


	def __init__(self, configure):
		self.imagesLocation = configure.VM_IMAGES_LOCATION
        	self.vmLocation = configure.INSTANTIATED_VM_LOCATION
		self.manifestManager = ManifestManager(configure)

	def retriveDisk(self, nfID, localNFID):
		'''
		Retrieve the Disk for a NF
		'''
		manifest = self.manifestManager.getManifest(nfID)
		subprocess.call(["qemu-img", "create", "-b", self.imagesLocation+manifest['disk'], "-f", "qcow2", self.vmLocation+localNFID+".qcow2"])
		return self.vmLocation+localNFID+".qcow2"

	def removeLocalDisk(self, localNFID):
		'''
		Remove a Disk from the local drive
		'''
		subprocess.call(["rm", "-f", self.vmLocation+localNFID+".qcow2"])
