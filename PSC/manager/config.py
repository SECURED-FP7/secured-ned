import ConfigParser
import os
import copy


class Configuration(object):
    
    _instance = None
    #(fmignini) Not too meaningful use this var, I should change his name with something else like inizialized = False 
    _AUTH_SERVER = None
    
    def __new__(cls, *args, **kwargs):
        
        if not cls._instance:
            cls._instance = super(Configuration, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance 
    
    def __init__(self):
        #print 'Configuration - PATH : '+os.getcwd()
        path = copy.copy(os.getcwd())
        path_dirs = path.split("/")
        for path_dir in path_dirs:
            if path_dir == 'tests':
                self.test = True
            else:
                self.test = False
        #print self.test
        if self._AUTH_SERVER is None:
            self.inizialize()
    
    def inizialize(self): 
        config = ConfigParser.RawConfigParser()
        config.read('psc.conf')
        self._LOG_FILE = 'PSC.log'
        self._VERBOSE = 'true'
        self._DEBUG = 'true'
        self._PSA_CONFIG_PATH = config.get('configuration', 'psa_config_path')
        self._PSA_API_VERSION = config.get('configuration', 'psa_api_version')
        self._PSC_LOG_PATH = config.get('configuration', 'psc_log_path')
        self._PSA_LIST_PATH = config.get('configuration', 'psa_list_path')
        self._PSA_LIST_ONLINE_PATH = config.get('configuration', 'psa_list_online_path')
        self._PSA_STATUS_REQ_DELAY = config.get('configuration', 'psa_status_req_delay_secs')

    @property
    def LOG_FILE(self):
        return self._LOG_FILE

    @property
    def VERBOSE(self):
        return self._VERBOSE

    @property
    def PSA_API_VERSION(self):
        return self._PSA_API_VERSION

    @property
    def PSA_CONFIG_PATH(self):
        return self._PSA_CONFIG_PATH
    
    @property
    def PSC_LOG_PATH(self):
        return self._PSC_LOG_PATH
    
    @property
    def PSA_LIST_PATH (self):
        return self._PSA_LIST_PATH 
    
    @property
    def PSA_LIST_ONLINE_PATH(self):
        return self._PSA_LIST_ONLINE_PATH
    @property

    def PSA_STATUS_REQ_DELAY(self):
        return self._PSA_STATUS_REQ_DELAY


    
