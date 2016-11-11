from lxml import etree





class parseXml(object):
	"""
	Parser for the XML data retrieved from the repositories
	"""

	@staticmethod
	def parseAG(user_id, xml):
	        """
	        Parse the application graph on a dictionary
	        """
		serviceGraph = {}
		serviceGraph['name'] = "user_profile_type"
		serviceGraph['user_token'] = user_id
		serviceGraph['profile_type'] = "AD"
		serviceGraph['PSASet'] = []
		serviceGraph['ingress_flow'] = []
		serviceGraph['egress_flow'] = []
		root = etree.fromstring(xml)
		for graph in root:
			for service in graph:
				for child in service:
					if child.tag.split('}', 1)[1] == 'PSA':
						newPSA = {}
						newPSA['id'] = child.attrib['name']
						newPSA['security_controls'] = []
						config = {}
						config['imgName'] = child.attrib['name']
						config['conf_id'] = user_id
						newPSA['security_controls'].append(config)
						serviceGraph['PSASet'].append(newPSA)
						serviceGraph['ingress_flow'].append(child.attrib['name'])
						serviceGraph['egress_flow'].insert(0, child.attrib['name'])
		return serviceGraph
