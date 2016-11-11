#
#   File:       psc_manager.py
#   Created:    18/04/2015
#   Author:     VTT
#
#   Description:
#       REST interface to PSC manager
#
import falcon
import json
import logging
import sys
import requests
import urllib2
import subprocess
from subprocess import check_output
from psa_helper import PsaHelper

# For PSA status monitoring
from time import sleep
import threading

class PSCInfo():
    def __init__(self, psc_log_path, psa_list_path, psa_list_online_path, confsPath, psa_api_version, psa_status_req_delay):
        self.psc_log_path = psc_log_path
        self.confsPath = confsPath
        self.PSA_API_VERSION = psa_api_version
        self.PSA_LIST_PATH = psa_list_path
        self.PSA_LIST_ONLINE_PATH = psa_list_online_path
        self.psaStatus = PSAStatus(psa_api_version, psa_list_online_path, psa_status_req_delay)
    
    def on_get(self, request, response, command):
        logging.info("GET: " + command)
        try:
            res = {}
            if command == "status":
                response.body = '{"status":"ok"}'
                response.set_header("Access-Control-Allow-Origin", "*")
                response.set_header("Access-Control-Allow-Methods", "*")
                response.set_header("Access-Control-Allow-Headers", "*")
                response.status = falcon.HTTP_200
                return
            elif command == "get-psa-statuses":
                res = self.psaStatus.get_psa_statuses()
            elif command == "get-user-ip":
                res["client_address"] = self.get_client_address(request.env)
            elif command == "get-psa-list":
                res["psa_response"] = self.get_psas()
            elif command == "get-psa-list-online":
                res["psa_response"] = self.get_psas_online()
            elif command == "dump-log-psc":
                response.body = self.get_psc_log()
                response.set_header("Content-Type", "text/plain; charset=UTF-8")
                response.status = falcon.HTTP_200
                return
            else:
                logging.info("GET: unknown command: " + command)
                response.set_header("Content-Type", "text/plain; charset=UTF-8")
                response.status = falcon.HTTP_404
                return
            
            response.body = json.dumps(res)
            #response.set_header("Accept", "application/json")
            response.set_header("Content-Type", "application/json")
            response.status = falcon.HTTP_200
        except Exception as e:
            logging.exception(sys.exc_info()[0])
            response.status = falcon.HTTP_501
    
    # Returns PSC's log
    def get_psc_log(self):
        logging.info("get psc log")
        try:
            in_file = open(self.psc_log_path, "r")
            log = in_file.read()
            in_file.close()
            return log
        except Exception as e:
            logging.exception(sys.exc_info()[0])
            return None
    
    # Get the list of PSAs received, i.e., user graph
    def get_psas(self):
        logging.info("get psas") 
        ret = "None"
        try:
            with open(self.PSA_LIST_PATH, 'rb') as f:
                psas = f.read()
                logging.info("psas:"+psas) 
                ret = psas    
        except IOError as exc:
            logging.error("Unable to read file " + self.PSA_LIST_PATH)
            raise exc
        return ret

    # Get currently online PSA's, i.e., what are up
    def get_psas_online(self):
        logging.info("get psas online") 
        ret = "None"
        try:
            with open(self.PSA_LIST_ONLINE_PATH, 'rb') as f:
                psas = f.read()
                logging.info("psas:"+psas) 
                ret = psas    
        except IOError as exc:
            logging.error("Unable to read file " + self.PSA_LIST_ONLINE_PATH)
            raise exc
        return ret

    def get_client_address(self,environ):
        try:
            return environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
        except KeyError:
            return environ['REMOTE_ADDR']

