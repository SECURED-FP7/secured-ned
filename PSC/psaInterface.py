#
#   File:       psaInterface.py
#   Created:    25/08/2014
#   Author:     BSC, VTT
#
#   Description:
#       REST interface to receive configuration requests from the PSAs
#

import falcon
import json
import logging
import sys
from pscExceptions import pscExceptions
import threading
from time import sleep

class psaInterface():
    def __init__(self, confsPath):
        self.confsPath = confsPath
        self.psa_list = []
    
    # Config is pulled by the PSA, also functions as a PSA UP event.
    # Stores every PSA IP and PSA ID that are up
    def on_get(self, request, response, psa_id):
        try:
            logging.info(request.method+" "+request.uri)
            try:
                fp = open(self.confsPath+"/"+psa_id, 'rb')
                conf = fp.read()
                fp.close()     
            except IOError as exc:
                logging.error("Unable to read file "+self.confsPath+"/"+psa_id)
                raise exc

            # Store current PSA ID and IP, if not present
            res = {"psa_id": psa_id, "ip": self.get_client_address(request.env)}
            if not res in self.psa_list:
                self.psa_list.append(res)
                with open(self.confsPath + "/psa_online", 'wb') as f:            
                    f.write(json.dumps(self.psa_list))
            
            response.data = conf
            response.status = falcon.HTTP_200
            logging.info("PSA "+psa_id+" configuration sent to "+self.get_client_address(request.env))
        
        except Exception as e:
            logging.exception(sys.exc_info()[0])
            response.status = falcon.HTTP_501
    
    def get_client_address(self,environ):
        try:
            return environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
        except KeyError:
            return environ['REMOTE_ADDR']
