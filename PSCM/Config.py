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
        config.read('pscm.conf')
        self._ORCHESTRATOR_LOCATION = config.get('configuration', 'orchestrator_location')
        self._USER_DATA_LOCATION = config.get('configuration', 'userDataLocation')
        self._LOGIN_PAGE_LOCATION = config.get('configuration', 'loginPageLocation')
        self._PSCM_VERSION = config.get('configuration', 'pscm_version')
        self._UPR_LOCATION = config.get('configuration', 'upr_location')
        self._USE_LOCAL_FILE = config.getboolean('configuration', 'use_local_file')

    @property
    def ORCHESTRATOR_LOCATION(self):
        return self._ORCHESTRATOR_LOCATION
    
    @property
    def LOGIN_PAGE_LOCATION(self):
        return self._LOGIN_PAGE_LOCATION

    @property
    def USER_DATA_LOCATION(self):
        return self._USER_DATA_LOCATION

    @property
    def PSCM_VERSION(self):
        return self._PSCM_VERSION

    @property
    def UPR_LOCATION(self):
        return self._UPR_LOCATION

    @property
    def USE_LOCAL_FILE(self):
        return self._USE_LOCAL_FILE

