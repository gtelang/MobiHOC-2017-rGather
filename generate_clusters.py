#!/home/gaurish/anaconda2/bin/python2
# Example usage: python2 generateClusters.py  --trajectories -samples 2 -rs 4 5 6  -range 30 50  -time-of-day 144
# Example usage: python2 generateClusters.py  --points                   -rs 5 6 7 -range 40 50  -time-of-day 189
# ... note that the -samples flag will have no effect for the static-point set case, since the number of samples should anyway logically be 1
# Output files are generated automatically, depending on whether trajectories or points are passed.
# Look in utilities.py to see which variables you have set optional, and which are compulsory.

import rGather as rg
import utilities as ut
import numpy as np, sys, yaml
import matplotlib.pyplot as plt
from matplotlib import rc
from termcolor import colored
import json
from datetime import datetime

def clusters_using_2apx_and_4apx_algos( args, metric_space_points):
    """ Run the algorithms on the provided point-cloud and write to disk a YAML file
    clusters for different values of r for each algorithm. 

    The result is returned in the form of a dictionary, to the calling fucntion 
    which then writes it to disk.

    This function works well for trajectories and normal static point-clouds in R^2
    """

    # Initialize dictionary, to be written out to a YAML output file
    rArray = args.rs
    D = {}
    D['range']       = [args.range[0], args.range[1]] 

    # For trajectories in particular, this refers to the time of the day when first GPS point on them was recorded.
    # For static points this is just the time at which the GPS locations were recorded.
    D['Time of day'] = args.time_of_day 
    
    # This is important. otherwise YAML cannot serialize metric_space_points. For both 
    D['coordinates'] = [ pt.tolist()  for pt in metric_space_points ] 
    D['2-APX'] = {} # D['2-APX'][r] is the clustering on the point-cloud for the specified r.
    D['4-APX'] = {} # Ditto for 4-APX

    # Boolean: Check if the data-file contains trajectories or point-sets
    # Run the appropriate algorithms according to this case.
    isTrajectory = args.isTrajectory

    ##########################################################################################
    # :TODO:Do brute force neighbor search and detect the all-to-all neighbor distances.
    # :Then pass it to the clustering function. You need to rewrite there the part that
    # accepts a file containing neighbors and replace it with just a dumb precomputed neighbor set.
    ##########################################################################################
    
    # Generate clusters for each value of r for the point-cloud for both the 2-approx and the 4-approx.
    for i, r in enumerate(rArray):

	    if not isTrajectory: # The point-cloud is a collection of static points

		    run_2APX = rg.AlgoAggarwalStaticR2L2( r=r, pointCloud = metric_space_points )
		    run_2APX.generateClusters()
		    
		    run_4APX = rg.Algo_Static_4APX_R2_L2( r = r, pointCloud = metric_space_points )
		    run_4APX.generateClusters( config = {'mis_algorithm': 'networkx_random_choose_20_iter_best' } )

	    else:# The point-cloud is a collection of trajectories.:
		    
		    run_2APX = rg.AlgoJieminDynamic( r=r, pointCloud = metric_space_points )
                    run_2APX.generateClusters()

		    run_4APX = rg.Algo_Dynamic_4APX_R2_Linf( r = r, pointCloud = metric_space_points )
		    run_4APX.generateClusters( config = {'mis_algorithm': 'networkx_random_choose_20_iter_best' } )

	    D['2-APX'][r] = run_2APX.computedClusterings
	    D['4-APX'][r] = run_4APX.computedClusterings

	    # Remember that run_4APX.nbrTable_idx is of type [[Int]] for both trajectories and static points.
	    if i == 0 and isTrajectory: # this sectionary entry is computed exactly once.

		    #Indices r-th nearest neighborrs for each point, sorted by
		    # distance to that point. This is a collection of lists.
		    D['nbrTable_idx'] = {} 
		    for k in range(len(run_4APX.pointCloud)):
			    
			    # This is the same for both 2APX and 4APX across all r's for a point-cloud.
			    # It was used to speed up the neighbor search
			    D['nbrTable_idx'][k] = run_4APX.nbrTable_idx[k] 

			    # that's because indices are sorted by distance, and each point is its own nearest neighbor
			    assert( D['nbrTable_idx'][k][0] == k  )
    return D

def main():

	
	# Parse input arguments and extract data from input file
	#========================================================
	
	args      = ut.argumentParser().parse_args()
	input_file = args.input_file 
	output_folder = args.output_folder + '/' 
	time_of_day  = args.time_of_day

	# Depending on the command-line arguments just parsed, metric_space_points can be either points or trajectories
	[_, metric_space_points, _ , _] = ut.interpret_command_line_arguments( args, inputFile=input_file ) 

	
	# Generate Clusters
	#========================================================
	D = clusters_using_2apx_and_4apx_algos( args, metric_space_points )

	
	# Write dictionary to disk
	#========================================================
	if args.isTrajectory: # Trajectories. Mention the number of samples.
	
	    numSamples = len(metric_space_points[0]) # the length/number of GPS sample points per trajectory are the same
	    output_file = output_folder + 'traj-' + str(len(metric_space_points))           + \
	                  '_range-[' + str(args.range[0]) + '-' + str(args.range[1])  + ']' + \
			  '_samples-' + str(numSamples)  + '_tod-' + str(time_of_day) + '.yaml'
	    
	else: # static points

	    output_file = output_folder + 'staticPts-' + str(len(metric_space_points)) + \
			 '_range-[' + str(args.range[0]) + '-' + str(args.range[1])  + ']' +\
	                 '_tod-' + str(time_of_day) + '.yaml'
	    
	with open(output_file, 'w') as output_file_handle:
		output_file_handle.write( yaml.dump(D) )

	print colored("\n\n*******************************************************************************************", 'green')
	print colored("Clustering results written out to " + output_file, 'green')
	print colored("*******************************************************************************************", 'green')

if __name__ ==  '__main__':
	main()
