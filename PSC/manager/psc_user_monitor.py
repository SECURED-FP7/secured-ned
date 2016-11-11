''' 
	File:		psc_user_monitor.py   
	Created:	18/04/2015
	
	@author:	VTT
  
  	Description:
      	The WSGI app to be given to the HTTP proxy server (e.g. Gunicorn). 
      	Falcon is a web framework to manage WSGI interface and HTTP reply/responses       
'''

import falcon
import requests
import logging
import config
from psc_manager import psaManager
from psc_manager import PSCInfo
from psc_manager import PSAInfo
from mobReport import mobReport
from mobReport import forceHandOver
from dump_log_file import dumpLogFile
from mobReport import mobReport
from mobReport import forceHandOver

conf = config.Configuration()
logging.basicConfig(filename="PSC_User_Monitor.log",level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

logging.info("--------")
logging.info("PSC GUI init.")
logging.info("PSA-PSC API version: " + str(conf.PSA_API_VERSION))
logging.info("--------")

# classes instatiation
psa_manager = psaManager("-")
psc_info = PSCInfo(conf.PSC_LOG_PATH, conf.PSA_LIST_PATH, conf.PSA_LIST_ONLINE_PATH, conf.PSA_CONFIG_PATH, str(conf.PSA_API_VERSION), conf.PSA_STATUS_REQ_DELAY)
psa_info = PSAInfo(conf.PSA_CONFIG_PATH, conf.PSA_LIST_ONLINE_PATH, str(conf.PSA_API_VERSION))
dump_log = dumpLogFile()
mobReporting = mobReport()
forceHandOver = forceHandOver()

# start the HTTP falcon proxy and adds reachable resources as routes
app = falcon.API()

# REST interfaces for user actions from manager web site
app.add_route('/psc/', psa_manager)
app.add_route('/psc/{command}/', psc_info)
app.add_route('/psa/{command}/{psa_id}', psa_info)
app.add_route('/dumpLogFile/', dump_log)
app.add_route('/mobReport', mobReporting)
app.add_route('/forceHandOver', forceHandOver)

