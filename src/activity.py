import os
import numpy
import matplotlib.pyplot as plt
import time
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from std import std
from zfdict import zfdict
from units import units
from read_config import read_config
from read_input import read_input
from log import log
from exyz import exyz
from srim_plot import srim_plot
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
    print("Loading isotopes...", end="")
    isotopes.load_data(g.dirs['isotopes'])
    print("complete.")
    
    # Start tendl xs
    print("Loading xs data...", end="")
    log.log("Loading isotope tendl xs")
    tendl.load(g.dirs['xs'])
    log.log("Load complete")
    print("complete.")
    
    # Load all exyz files
    print("Loading exyz data...", end="")
    exyz.load()
    print("complete.")
    
    # Run Sim
    sim.run()
    
    print()
    print("Run Time: ", '{:7.3f}'.format(time.time() - start_time) + "s")
    print()
    
    
    
    










