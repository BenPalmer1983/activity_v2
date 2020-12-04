################################################################
#    Main Program
#
#
#
#
################################################################

import os
import time
import datetime
import re
import sys
import shutil
import numpy 
import json
import zlib
from globals import g
from activity import activity

class main():

  def start():
  
    # RECORD START TIME
    g.times['start'] = time.time()
    
    now = datetime.datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    print(date_time)	
  
    activity.run()
    
    main.end()
      
  def end(): 
    # CLOSE LOG
    g.times['end'] = time.time()
    exit()


# Run
main.start()
