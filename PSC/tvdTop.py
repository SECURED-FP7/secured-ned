'''

    File:       tvdTop.py
    Created:    26/08/2014
    
    @author:    BSC, VTT
  
    Description:
        Service class used to compute the service graph to be passed to the Orchestrator, 
        starting from the profileType json file received.
        It includes also methods used by the internal logic of the PSC to store and retrieve info about
        the TVD topology.

'''

import json
import hashlib
from datetime import datetime

class tvdTop():
    def __init__(self, sg_dict):
        self.sg_dict = sg_dict

    def resolveTVDtop(self, proType):

        '''
        Right now the TVD resolution logic is a dumb reformatting of the profileType file
        The only valid modification is the added unique TVDid
        '''
        
        self.sg_dict['name'] = "user_service_graph"
    	
        # unique TVD id generation; the token <--> TDV_id association is only known to the PSC 
        # as the Orchestrator deletes the entry as soon as the instantiation is done
        self.sg_dict['TVDid'] = hashlib.sha256(proType['user_token']+str(datetime.now())).hexdigest()
        
        self.sg_dict['token'] = proType['user_token']
        
        PSAs = []
        temp = {}
        for psa in proType['PSASet']:
            # Create a new holder for every PSA 
            temp = {}
            temp['id'] = psa['id']
            # the following doesn't work for PSAs described by multiple security controls
            # [0] is hardcoded for the first value
            temp['conf'] = psa['security_controls'][0]['conf_id']
            print temp
            PSAs.append(temp)

        self.sg_dict['PSAs'] = PSAs

        # TODO fix in NED!
        # UPR changes DO NOT provide these.... But are they used anyhow, later in NED - NO?
        if 'ingress_flow' in proType:
            self.sg_dict['ingress_flow'] = proType['ingress_flow']
        else:
            self.sg_dict['ingress_flow'] = None
        if 'egress_flow' in proType:
            self.sg_dict['egress_flow'] = proType['egress_flow']
        else:
            self.sg_dict['egress_flow'] = None
        return self.sg_dict

    # def resolveTVDtop(self, proType):
        
    #     # dummy resolveTVDtop that returns a static local serviceGraph file
    # 	# TODO PSC TVD resolution logic

    # 	fp = open("./json/serviceGraph_ex.json", "r")
    # 	sg_dict = json.loads(fp.read() % self.token)
    # 	self.sg_dict = sg_dict
    	
    # 	return sg_dict

    
