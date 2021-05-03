import os
import numpy
import matplotlib.pyplot as plt
import time
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
from std import std
from zfdict import zfdict
from units import units
from read_config import read_config
from read_input import read_input
from log import log
from exyz import exyz
from sim import sim
from beam import beam
from target import target
from isotopes import isotopes
from tendl import tendl

class activity:

  def run():
    
    log.log("Start")
    start_time = time.time()
    
    # Make output directories
    std.make_dir('output')
    
    # Load input file
    read_input.run()
    
    # Start isotopes
    isotopes.load_data(g.dirs['isotopes'])
    
    # Start tendl xs
    log.log("Loading isotope tendl xs")
    tendl.load(g.dirs['xs'])
    log.log("Load complete")
    
    # Load all exyz files
    exyz.load()
    
    # Run Sim
    sim.run()
    
    print()
    print("Run Time: ", '{:7.3f}'.format(time.time() - start_time) + "s")
    print()
    
    
    
    










