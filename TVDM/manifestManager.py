import json
import sys

class ManifestManager(object):

	def __init__(self, config):
		self.manifestPath = config.PSA_MANI_LOCATION


	def getManifest(self, psaID):
		'''
		Get information of the manifest of the PSA
		'''
		fp = open(str(self.manifestPath+'/'+psaID), 'r')
                manifest = fp.read()
                fp.close()
                return json.loads(manifest)
