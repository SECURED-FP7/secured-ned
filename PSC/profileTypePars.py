'''   

    File:       profileTypePars.py
    Created:    23/08/2014
  
    @author:    BSC
  
    Description:
        This script take as input the profyleType json file and computes the TVD topology to be sent back 
        to the Orchestror

'''

import requests
import json 
import logging
from pscExceptions import pscExceptions
from tvdTop import tvdTop
import utils

class profileTypePars():

    def __init__(self, orchAddr, configsPath):
        self.orchAddr = orchAddr
        self.conf_URIs_list = {}
        self.conf_list = {}
        self.sg_dict = {}
        self.configsPath = configsPath


    def requestProfileType(self):
        logging.info("Sending profile type request to Orchestrator...")
        
        # We don't need to send the token, actually we need to get it from the TVDM
        #body = {"token":self.token}
        header = {'Accept': 'application/json', 'Content-Type':'application/json'}
        # check: body of GET should not contain anything influencing the decision of the server
        # use post for that
        #resp = requests.get(self.orchAddr+"/getGraph", data=json.dumps(body), headers=header)
        resp = requests.get(self.orchAddr+"/getGraph", headers=header)
        logging.info("Orchestrator replied: "+str(resp.status_code)+" "+resp.text)
        return resp


    def parsProfile(self, resp):
        # convert resp body to JSON-like string
        proType = json.loads(resp.text)

        # Receives the profileType json object to be processed
        if (proType['name'] == "user_profile_type"):
            try:
                # resolveTVDtop generates the service graph structure in form of a dictionary 
                self.TVDman = tvdTop(self.sg_dict)
                self.sg_dict = self.TVDman.resolveTVDtop(proType)
            except Exception as exc:
                #logging.error("Unable to write to file "+path+"/"+v_conf)
                logging.error("TVDman error:" + str(exc.message))
                raise exc

            # the service graph dictionary is encoded in json format according to the 
            # serviceGraph schema and sent to the Orchestrator 
            body = json.dumps(self.sg_dict)
            header = {'Accept': 'application/json', 'Content-Type':'application/json'}	    

            # sends the service graph to the Orchestrator
            logging.info("Sending PSA service graph instantiation request to Orchestrator...")
            resp = requests.put(self.orchAddr+"/createPSA", data=body, headers=header)

            if (resp.status_code != 200):
                logging.error("Orchestrator failed to instatiate TVD error: "+resp.status_code)
                raise pscExceptions.TVDnotInstantiated("Orchestator response failure")
            
            logging.info("Orchestrator replied: "+str(resp.status_code)+" "+resp.text)

            # scan PSAs list and retrieve configuration files URIs
            PSAList = self.sg_dict['PSAs']
            
            # Create path if not existing
            utils.mkdir_p(self.configsPath)
            # Save the list of PSA's, i.e., the user graph
            with open(self.configsPath + "/psa_list", 'wb') as f:            
                f.write(json.dumps(PSAList))

            for psa in PSAList:
                self.conf_URIs_list[psa['id']] = psa['conf']

            # petition for PSA configuration file
            # TODO adapt TVDM to reply to configuration file request (aka register every conf file as a resource on the TVDM interface)
            for k_id, v_conf in self.conf_URIs_list.iteritems():
                logging.info("Sending request of conf file for PSA "+k_id)
                header = {'Content-Type':'application/octet-stream'}
                resp = requests.get(self.orchAddr+"/getConf/"+k_id+"/"+v_conf, headers=header)
                #resp = requests.get(self.orchAddr+"/getConf/"+k_id+"_"+v_conf, headers=header)
                logging.info("Orchestrator replied: "+str(resp.status_code))
                if (resp.status_code == requests.codes.ok):
                    #path=self.configsPath+"/"+k_id
                    #utils.mkdir_p(self.configsPath)
                    try:
                        #fp=open(path+"/"+v_conf,'wb')
                        fp=open(self.configsPath+"/"+k_id,'wb')
                        fp.write(resp.content)
                        fp.close()
                        logging.info("PSA "+k_id+" configuration "+v_conf+" registered")
                    except IOError as exc:
                        #logging.error("Unable to write to file "+path+"/"+v_conf)
                        logging.error("Unable to write to file "+self.configsPath+"/"+k_id)
                        raise exc

                else: 
                    logging.error("Bad configuration request for PSA "+k_id)
                    raise pscExceptions.PSAconfNotFound("Orchestator response failure")



            # # send requests for the PSAs configuration files to the Orchestator
            # logging.info("Sending PSA configuration files request to Orchestrator...")
            # body = json.dumps(self.conf_URIs_list)
            # header = {'Accept': 'application/json', 'Content-Type':'application/json'}   
            # resp = requests.post(self.orchAddr+"/getConf", data=body, headers=header)           
            # logging.info("Orchestrator replied: "+resp.status_code+" "+resp.text)

            # # receives PSAs configuration files
            # sjson = json.loads(resp.text)
            # #rjson = json.loads(sjson)
            # self.conf_list = sjson['configurations']            
            
        else:
            raise pscExceptions.pscscWrongProfileType("Wrong profile type file: [name] field is not as expected")
    

    # def getPSAconf(self, psaID):
        
    #     for psa in self.conf_list:
    #         if (psa['PSA_id'] == psaID):
    #             return psa['conf_script']
        
    #     raise pscExceptions.PSAconfNotFound("Configuration file for the requested PSA has not been found or does not exist")

