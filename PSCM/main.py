'''
Created on 12/set/2014

'''
import falcon
import logging
from AuthUser import Authenticate
import Config

conf = Config.Configuration()
logging.basicConfig(filename="PSCM.log",level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

logging.info("--------")
logging.info("PSCM init.")
logging.info("PSCM VERSION: " + str(conf.PSCM_VERSION)) 
logging.info("--------")

# Falcon starts
app = falcon.API()
app.add_route('/login', Authenticate(conf))
