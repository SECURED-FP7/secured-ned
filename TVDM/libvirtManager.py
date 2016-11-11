import libvirt
from lxml import etree
from diskManager import DiskManager

class ComputeManager(object):

	def __init__(self, config):
		self.conn = libvirt.open("qemu:///system")
		self.diskManager = DiskManager(config)

	def instantiateNF(self, name, vmProperty):
		'''
		Instantiate a VM
		'''
		vmXML = self.defineXML(name, vmProperty)
		self.conn.defineXML(vmXML)
		domain = self.conn.lookupByName(name)
		domain.create()

	def deleteNF(self, name):
		'''
		Destroy a VM
		'''
		domNF = self.conn.lookupByName(name)
                domNF.destroy()
                domNF.undefine()
		self.diskManager.removeLocalDisk(name)

	def getDiskInfo(self, nfID, localNFID):
		'''
		Get the information of the disk for the VM
		'''
		diskLocation = self.diskManager.retriveDisk(nfID, localNFID)
		newDisk = {}
		newDisk['location'] = diskLocation
		newDisk['type'] = 'qcow2'
		return newDisk

	def defineXML(self, name, vmProperty):
		'''
		Define the xml to use to generate the VM
		name = name of the virtual machine
		vmProperty = map with the properties of the VM:
		{
		memory:memory requirement(KiB)
		vcpu:numeber of core needed
		disk:{location:disk location
			type:type of the disk}
		interfaces:[list of interfaces]
		}
		'''
		vmXML = etree.Element('domain')
		vmXML.attrib['type'] = 'kvm'
		element = etree.Element('name')
		element.text = name
		vmXML.append(element)
		element = etree.Element('memory')
		element.attrib['unit'] = 'MiB'
		element.text = str(vmProperty['memory'])
		vmXML.append(element)
		element = etree.Element('currentMemory')
		element.attrib['unit'] = 'MiB'
		element.text = str(vmProperty['memory'])
		vmXML.append(element)
		element = etree.Element('vcpu')
		element.attrib['placement'] = 'static'
		element.text = str(vmProperty['vcpu'])
		vmXML.append(element)
		element = etree.Element('os')
		element2 = etree.Element('type')
		element2.text = 'hvm'
		element.append(element2)
		vmXML.append(element)
		
		element = etree.Element('devices')
		
		element2 = etree.Element('disk')
		element2.attrib['type'] = 'file'
		element2.attrib['device'] = 'disk'
		element3 = etree.Element('driver')
		element3.attrib['name'] = 'qemu'
		element3.attrib['type'] = vmProperty['disk']['type']
		element2.append(element3)
		element3 = etree.Element('source')
		element3.attrib['file'] = vmProperty['disk']['location']
		element2.append(element3)
		element3 = etree.Element('target')
		element3.attrib['dev'] = 'vda'
		element2.append(element3)
		element.append(element2)

		for interface in vmProperty['interfaces']:
			element2 = etree.Element('interface')
			element2.attrib['type'] = 'bridge'
			if 'vlan' in interface.keys():
				element3 = etree.Element('vlan')
				element4 = etree.Element('tag')
				element4.attrib['id'] = str(interface['vlan'])
				element3.append(element4)
				element2.append(element3)
			if 'mac' in interface.keys():
				element3 = etree.Element('mac')
				element3.attrib['address'] = interface['mac']
				element2.append(element3)
			element3 = etree.Element('source')
			element3.attrib['bridge'] = interface['bridge']
			element2.append(element3)
			element3 = etree.Element('virtualport')
			element3.attrib['type'] = 'openvswitch'
			element2.append(element3)
			element3 = etree.Element('target')
			element3.attrib['dev'] = interface['name']
			element2.append(element3)
			element.append(element2)
					
		element2 = etree.Element('controller')
		element2.attrib['type'] = 'usb'
		element2.attrib['index'] = '0'
		element.append(element2)
		
		element2 = etree.Element('controller')
		element2.attrib['type'] = 'pci'
		element2.attrib['index'] = '0'
		element2.attrib['model'] = 'pci-root'
		element.append(element2)

		element2 = etree.Element('graphics')
		element2.attrib['type'] = 'vnc'
		element2.attrib['port'] = '5900'
		element2.attrib['autoport'] = 'yes'
		element2.attrib['listen'] = '127.0.0.1'
		element.append(element2)

		vmXML.append(element)

		return etree.tostring(vmXML)
