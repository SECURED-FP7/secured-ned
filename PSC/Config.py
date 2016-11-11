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
        self._ORCHESTRATOR_ADDRESS = config.get('configuration', 'orchestrator_address')
        self._PSA_CONFIG_PATH = config.get('configuration', 'psa_config_path')
        self._PSC_VERSION = config.get('configuration', 'psc_version')
        self._PSA_API_VERSION = config.get('configuration', 'psa_api_version')

    @property
    def LOG_FILE(self):
        return self._LOG_FILE

    @property
    def VERBOSE(self):
        return self._VERBOSE

    @property
    def ORCHESTRATOR_ADDRESS(self):
        return self._ORCHESTRATOR_ADDRESS
    
    @property
    def PSA_API_VERSION(self):
        return self._PSA_API_VERSION

    @property
    def PSC_VERSION(self):
        return self._PSC_VERSION

    @property
    def PSA_CONFIG_PATH(self):
        return self._PSA_CONFIG_PATH
