'''   

    File:       utils.py
    Created:    16/02/2015
  
    @author:    BSC, Francesco Ciaccia
  
    Description:
        Utility functions for general OS operations management 

'''

import os, errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
