'''
Created on 12/set/2014

'''
import falcon
import logging
import json
import sys
import subprocess
import requests
import hashlib
import upr_client

class Authenticate(object):
    '''
    classdocs
    '''


    def __init__(self, config):
        '''
        Constructor
        '''       
        self.loginPageLocation = config.LOGIN_PAGE_LOCATION
        self.orchestratorLocation = config.ORCHESTRATOR_LOCATION
        self.use_local_file = config.USE_LOCAL_FILE
        self.upr_client = upr_client.UPRClient(config.UPR_LOCATION)
        logging.info("PSCM AuthUser.Authenticate loaded, use local users accounts:" + str(self.use_local_file))

        if self.use_local_file:
           fp = open(config.USER_DATA_LOCATION, 'r')
           users = fp.read()
           fp.close()
           self.users = {}
           listUsr = users.split()
           while True:
                try:
                    name = listUsr.pop(0)
                    self.users[name] = listUsr.pop(0)
                except:
                    break
        
    def on_get(self, request, response):
        try:
            fp = open(self.loginPageLocation, 'r')
            page = fp.read()
            fp.close()
            response.set_header("Content-Type", "text/html")
            response.body = page
            response.status = falcon.HTTP_200
        except Exception as e:
            logging.exception(sys.exc_info()[0])
            response.status = falcon.HTTP_501
    
    def on_post(self, request, response):
        try:
            args = request.stream.read()
            logging.info(request.method+" "+request.uri+" "+args)
            session = json.loads(args, 'utf-8')
            if self.use_local_file:
                if self.users.has_key(session['user']):
               	    if self.users[session['user']] == hashlib.sha256(session['password']).hexdigest():
                        subprocess.call(["ip", "netns", "exec", "orchNet", "curl", "-X", "PUT", "--header", "Accept: application/json", "--header", "Content-Type: application/json", "-d", '{"token":"'+session['user']+'", "IP":"'+self.get_client_address(request.env)+'"}', self.orchestratorLocation])
                        response.status = falcon.HTTP_200
                    else:
                        logging.info("Auth error: "+hashlib.sha256(session['password']).hexdigest())
                        response.status = falcon.HTTP_401
                else:
                    logging.info("User does not exsist")
                    response.status = falcon.HTTP_401
            else:
                r = self.upr_client.auth_user(session['user'], session['password'])
                if r.status_code == requests.codes.ok:
                    subprocess.call(["ip", "netns", "exec", "orchNet", "curl", "-X", "PUT", "--header", "Accept: application/json", "--header", "Content-Type: application/json", "-d", '{"token":"'+session['user']+'", "IP":"'+self.get_client_address(request.env)+'"}', self.orchestratorLocation])
                    response.status = falcon.HTTP_200
                else:
                    logging.info("Auth error")
                    response.status = falcon.HTTP_401
        except Exception as e:
            logging.exception(sys.exc_info()[0])
            response.status = falcon.HTTP_501

    def on_delete(self, request, response):
        try:
            logging.info(request.method+" "+request.uri)
            proc = subprocess.Popen("ip netns exec orchNet curl -X DELETE --header Accept: application/json --header Content-Type: application/json -d '{\"IP\":\""+self.get_client_address(request.env)+"\"}' -sw '%{http_code}' "+self.orchestratorLocation, stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate() 
            returnedValue = int(out)
            if returnedValue == 200:
                response.status = falcon.HTTP_200
            else:
                logging.info("User is not already instantiated")
                response.status = falcon.HTTP_401
        except Exception as e:
            logging.exception(sys.exc_info()[0])
            response.status = falcon.HTTP_501
            
    def get_client_address(self,environ):
        return environ['REMOTE_ADDR']
