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
from sklearn.neighbors import NearestNeighbors
import yaml

from matplotlib import rc
rc('font',**{'family':'serif','serif':['Helvetica']})
rc('text', usetex=True)


###############################################################################################################
#                                        PARSING COMMAND-LINE ARGUMENTS
###############################################################################################################

def argumentParser() :
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-rs'      , nargs='+', type=int , help='<Required> Clustering coefficient : r'                 , required=True)
    parser.add_argument('-range'   , nargs= 2 , type=int , help='<Required> Strt and ending cars from Shenzen data set', required=True)
    parser.add_argument('-samples'     , type=int , default=20 , help='Number of Samples')
    parser.add_argument('-time-of-day' , type=int , default=0  , help='Time of the day at which measurements of trajectories start, \
                                                                       or the coordinates of static point sets are recorded.')
    parser.add_argument('-input_file'    , type=str , default='shenzhen_9386.mat', help='Input File')
    parser.add_argument('-output_folder' , type=str , default='clusters', help='Output folder')
    
    # From here http://tinyurl.com/l9dghj7 # default analysis takes place for points.
    # Python has this extremely irritating feature, of not being able to accept boolean flags by default as 
    # described in my Stack Overflow question here: http://stackoverflow.com/q/41655897/505306
    isTrajectory = parser.add_mutually_exclusive_group(required = True) # This means you cannot use --points and --trajectories simultaneously.
    isTrajectory.add_argument('--trajectories', dest='isTrajectory', action='store_true')
    isTrajectory.add_argument('--points'      , dest='isTrajectory', action='store_false') 
    return parser



def  interpret_command_line_arguments(args, inputFile='shenzhen_9386.mat'):
	""" We are principally interested in the variables r, points(static) / trajectories, and lats and long variable.
        The rest of the body of this code-block is just setting up the file-reading below. 
	time_of_day represents the time at which coordinates were measured for static point sets 
        for trajectories it represents the time-stamp of the starting points of their trajectories. 
	"""
	#We can choose an arbitrary subset of cars. Specify the corresponding the column numbers in indicesOfCarsPlotted
	data                  = io.loadmat(inputFile)
	indicesOfCarsPlotted  = range(args.range[0], args.range[1]) # This can be an arbitrary selection of column indices if you wish
	rArray                = args.rs
	numCars               = len(indicesOfCarsPlotted) # Total number of cars selected to run the data on.
	all_lats              = data.get('lat')  # Latitudes of ALL cars in the data
	all_longs             = data.get('long') # Longitudes of ALL cars in the data
	time_of_day           = args.time_of_day
	
	if not args.isTrajectory : # This means we will be working with static point sets
	     lats        = all_lats  [ np.ix_( range(time_of_day, time_of_day + 1), indicesOfCarsPlotted) ]
	     longs       = all_longs [ np.ix_( range(time_of_day, time_of_day + 1), indicesOfCarsPlotted) ]
	     
             points = []
             for car in range(numCars): # Columns
                (x,y) = (lats[0][car], longs[0][car]) 
                points.append((x,y))
             points   = np.array(points)
	
	     return rArray, points, lats, longs

	else: # This means we will be working with trajectories
             numSamples = args.samples
 	     lats       = all_lats  [ np.ix_( range(time_of_day, time_of_day + numSamples), indicesOfCarsPlotted) ]
	     longs      = all_longs [ np.ix_( range(time_of_day, time_of_day + numSamples), indicesOfCarsPlotted) ]
	     
             trajectories = []
             for car in range(numCars): # Columns
                 trajectories.append([]) 
                 for t in range(numSamples): # Rows
                     (x,y) = (lats[t][car], longs[t][car])
                     trajectories[car].append((x,y))# Append the gps coordinate of 'car' at time 't' to its trajectory.
                 trajectories[car] = np.rec.array( trajectories[car], dtype=[('x', 'float64'),('y', 'float64')] )
             trajectories   = np.array(trajectories)
	
	     return rArray, trajectories, lats, longs






def dist_trajectories(p,q):
       dpq = 0
       for t in range(len(p)):
            # M is the euclidean distance between two points at time t.  
            M = np.sqrt( abs( (p[t][0]-q[t][0])**2 + (p[t][1]-q[t][1])**2 ) ) 
            if M > dpq:
                dpq = M
       
       return dpq



def compute_max_cluster_diameter_trajectories( pointCloud, clusterings ):
       diameters_of_clusters = []
       for cluster in clusterings:
	       diameter_cluster = 0
	       for i in cluster:
		       for j in cluster:
			       if j>i:
				     D = dist_trajectories( pointCloud[i], pointCloud[j] )
				     if D >= diameter_cluster:
					     diameter_cluster = D

	       diameters_of_clusters.append( diameter_cluster )			     

       return  max(diameters_of_clusters)  # np.percentile(diameters_of_clusters, 100) 


def compute_90p_cluster_diameter_trajectories( pointCloud, clusterings ):
       diameters_of_clusters = []
       for cluster in clusterings:
	       diameter_cluster = 0
	       for i in cluster:
		       for j in cluster:
			       if j>i:
				     D = dist_trajectories( pointCloud[i], pointCloud[j] )
				     if D >= diameter_cluster:
					     diameter_cluster = D

	       diameters_of_clusters.append( diameter_cluster )			     

       return np.percentile(diameters_of_clusters, 90)
	       



def compute_max_over_rth_nearest_neighbors_trajectories( pointCloud, nbrTable_idx, r ):

	num_points_metric_space = len(pointCloud)
	dist2rnearest = []
	
	for i in range(num_points_metric_space):
		current_point                   = pointCloud[i]
		r_farthest_nbr_of_current_point = pointCloud[ nbrTable_idx[i][r-1] ]  # Should this be r or r-1? 
		dist2rnearest.append(  dist_trajectories(current_point, r_farthest_nbr_of_current_point)   )
	return max( dist2rnearest )



def compute_90p_over_rth_nearest_neighbors_trajectories( pointCloud, nbrTable_idx, r ):

	num_points_metric_space = len(pointCloud)
	dist2rnearest = []
	
	for i in range(num_points_metric_space):
		current_point                   = pointCloud[i]
		r_farthest_nbr_of_current_point = pointCloud[ nbrTable_idx[i][r-1] ]  # Should this be r or r-1? 
		dist2rnearest.append(  dist_trajectories(current_point, r_farthest_nbr_of_current_point)   )
	return np.percentile( dist2rnearest, 90 )

