# A module containing helper functions for data-analysis, parsing command-line arguments etc.
# These contain mainly house-keeping and commonly used functions.
import rGather as rGather
import numpy as np
import matplotlib.pyplot as plt
import sys
from termcolor import colored
import argparse
import numpy as np, math
import sys, argparse, re
import matplotlib.animation as animation
import matplotlib as mpl, colorsys
from scipy import io
import os.path
from termcolor import colored


def argumentParser() :
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-r'       , type=int , default=2   , help='Minimum number of elements per cluster')
    parser.add_argument('-range'   , nargs=2  , type=int    , default=[9000, 9020], help='Ending Index from Shenzen data set')
    parser.add_argument('-samples' , type=int , default=20  , help='Number of Samples')
    return parser


def  interpretCommandLineArguments(args, inputFile='../DynamicInput/finalShenzhen9386V6.mat'):
	""" We are principally interested in the variables r, trajectories, and lats and long variable.
        The rest of the body of this code-block is just setting up the file-reading below. 
	"""
	#We can choose an arbitrary subset of cars. Specify the corresponding the column numbers in indicesOfCarsPlotted
	indicesOfCarsPlotted  = range(args.range[0], args.range[1]) # This can be an arbitrary selection of column indices if you wish
	numSamples            = args.samples # All_lats.shape[0] # Total number of GPS samples for each car. 
	r                     = args.r
	numCars               = len(indicesOfCarsPlotted) # Total number of cars selected to run the data on.
	data                  = io.loadmat(inputFile)
	all_lats              = data.get('lat')  # Latitudes of ALL cars in the data
	all_longs             = data.get('long') # Longitudes of ALL cars in the data
	lats                  = all_lats  [ np.ix_( range(0, numSamples), indicesOfCarsPlotted) ]
	longs                 = all_longs [ np.ix_( range(0, numSamples), indicesOfCarsPlotted) ]

        trajectories = []
        for car in range(numCars): # Columns
              trajectories.append([]) 
              for t in range(numSamples): # Rows
                  (x,y) = (lats[t][car], longs[t][car])
                  trajectories[car].append((x,y))# Append the gps coordinate of 'car' at time 't' to its trajectory.
              trajectories[car] = np.rec.array( trajectories[car], dtype=[('x', 'float64'),('y', 'float64')] )
        trajectories   = np.array(trajectories)

	return r, trajectories, lats, longs










def wrapperkeyPressHandler( fig, ax, run, lats, longs, interval_between_frames, keyStack=[] ): # the key-stack argument is mutable! I am using this hack to my advantage.
    def _keyPressHandler(event):
        if event.key in ['r', 'R']: # Signal to start entering an r-value

            run.clearComputedClusteringsAndR() # Neighbor map remain intact.
            keyStack.append('r')

        elif event.key in ['0','1','2','3','4','5','6','7','8','9'] and \
             len(keyStack) >= 1                                     and \
             keyStack[0] == 'r': # If the 'r'-signal has already been given, accept only numeric characters

             keyStack.append(event.key)
             print event.key

        elif event.key == 'enter': # Give the signal to interpret the numbers on the stack

           rStr = ''
           for elt in keyStack[1:]:
               if elt in ['0','1','2','3','4','5','6','7','8','9'] :
                   rStr += elt
               else:
                   break # You just hit an non-numeric character entered by mistake

           r = int(rStr)
           print "R-value interpreted: ", r
           keyStack[:] = [] # Empty for further integers.

           # Run the algorithm again, with the new r. 
           run.r = r
           run.generateClustersSimple( config ={'mis_algorithm':'networkx_random_choose_20_iter_best' } ) # Generate clusters. Each cluster center itself is a trajectory.
	   print "Computed Clusterings are ", run.computedClusterings
	   ax.cla() # Clear the previous canvas
           run.plotClusters( ax, trajThickness=2, markersize = 5 ) 

           fig.canvas.draw()

        elif event.key == 'a': 
		ax.cla()
		ax.set_xlim(ax.get_xlim()) # These axes limit setting lines are important. It freezes the axes limits forever. 
		ax.set_ylim(ax.get_ylim()) # Otherwise they keep getting updated dynamically.
		run.animateClusters(ax, fig, lats, longs, lineTransparency=1.0,  markersize=15, interval_between_frames=interval_between_frames)
		fig.canvas.draw()
                plt.show()

        elif event.key == 'b': 
		ax.cla()
		ax.set_xlim(ax.get_xlim()) # These axes limit setting lines are important. It freezes the axes limits forever. 
		ax.set_ylim(ax.get_ylim()) # Otherwise they keep getting updated dynamically.
		run.mkClustersEveryTimeStep(ax, fig, lats, longs, lineTransparency=1.0,  markersize=15, interval_between_frames=interval_between_frames)
		fig.canvas.draw()
                plt.show()

    return _keyPressHandler
