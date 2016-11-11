import falcon
import json
from threading import Thread
from GraphInstatiator import GraphInstantiator
import logging
import sys

class Orchestrator(object):
    '''
    Orchestrator class that intercept the REST call through the WSGI server
    '''

    def __init__(self, instantiator):
        '''
        Constructor
        '''
        self.instantiator = instantiator
    
    def on_delete(self, request, response):
        try:
            args = request.stream.read()
            self.instantiator.logger.info(request.method+" "+request.uri+" "+args)
	    session = json.loads(args, 'utf-8')
	    token = self.instantiator.IPandUser[session["IP"]]
	    newTVD = Thread(target=self.instantiator.deleteUser,kwargs={"session" :session})
            newTVD.start()
            response.status = falcon.HTTP_200
        except Exception as e:
            self.instantiator.logger.exception(sys.exc_info()[0])
            response.status = falcon.HTTP_501      
    
    def on_put(self, request, response):
        try:
            args = request.stream.read()
            self.instantiator.logger.info(request.method+" "+request.uri+" "+args)
            session = json.loads(args, 'utf-8')
            newTVD = Thread(target=self.instantiator.instatiateTVD,kwargs={"session" :session})
            newTVD.start()
            response.status = falcon.HTTP_200
        except Exception as e:
            self.instantiator.logger.exception(sys.exc_info()[0])
            response.status = falcon.HTTP_501

    def on_get(self, request, response):
        pass

   
        

                
