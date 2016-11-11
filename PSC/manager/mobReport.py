'''   

    File:       mobReport.py
    Created:    1/9/2015
  
    @author:    UPC
  
    Description:
        This Module handles the mobility of the nodes by accepting the
        reporting of AP data, returning whether the system needs to migrate
        or not. It handles too the possibility to force the migration.

'''
import falcon
import json

force = False
 
class mobReport:

	def getStrongestAP(self,aps,strongestSignal, handOver,newAPbssid):
		print "HandOver just al entrar: " + str(handOver)
		print "strongestSignal: " + str(strongestSignal)
		for ap in aps:
			print ap["ssid"] + " " + ap["bssid"] + " " + str(ap["signal"])
			if(ap["signal"] > strongestSignal):
				print "Es millor!"
				handOver = True
				newAPbssid = ap["bssid"]
				strongestSignal = ap["signal"]
		return handOver,newAPbssid
		

	'''	Takes the report JSON and checks if there is a strongest access 
		point to connect. 
		Also forms the response JSON to send to the client. 
		If the force flag is enabled, it forces the hand over to the 
		next secured AP available
	'''

	def processReport(self,req):
		global force
		error = False
		errorMessage = ""
		try:
			report = json.loads(req.stream.read())
		except:
			error = True
			errorMessage = "Report JSON Malformed"		
		
		currentConnection = report["currentConnection"]
		aps = report["ap-list"]
		if(aps):
			if(currentConnection):
				print "Connected to " + currentConnection["bssid"]
				currentAP = [ap for ap in aps if ap["bssid"] == currentConnection["bssid"]]
				if(force):
					print "Hand Over was forced. Searching the next secured access point..."
					handOver = True
					if(currentAP):
						newIndex = (aps.index(currentAP[0]) + 1) % len(aps)
						newAPbssid = aps[newIndex]["bssid"]	
					else:
						newAPbssid = aps[0]["bssid"]
					force = False
				else:
					strongestSignal = 0
					handOver = False
					newAPbssid = ""
					if(currentAP):
						currentAP = currentAP[0]
						strongestSignal = currentAP["signal"]				
					else:
						handOver = True
						strongestSignal = aps[0]["signal"]			
						newAPbssid = aps[0]["bssid"]
					print "HandOver abans de mirar: " + str(handOver)
					handOver, newAPbssid = self.getStrongestAP(aps,strongestSignal, handOver,newAPbssid)		
					
			else:
				handOver = True
				strongestSignal = aps[0]["signal"]
				newAPbssid = aps[0]["bssid"]
				handOver, newAPbssid = self.getStrongestAP(aps,strongestSignal, handOver, newAPbssid)	

		else:
			error = True
			errorMessage = "Secured access points list is empty"

		responsejson = {}
		if(not error):
			if(handOver):
				print "Hand Over needed. The best signal access point bssid is: " + ap["bssid"]
				responsejson["action"] = 1
				responsejson["bssid"] = newAPbssid            
			else:
				print "Hand Over not needed."
				responsejson["action"] = 0
		else:
			print "ERROR: " + errorMessage
			responsejson["action"] = 2
			responsejson["error"] = errorMessage
		return responsejson

	def on_put(self, req, resp):
		
		responsejson = self.processReport(req)	
		resp.body = json.dumps(responsejson)
 
class forceHandOver:

	'''	Handles the force hand over petition'''

	def on_get(self, req, resp):

		global force
		force = True
		resp.body = "Hand Over Forced."

