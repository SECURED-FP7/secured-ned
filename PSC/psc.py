''' 

	File:		psc.py   
	Created:	07/08/2014
	
	@author:	BSC
  
  	Description:
      	The WSGI app to be given to the HTTP proxy server (e.g. Gunicorn). 
      	Falcon is a web framework to manage WSGI interface and HTTP reply/responses       

'''

import falcon
import requests
import Config
import logging
from pscExceptions import pscExceptions
from psaInterface import psaInterface
from psaExecution import psaExecution
from profileTypePars import profileTypePars
from tvdTop import tvdTop
from dumpLogFile import dumpLogFile

conf = Config.Configuration()

date_format = "%m/%d/%Y %H:%M:%S"
log_format = "[%(asctime)s.%(msecs)d] [%(module)s] %(message)s"
logging.basicConfig(filename=conf.LOG_FILE,level=logging.DEBUG,format=log_format, datefmt=date_format)
#logging.basicConfig(filename=conf.LOG_FILE,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


logging.info("--------")
logging.info("PSC init.")
logging.info("PSC VERSION: " + str(conf.PSC_VERSION)) 
logging.info("PSA-PSC API version: " + str(conf.PSA_API_VERSION))
logging.info("--------")


orchAddr = conf.ORCHESTRATOR_ADDRESS
configsPath = conf.PSA_CONFIG_PATH

# classes instatiation
profPars = profileTypePars(orchAddr, configsPath)
psaIntfc = psaInterface(configsPath)
psaExec = psaExecution()
dumpLog = dumpLogFile()

# start the HTTP falcon proxy and adds reachable resources as routes
app = falcon.API()

# REST interfaces
#app.add_route('/getConf/{psa_id}/{conf_id}', psaIntfc)

#new
app.add_route('/' + str(conf.PSA_API_VERSION) + '/getConf/{psa_id}', psaIntfc)
#app.add_route('/psa_up/{psa_id}', psaIntfc)
app.add_route('/dumpLogFile', dumpLog)

#Legacy support
app.add_route('/getConf/{psa_id}', psaIntfc)

# management interfaces
# requests to the Orchestrator

# first request profile type
orchReply = profPars.requestProfileType()

# pars profile type and generates the TVD service graph
try:
	profPars.parsProfile(orchReply)
except Exception as exc:
	logging.exception("Exception in parsProfile:" + str(exc))

