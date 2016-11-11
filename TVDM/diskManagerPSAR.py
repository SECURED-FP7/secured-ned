import subprocess
from manifestManager import ManifestManager
import psar

class DiskManager(object):


	def __init__(self, configure):
		self.imagesLocation = configure.VM_IMAGES_LOCATION
        	self.vmLocation = configure.INSTANTIATED_VM_LOCATION
		self.manifestManager = ManifestManager(configure)
		self.client = psar.Client(configre.PSAR_LOCATION)

	def retriveDisk(self, nfID, localNFID):
		'''
		Retrive the Disk for a NF
		'''
		r = self.client.get_imagelist(id=nfID)
		nfInfo = json.loads(r.text)[0]
		diskHash = nfInfo["psa_image_hash"] 
		if self.file_accessible(self.imagesLocation+nfID, 'r'):
			f = open(self.imageLocation+nfID+".hash", 'r')
			localHash = f.read()
			f.close()
			if localHash != diskHash:
				self.client.get_image_file(nfID, self.imagesLocation+nfID)
				f = open(self.imageLocation+nfID+".hash", 'w')
				f.write(diskHash)
				f.close()
		else:
			self.client.get_image_file(nfID, self.imagesLocation+nfID)
			f = open(self.imageLocation+nfID+".hash", 'w')
			f.write(diskHash)
			f.close()
		subprocess.call(["qemu-img", "create", "-b", self.imagesLocation+nfID, "-f", "qcow2", self.vmLocation+localNFID+".qcow2"])
		return self.vmLocation+localNFID+".qcow2"

	def removeLocalDisk(self, localNFID):
		'''
		Remove a Disk from the local drive
		'''
		subiprocess.call(["rm", "-f", self.vmLocation+localNFID+".qcow2"])

	def file_accessible(self, path, mode):
		try:
			f = open(path, mode)
			f.close()
			f = open(path+".hash", mode)
			f.close()
		except IOError as e:
			return False
		return True
