'''
Created on 09/set/2014

'''

import falcon
import logging
import sys
import json
import upr_client

class PSAConf(object):
    '''
    Class with the API for the REST call of the TVDM to get the user Graph information
    '''

    def __init__(self, confsPath, logger, config, instantiator):
        self.confsPath = confsPath
        self.logger = logger
        self.config = config
        self.upr_client = upr_client.UPRClient(config.UPR_LOCATION)
        self.instantiator = instantiator

    def on_get(self, request, response, psa_id, conf_id):
        """
        Load PSA configuration for a new request
        """
        try:
            self.logger.info(request.method+" "+request.uri)
            #TODO: define other formats, e.g., zipped
            conf_type = None
            #logging.info(self.confsPath+"/"+psa_id+"/"+conf_id)
            if self.config.USE_LOCAL_FILE:
                self.logger.info("-PSAConf Load PSA config from local file.")
                try:
                    fp = open(self.confsPath+"/"+psa_id+"/"+conf_id, 'rb')
                    conf = fp.read()
                    fp.close()
                except IOError as exc:
                    logging.error("Unable to read file "+self.confsPath+"/"+psa_id+"/"+conf_id)
                    raise exc
                conf_type = "text"
            else:
                token = self.instantiator.TokenIP[self.get_client_address(request.env)]
                self.logger.info("-PSAConf Load PSA config from UPR for user:" +str(token) + ", psa_id:" + str(psa_id))
                r = self.upr_client.get_user_psaconf(token, psa_id)
                self.logger.info("response:" + str(r.json()))
                conf = r.json()["conf"]
                conf_type = "base64"

            #new JSON and IP
	    token = self.instantiator.TokenIP[self.get_client_address(request.env)]
	    userTVD = self.instantiator.userTVDs[token]
            configuration = {}
            configuration['conf_type'] = conf_type
            configuration['conf'] = conf
            if psa_id in userTVD.psaIPaddresses.keys():
                self.logger.info("PSAConf: PSA requires IP")
                configuration["IP"] = userTVD.psaIPaddresses[psa_id]
                configuration["gateway"] = self.config.GATEWAY_IP
                configuration["dns"] = self.config.DNS_IP
                configuration["netmask"] = self.config.NETMASK
                configuration["userIP"] = userTVD.interfaceIP
            else:
                self.logger.info("PSAConf: PSA doesn't require IP")
            response.data = json.dumps(configuration)
            response.status = falcon.HTTP_200
            self.logger.info("PSA "+psa_id+" configuration "+conf_id+" sent to PSC "+self.get_client_address(request.env))

        except Exception as e:
            self.logger.exception(sys.exc_info()[0])
            response.status = falcon.HTTP_501
            

    def get_client_address(self,environ):
        """
        Retrieves IP of user request
        """
        try:
            return environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
        except KeyError:
            return environ['REMOTE_ADDR']
        
