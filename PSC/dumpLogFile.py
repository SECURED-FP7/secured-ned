'''   

    File:       dumpLogFile.py
    Created:    17/12/2014
  
    @author:    BSC
  
    Description:
        REST resource to dump content of the log file from the PSC
        For development purpose only! Disable this in production (TBD)

'''
import falcon
import json


class dumpLogFile():

	def __init__(self):
		pass
		

	def on_get(self, req, resp):
		try:
			in_file = open("PSC.log","r")
			log = in_file.read()
			in_file.close()
			resp.status = falcon.HTTP_200
			resp.body = log
		except Exception as e:
			logging.exception(sys.exc_info()[0])
			resp.status = falcon.HTTP_501
    
	def on_get(self, req, resp):
		try:
			in_file = open("PSC.log","r")
			log = in_file.read()
			in_file.close()
			resp.status = falcon.HTTP_200
			resp.body = log
		except Exception as e:
			logging.exception(sys.exc_info()[0])
			resp.status = falcon.HTTP_501
