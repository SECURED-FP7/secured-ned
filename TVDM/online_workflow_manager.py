#!/usr/bin/env python

#
# NED Policy Manager (a.k.a the online workflow manager)
#
# Dependencies: pip install json2xml dicttoxml termcolor
#
# Example usage: ./online_workflow_manager.py child child 195.235.93.146 130.192.1.102 testCoop

import os
import json
import base64
import inspect
import requests
import dicttoxml
import upr_client
import online_workflow_manager
from sys import argv
from time import sleep
from xml.dom import minidom
from termcolor import colored
from lxml import etree, objectify
from lxml.etree import XMLSyntaxError
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import logging
import datetime as dt

# TODO: control if there are sessions open, if true close them
class MyFormatter(logging.Formatter):
    '''
    Formats logs with particular time-stamps. 
    '''
    converter=dt.datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


class WorkflowManager(object):
	DEBUG = False

	def dbprint(self, string):
            '''
            Debug function. When enabled
            produces more verbose logs.
            '''
	    if self.DEBUG == True:
	            self.logger.info(string)

        def spm_reconcile(self, spm_url, rec_input):
            '''
            Low-level auxiliary function which calls the SPM reconciliation
            service.
            '''
	    rec_svc = ":8181/restconf/operations/reconciliation:reconciliation"
	    url = "http://" + str(spm_url) + str(rec_svc)

	    self.dbprint("Contacting the SPM H2M service")

            r = ""
            headers = {'content-type': 'application/json'}

            counter = 0
	    while counter < 3:
		try:
                    if self.DEBUG == True:
                        #print str(rec_input)
                        self.dbprint( str(url) )
		    r = requests.post(url, auth=('admin', 'admin'),
			headers=headers, data=rec_input, timeout=None)
		    return r
		except Exception:
		    counter = counter + 1
		    if counter < 3:
		    	continue
		    # Give up
		    self.dbprint("ERROR: Could not reach SPM at " + str(url))
		    raise Exception ('Could not reach SPM.')
            return None

        def get_capability_from_mspl(self, mspl):
            '''
            Parse a specific MSPL and return a list of capabilities
            that are discovered inside
            '''
            capabilities = ""
            tree = ET.fromstring(mspl)
            root = tree
            for child in root:
                for a in child:
                    if (str(a.tag).endswith("capability")):
                        for b in a:
                            self.dbprint("Found a capability: " + str(b.text))
                            capabilities = capabilities + str(b.text)
            return capabilities

	def get_creator(self, user, upr):
                '''
                Get the administrator who created a given user
                '''
		r = upr.get_user_creator(user)
		if (r.status_code != 200):
			self.dbprint( "ERROR getting creator of user during reconciliation" \
					+ ". Status code = " + str(r.status_code))
			raise Exception('Error getting creator of ' + str(user) \
					+ ". Error is " + str(r.status_code) \
					+ '. Does ' + str(user) + ' exist?') 
		data = r.json()
		return data['creator']
		
	def get_PolicyStack(self, user, upr, cooperative, coop, uncoop):
                '''
                Get the policy stack of a particular user.
                '''
		mspls = []	
		coopList = []
                uncoopList = []
	
		
		creator = user
		
		# get all AG of user
		r = upr.get_user_ag(user)
		if r.status_code != 200:
			self.dbprint( "ERROR getting AG of user + " + str(user) + " with error code " + str(r.status_code))
		applicationGraphs = r.json()

		while creator != None:
			self.dbprint("")
			self.dbprint("Computing policy stack of layer : " + user+ " " +creator)

			#get all MSPLs of current stack layer
			r = upr.get_mspl(is_reconciled='false', target=str(user), editor=str(creator))
                        if r.status_code != 200:
                            raise Exception('Could not get policies for user!')
                        
                        mspl_list_json = r.json()

			for mspl in mspl_list_json:
				self.dbprint("Getting MSPL...")
				# add MSPL to msplList
                                mspls.append(mspl['mspl'])
			
			r = upr.get_user_list(user_id=creator)
			if (r.status_code != 200):
				self.dbprint("ERROR finding out cooperative data with + " \
						+ str(r.status_code))
				raise Exception ("Can't tell if cooperative: " \
						+ str(r.status_code) )
			data = r.json()
			creator_is_cooperative = data['is_cooperative']

			if cooperative and creator_is_cooperative:
                                try:
				    data = {}
				    data['id'] = str(coop)
				    data['ag'] = filter(lambda ag: ag['editor'].upper() == str(creator).upper(), applicationGraphs)[0]['ag'];
				    data['creator']  = creator
				    coopList.append(data)
				    coop += 1
				    self.dbprint("Adding to user's cooperative stack")
                                except IndexError:
                                    self.dbprint( colored("ERROR: USER " + str(creator) + " DOES NOT HAVE AN AG", 'red') )
			else:
				cooperative = False
                                try:
				    data = {}
				    data['id'] = str(uncoop)
				    data['ag'] = filter(lambda ag: ag['editor'].upper() == str(creator).upper(), applicationGraphs)[0]['ag'];
				    data['creator']  = creator
				    uncoopList.append(data)
				    uncoop += 1
				    self.dbprint("Adding to uncooperative stack")
                                except IndexError:
                                    self.dbprint( colored("ERROR: USER " + str(creator) + " DOES NOT HAV AN AG", 'red') )
			creator = self.get_creator(creator, upr)
			
		data = {}
		data['mspls'] = mspls
		data['coopList'] = coopList
		data['uncoopList'] = uncoopList
		data['cooperative'] = cooperative
		data['coop'] = coop
		data['uncoop'] = uncoop
		
		return data
	
	def reconcile(self, user, password, upr_url, spm_url, ned_ID):
                '''
                Function which gets all the users associated to a particular user
                (e.g. stakedholders like parent, ISP, country) and identify
                which policies are co-operative and non-co-operative.
                If successful, a reconciled application/service graph is produced
                and stored in the user's profile.
                '''
		self.dbprint("Truth and reconciliation...")
		upr = upr_client.UPRClient(str(upr_url))
	
	
		mspls = []	
		coopList = []
                uncoopList = []
                    
		data = self.get_PolicyStack(user, upr, True, 1, 1)
		mspls.extend(data['mspls'])
		coopList.extend(data['coopList'])
		uncoopList.extend(data['uncoopList'])
		
		data = self.get_PolicyStack(ned_ID, upr, data['cooperative'], data['coop'], data['uncoop'])
		mspls.extend(data['mspls'])
		coopList.extend(data['coopList'])
		uncoopList.extend(data['uncoopList'])

		coopList.reverse()
		uncoopList.reverse()
		
		# Prepare input 
		data = {}
		data['coop'] = coopList
		data['non_coop'] = uncoopList
		data['MSPL'] = mspls
		
		parent_json = {}
		parent_json['input'] = data
		rec_input = json.dumps(parent_json, sort_keys=True, indent=4)

	
		
		self.dbprint(rec_input)

                r = self.spm_reconcile(spm_url, rec_input)

                if r.status_code != 200:
                    self.dbprint( "ERROR: SPM returned " + str(r.status_code) )
                    raise Exception ("SPM returned " + str(r.status_code))

                data = r.json()

                rag = ""
                reconciled_mspls = []

                try:
                    rag = data['output']['application_graph']
                    r = upr.post_rag(user, ned_ID, rag)
                    if r.status_code != 201:
                        self.dbprint( colored("UPR did not save RAG: error " + str(r.status_code), 'red') )
                except KeyError:
                    self.dbprint( colored("No reconciled application graph", 'red') )

                try:
                    report = data['output']['report']
                    upr.post_reconciliation_report(user, ned_ID, report)
                except KeyError:
                    self.dbprint( colored('No reconciliation report', 'red'))

                try:
                    reconciled_mspls = data['output']['MSPL']
                    for m in reconciled_mspls:
                        capability = self.get_capability_from_mspl(base64.b64decode(m))
                        is_reconciled = True
                        r = upr.create_mspl(user, user, capability, is_reconciled, m)
                except KeyError:
                    self.dbprint( colored("No MSPLs returned from SPM reconciliation", 'red') )
		    
		
                return (rag, reconciled_mspls, None)


	def translate(self, spm_url, mspl, psaID):
            '''
            Low-level auxiliary function which translates a single MSPL
            rule into a specific PSA configuration, where PSA ID is
            the name of the PSA.
            '''
	    data = {}
	    data['mspl'] = base64.b64encode(mspl)
	    data['securityControl'] = psaID
	    m2l_input = {}
	    m2l_input['input'] = data
	    #self.dbprint( "INPUT IS: \n" + str(m2l_input)
	    headers = {'content-type': 'application/json'}
	    url = "http://" + spm_url + ":8090/M2LServiceCoordinator/rest/translate/" + str(psaID) + "/"
	    self.dbprint(url)
	    r = requests.post(str(url), data=data['mspl'], timeout=None)
	    if r.status_code == 200:
		self.dbprint( "SUCCESSFUL REPLY FROM THE M2L SERVICE")
		rawdata = (r.text).replace("This file contains specific configuration for the security control", "")
		# Marco!!! Don't mess with my data!
		data = base64.b64decode(rawdata)
		return data
	    else:
		self.dbprint( (spm_url + ": " + str(r.status_code)))
		return None


	# Returns a string
	def M2L(self, upr_url, spm_url, service_graph_xml, mspl_list_xml, user, password, editor_id):
            '''
            High-level function which translates the MSPL rules into low-level configurations.
            User is the username of the user.
            Password is the token of the user.
            Editor_id is the username of the user who created the policy.
            MSPL_list_xml is an XML list of MSPL rules which is returned by the SPM H2M service. 
            '''
            self.dbprint( "Starting M2L")
	    j = 0
	    return_code = "ERROR"

	    # Get UPR connection
	    upr = upr_client.UPRClient(str(upr_url))

	    # Extract data from the PSA list
	    xmldoc = minidom.parseString(service_graph_xml)
	    psa_list = xmldoc.getElementsByTagName('PSA')
	    self.dbprint( "There are " + str(len(psa_list)) + " PSAs")
	    for psa in psa_list:
		psa_name = psa.attributes['name'].value
		self.dbprint( "PSA name is " + str(psa_name))
		mspl_ids = psa.getElementsByTagName('mspl_list')

		# ICT hack - for now just get the first MSPL ID
		# TODO: need to support multiple MSPLs per PSA
		if len(mspl_ids) == 1:
		    mspl_id = mspl_ids[0].attributes['id'].value

		    # For each MSPL, get the configuration
		    for mspl in mspl_list_xml:
		        xml = minidom.parseString(mspl)
		        configuration = xml.getElementsByTagName('configuration')
		        name_tag = ""
		        self.dbprint( "DEBUG: Found " + str(len(configuration)) + " tags")

		        # For each configuration, find the corresponding application
                        for child in configuration[0].childNodes:
		            if child.nodeName == "Name":
		                mspl_name = child.firstChild.nodeValue
		                self.dbprint( "Comparing " + str(mspl_name) + " with " + str(mspl_id))

		                # If you find corresponding MSPL, get the translated LSPL from the SPM
		                if mspl_id == mspl_name:
		                    self.dbprint( "Found corresponding MSPL, getting translated LSPL")
		                    lspl = self.translate(spm_url, mspl, psa_name)
		                    lspl = base64.b64encode(lspl)
		                    r = upr.post_psaconf(user,psa_name,lspl)
		                    if r.status_code == 201:
		                        self.dbprint(
                                                colored("yay, i has LSPL in the UPR." + \
                                                        "Use get_userpsa_conf to get them", 'green'))
		                    else:
		                        self.dbprint( colored("Failed to get LSPL: Error code " + \
                                                str(r.status_code), 'red'))
		                        return_code = "ERROR " + str(r.status_code)
		                        return return_code
		        self.dbprint( "Finished looking for MSPL")

		else:
		    return "ERROR: Multiple MSPLs per PSA unsupported at the moment"

	    return_code =  "Success"
	    return return_code

        def delete_all_rec_mspl(self, user, password, upr_url):
            '''
            Deletes old reconciled MSPLs which are no longer valid. 
            User Profile Repository (UPR) must be specified as well as the access token.
            '''
            upr = upr_client.UPRClient(str(upr_url))
            r = upr.get_mspl(target=user,editor=user,is_reconciled='true')
            if r.status_code != 200:
                raise Exception ("WFM could not delete MSPL policies from the UPR " + str(r.status_code))

            data = r.json()
            for mspl in data:
                mspl_id = mspl['mspl_id']
                r = upr.delete_mspl(mspl_id)
                if r.status_code != 204:
                    self.dbprint( "Could not delete MSPL??? " + str(r.status_code) )

	def __init__(self, user, password, upr_url, spm_url, ned_ID, debug=False):
		self.init_log()
	
		# If debug is enabled
		if (debug == True):
			self.DEBUG = True

                self.delete_all_rec_mspl(user, password, upr_url)

		results = self.reconcile(user, password, upr_url, spm_url, ned_ID)

                if results == None:
                    raise Exception ("Reconciliation failed")

                if results[0] == "":
                    raise Exception ("No service graph returned from reconciliation")

                if len(results) < 3:
                    raise Exception ("Didn't get the expected number of return values")

                sg = base64.b64decode(results[0])
                mspl_list = results[1]
                editor_id = results[2]

                i=0
                while i < len(mspl_list):
                    mspl_list[i] = base64.b64decode(mspl_list[i])
                    i=i+1

                if mspl_list != [] and sg != "":
                    self.dbprint( "Running M2L" )
                    self.M2L(upr_url, spm_url, sg, mspl_list, user, password, editor_id)

	def init_log(self):
                '''
                Initialises logger and logs to a file called WFM.log
                '''
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(logging.DEBUG)

		fh = logging.FileHandler("WFM.log")
		fh.setLevel(logging.DEBUG)

		console = logging.StreamHandler()

		formatter = MyFormatter(fmt='%(asctime)s %(message)s',datefmt='%Y-%m-%d,%H:%M:%S.%f')
		fh.setFormatter(formatter)
		console.setFormatter(formatter)

		self.logger.addHandler(console)
		self.logger.addHandler(fh)
		#logging.basicConfig(filename=conf.LOG_FILE,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
		self.logger.info("--------")
		self.logger.info("WFM running")
		self.logger.info("--------")


def main():
        '''
        Invoked when run manually from the command line
        '''
	args = argv
	set_debug = None

	for a in args:
		if a == "--debug":
			set_debug = True
               		args.remove('--debug')


	if len(args) != 6:
		print("online_workflow_manager.py <username> <password>" + \
				"<upr_address> <spm_address> <ned_ID>")
		print("\nMy job is turn MSPL into LSPL, just like water into wine")
	else:
		script, user, password, upr_url, spm_url, ned_id = argv
		wfm = WorkflowManager(user, password, upr_url, spm_url, 
				ned_id, debug=set_debug) 

if __name__ == '__main__':
	main()