class PSAInfo():
    def __init__(self, confsPath, psa_list_online_path, psa_api_version):
        self.confsPath = confsPath
        self.PSA_API_VERSION = psa_api_version
        self.psaHelper = PsaHelper(self.PSA_API_VERSION)
        self.PSA_LIST_ONLINE_PATH = psa_list_online_path
    
    def on_get(self, request, response, command, psa_id):
        
        logging.info("GET: " + command + "/" + command)
        try:
            res = {}
            if command == "init":
                res["psa_response"] = self.post_psa_file("init", psa_id)
            elif command == "start":
                res["psa_response"] = self.post_psa("start", psa_id)
            elif command == "stop":
                res["psa_response"] = self.post_psa("stop", psa_id)
            elif command == "status":
                res["psa_response"] = self.try_psa("status", psa_id)
            elif command == "configuration":
                res["psa_response"] = self.try_psa("configuration", psa_id)
            elif command == "internet":
                res["psa_response"] = self.try_psa("internet", psa_id)
            # For getting logs from PSA
            elif command == "dump-log-psa-ctrl":
                response.body = self.get_psa_ctrl_log(psa_id)
                response.set_header("Content-Type", "text/plain; charset=UTF-8")
                response.status = falcon.HTTP_200
                return
            elif command == "get-log-psa":
                log = self.get_psa_log(psa_id)
                if log != None:
                    response.body = log
                    response.set_header("Content-Type", "text/plain; charset=UTF-8")
                    response.status = falcon.HTTP_200
                else:
                    response.status = falcong.HTTP_501
                return
            else:
                logging.info("GET: unknown command: " + command)
                response.set_header("Content-Type", "text/plain; charset=UTF-8")
                response.status = falcon.HTTP_404
                return
            
            response.body = json.dumps(res)
            #response.set_header("Accept", "application/json")
            response.set_header("Content-Type", "application/json")
            response.status = falcon.HTTP_200
            
        except Exception as e:
            logging.exception(sys.exc_info()[0])
            response.status = falcon.HTTP_501

    def get_psa_log(self, psa_id):
        print "get_psa_log"
        try:
            res = self.psaHelper.try_load(self.psa_get_ip(psa_id), "log")
            return res
        except Exception as exc:
            print exc

    def get_psa_ctrl_log(self, psa_id):
        print "get_psa_ctrl_log"
        try:
            res = self.psaHelper.try_load(self.psa_get_ip(psa_id), "dump-log-ctrl")
            return res
        except Exception as exc: 
            print exc

    def put_psa(self, command, psa_id):
        print "put_psa, command:" + command
        try:
            res = self.psaHelper.try_put(self.psa_get_ip(psa_id), command, self.confsPath + "/" + psa_id)
            return res
        except Exception as exc: 
            print exc
    
    def post_psa_file(self, command, psa_id):
        print "post_psa_file, command:" + command
        try:
            res = self.psaHelper.try_post_file(self.psa_get_ip(psa_id), command, self.confsPath + "/" + psa_id)
            return res
        except Exception as exc: 
            print exc
        print "post_psa_file done"
    
    def post_psa(self, command, psa_id):
        print "post_psa, command:" + command
        try:
            res = self.psaHelper.try_post(self.psa_get_ip(psa_id), command, self.confsPath + "/" + psa_id)
            return res
        except Exception as exc: 
            print exc
        print "post_psa done"
    
    
    def try_psa(self, command, psa_id):
        print "try_psa, command:" + command
        try:
            res = self.psaHelper.try_load(self.psa_get_ip(psa_id), command)
            return res
        except Exception as exc: 
            print exc

    def psa_get_ip(self, psa_id):
        ret = psa_id
        conf_str = ""
        try:
            #TODO: We don't have to read every time
            with open(self.PSA_LIST_ONLINE_PATH, 'rb') as f:
                conf_str = f.read()
            
            psa = json.loads(conf_str)
            logging.info(psa)
            for temp in psa:
                logging.info(temp)
                # TODO: Takes last PSA now..
                if temp["psa_id"] == psa_id:
                    ret = temp["ip"]
        except IOError as exc:
            logging.error("Unable to read file " + self.PSA_LIST_ONLINE_PATH)
            raise exc
        
        return ret

    def get_client_address(self,environ):
        try:
            return environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
        except KeyError:
            return environ['REMOTE_ADDR']

# Just for serving the web page, should refactor to another file
class psaManager():
    def __init__(self, confsPath):
        self.confsPath = confsPath
        self.loginPageLocation = "manager.html"

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

    def get_client_address(self,environ):
        try:
            return environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
        except KeyError:
            return environ['REMOTE_ADDR']

# For simple PSA status monitoring
class PSAStatus():
    def __init__(self, psa_api_version, psa_list_loc, psa_status_req_delay):
        self.psaHelper = PsaHelper(psa_api_version)
        self.PSA_LIST_LOC = psa_list_loc
        self.psa_status_req_delay = int(psa_status_req_delay)
        self.psa_list = []
        self.psa_status_list = []
        self.__start_status_monitor()

    def __start_status_monitor(self):
        self.event = threading.Event()
        self.th = threading.Thread(target=self.__check_psa_statuses, args=(self.psa_status_req_delay, self.event))
        self.th.start()

    def __load_psa_online_list(self):
        psas = None
        try:
            with open(self.PSA_LIST_LOC, 'rb') as f:
                psas = f.read()
                #logging.info("psas:"+psas) 
                self.psa_list = json.loads(psas)
        except IOError as exc:
            pass

    def __check_psa_statuses(self, delay, event):
        logging.info("check_psa_statuses()")
        while not event.isSet():
            try:
                #logging.info("checking statuses")
                # Just load everytime, if there's new PSAs
                #if len(self.psa_list) == 0:
                #TODO: could be modified, not efficient.
                self.__load_psa_online_list()
                temp_psa_status_list = []
                for psa in self.psa_list:
                    #logging.info("checking " + str(psa["psa_id"]))
                    psa_status = self.__try_psa("status", psa["ip"])
                    logging.info(str(psa["psa_id"]) + " status: " + str(psa_status))
                    # None == no reply, otherwise normal PSA reply is everything OK by PSA
                    if psa_status != None:
                        psa_status = json.loads(psa_status)["ret_code"]
                    temp_psa_status_list.append({"psa_id":psa["psa_id"], "status": psa_status})
                    #logging.info("------------")
                self.psa_status_list = temp_psa_status_list
            except Exception as exc:
                # In case of error, report everything bad
                self.psa_status_list = []
                pass
            sleep(delay)

    def __try_psa(self, command, psa_ip):
        #print "try_psa, command:" + command
        try:
            res = self.psaHelper.try_load(psa_ip, command)
            if res == None:
                logging.info("Error trying status of: " + psa_ip)
            return res
        except Exception as exc: 
            print exc
    
    # Public method called by PSC GUI
    def get_psa_statuses(self):
        #print "get_psa_statuses"
        return self.psa_status_list
