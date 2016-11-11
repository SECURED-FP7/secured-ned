'''
Created on 29/lug/2014

'''
from lxml import etree
import libvirt
import subprocess
import thread
import json
import logging
import sys
import os
from userTVD import UserTVD
from userTVDIPSECLess import UserTVD as UserTVDIPSECLess
from Network import Network
from Compute import Compute


class GraphInstantiator(object):
    '''
    Class used to instantiate the TVD and the Profile Graph
    '''


    def __init__(self, configure, logger, useIPSEC=False):
        '''
        Constructor
        '''

        subprocess.call(["bash", configure.SCRIPT_LOCATION+"emptyDHCP.sh"])
	self.useIPSEC = useIPSEC
	
	self.IPandUser = {} #Used to associate the token to the IP (for the logout
        self.logger = logger
	self.config = configure
	self.networkManager = Network(configure)
	self.computeManager = Compute(configure)
	self.userTVDs = {} #All the generated TVD
        self.TokenIP = {} #Associate the PSC IP to a specifc user
	self.sigTerm = False

    def instatiateTVD(self, session):
	'''
	Intantiate the TVD for a logged user.
	In case for a TVD already instatiated it will generate the flows used for reedirecting the traffic of the new defice on it
	'''

	if session['IP'] in self.IPandUser.keys():
		self.logger.info("Machine already logged")
		return

	self.IPandUser[session['IP']] = session['token']
	
	if session['token'] in self.userTVDs.keys():
		userTVD = self.userTVDs[session['token']]
		userTVD.addNewIP(session['IP'])
		return

	#If the user have no TVD instantiated
	vlanID = self.networkManager.getNewVLANID()
	if self.useIPSEC:
		newTVD = UserTVD(session['token'], vlanID, self.networkManager, self.computeManager, self.config, self.logger)
	else:
		newTVD = UserTVDIPSECLess(session['token'], vlanID, self.networkManager, self.computeManager, self.config, self.logger)
	self.userTVDs[session['token']] = newTVD

	#Generates the PSC for the user
	mac = self.networkManager.generateMACaddress()
	newPSC = self.definePSC(vlanID, mac)	
	pscAddr = self.networkManager.configureNewIPOnDHCP(mac, session['token'])
	self.logger.info("PSC address for user "+session['token']+" "+pscAddr)
	self.TokenIP[pscAddr] = session['token']
	pscName = self.computeManager.instantiateNF('psc', newPSC)
	newPSC['name'] = pscName
	newTVD.setPSC(newPSC, pscAddr)
	self.logger.info("PSC created")
	newTVD.generatePSCflows()
	newTVD.addNewIP(session['IP'])

    def definePSC(self, vlanID, mac):
	'''
	Define the template for the PSC of the TVD
	'''

	properties = {}
	properties['memory'] = "512"
	properties['vcpu'] = "1"
	properties['interfaces'] = []
	
	interface = {}
	interface['mac'] = mac
	interface['bridge'] = "brCtl"
	interface['name'] = self.networkManager.generateVMPort()
	properties['interfaces'].append(interface)

	interface = {}
	interface['vlan'] = vlanID
	interface['bridge'] = "brCtl"
	interface['name'] = self.networkManager.generateVMPort()
	properties['interfaces'].append(interface)

	interface = {}
	interface['bridge'] = "brData"
	interface['name'] = self.networkManager.generateVMPort()
	properties['interfaces'].append(interface)

	return properties


    def deleteUser(self, session):
	'''
	This function is used for the user log out. If there are multiple devices connected it will be deleted only the flows for the specifc device that did the log out.
	If the last device for that specific user is disconnected the graph will be destroyed
	'''
	if session['IP'] not in self.IPandUser.keys():
		self.logger.info("Machine not logged in")
		return
	token = self.IPandUser[session['IP']]
	del self.IPandUser[session['IP']]
	userTVD = self.userTVDs[token]
	if userTVD.deleteTVD(session['IP']):
		del self.TokenIP[userTVD.pscAddr]
		del self.userTVDs[token]

    
    def instantiatePSA(self, session):
	'''
	Instantiate the PSA of the TVD
	'''
        PSAList = session['PSAs']
	userTVD = self.userTVDs[session['token']]
	userTVD.instantiatePSA(PSAList)
       
    def signal_term_handler(self):
	'''
	Used on SIGTERM signal to destroy all the instantiated TVD
	'''
	if not self.sigTerm:
		self.sigTerm = True
		for userTVD in self.userTVDs.values():
			userTVD.deleteAllTVD()
		return True
	return False
