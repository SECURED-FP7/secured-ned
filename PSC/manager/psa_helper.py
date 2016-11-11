#  
#   File: 	PsaHelper.py
#   
#   Description: Help functions
#

import json
import requests
import logging
import sys

class PsaHelper():
    def __init__(self, psa_api_version):
        self.PSA_API_VERSION = psa_api_version
        # Timeout for PSA communication in seconds
        self.time_out = 3.500
        logging.info("API version:" + self.PSA_API_VERSION)

    def try_load(self, ip, command):
        url = "http://" + ip +":8080/" + self.PSA_API_VERSION + "/execInterface/" + command
        try:
            resp = requests.get(url, timeout=self.time_out)
            if (resp.status_code == requests.codes.ok):
                print resp.text
                return resp.text
            else:
                print '{"psa_response":"error"}'
                return None
        except requests.exceptions.Timeout:
            print '{"psa_response":"time_out"}'
            return None
    
    def try_post_file(self, ip, command, filepath):
        url = "http://" + ip +":8080/" + self.PSA_API_VERSION + "/execInterface/" + command
        headers = {"Content-Type": "application/octet-stream"}
        try:
            with open(filepath, 'rb') as payload:            
                resp = requests.post(url, data=payload, headers=headers, timeout=self.time_out)
            
            if (resp.status_code == requests.codes.ok):
                print resp.text
                return resp.text
            else: 
                print '{"psa_response":"error"}'
        except requests.exceptions.Timeout:
            print '{"psa_response":"time_out"}'
            return None

    def try_post(self, ip, command, filepath):
        url = "http://" + ip +":8080/" + self.PSA_API_VERSION + "/execInterface/" + command
        headers = {"Content-Length": "0"}
        try:
            resp = requests.post(url, headers=headers, timeout=self.time_out)
            
            if (resp.status_code == requests.codes.ok):
                print resp.text
                return resp.text
            else: 
                print '{"psa_response":"error"}'
        except requests.exceptions.Timeout:
            print '{"psa_response":"time_out"}'
            return None

    def try_put(self, ip, command, filepath):
        url = "http://" + ip +":8080/" + self.PSA_API_VERSION + "/execInterface/" + command
        headers = {"Content-Type": "text/x-shellscript"}
        try:
            with open(filepath, 'rb') as payload:            
                resp = requests.put(url, data=payload, headers=headers, timeout=self.time_out)
            
            if (resp.status_code == requests.codes.ok):
                print resp.text
                return resp.text
            else: 
                print '{"psa_response":"error"}'
        except requests.exceptions.Timeout:
            print '{"psa_response":"time_out"}'
            return None

