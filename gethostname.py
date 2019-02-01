#!/usr/bin/env python
import sys
import os 
         
if os.path.isdir("/usr/lib/enigma2/python"):
        sys.path.append("/usr/lib/enigma2/python")
                                                  
try:
    import boxbranding
    print(boxbranding.getBoxType().strip())
    sys.exit(0)                                
except Exception, e:
    sys.exit(1)  