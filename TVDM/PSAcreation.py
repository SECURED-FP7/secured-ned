import falcon
import json
from threading import Thread
from GraphInstatiator import GraphInstantiator
import logging
import sys

class PSAcreation(object):
    '''
    Orchestrator class that intercept the REST call through the WSGI server
    '''

    def __init__(self, instantiator):
        '''
        Constructor
        '''
        self.instantiator = instantiator
    
    def on_delete(self, request, response):
        pass      
    
    def on_put(self, request, response):
        try:
            args = request.stream.read()
            self.instantiator.logger.info(request.method+" "+request.uri+" "+args)
            session = json.loads(args, 'utf-8')
            session['token'] = self.instantiator.TokenIP[self.get_client_address(request.env)]
            #logging.info(session)
            newTVD = Thread(target=self.instantiator.instantiatePSA,kwargs={"session" :session})
            newTVD.start()
            response.status = falcon.HTTP_200
            response.set_header("Accept", "application/json")
            response.set_header("Content-Type", "application/json")
        except Exception as e:
            response.status = falcon.HTTP_501
            self.instantiator.logger.exception(sys.exc_info()[0])

    def on_get(self, request, response):
        pass

    def get_client_address(self,environ):
        try:
            return environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
        except KeyError:
            return environ['REMOTE_ADDR']

   
        

                
