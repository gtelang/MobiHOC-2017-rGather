#!/home/gaurish/anaconda2/bin/python2
import rGather as rg
import utilities as ut
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
import yaml
import sys
import argparse
from termcolor import colored

def trajectories_compare_max_and_90p_diameters ( data, fig, ax, core_output_file_name,
						 outfolder= './figs/', outfile_extension='.eps'):

	""" Compare the max-diameters of clusters yielded by the two approximation 
	algorithms. Compare against the lower bound of the 2-Approximation.
	Use .eps, or .svg for vector ie. high-quality graphics.
	"""
	[rArray, diameters_2apx, diameters_4apx, d_r_max] = data

	# Title, legends and all that jazz
	ylabel     = 'Max cluster diameter' # Max diameter of a cluster withing a set of clusters
	plot_title = '' #'Comparing 2-APX and 4-APX algorithms for Trajectories \n' + ylabel +  ' vs $r$'
	xlabel     = 'Clustering Parameter $r$'

	# fig save sizes: from here: http://stackoverflow.com/a/10262161/505306
	fig_length  = 14
	fig_breadth = 12

	# Size of tick numbers along x and y axes.
	xtick_size  = 27         ; xticks = rArray
	ytick_size = xtick_size  ; #yticks are set extracted *after* plotting takes place.
	
	# Axis limits(Lower)
	#M = max(  d_r_max + diameters_2apx + diameters_4apx  )
	#ymin = 1.0    ; plt.ylim((ymin, M))
	#ymax = 1.35 ; plt.ylim(ymax=ymax)

	# Label sizes
	xlabel_size = 34
	ylabel_size = xlabel_size
	labelpad    = 20

	# Title size of plot
	title_size  = 32 

	# Legend
	legend_2apx    = '$2$-APX'
	legend_4apx    = '$4$-APX'
	legend_d_r_max = '$d_r^{max}$'
	
	# Marker and line thickness
	markersize      = 18
	markeredgecolor = 'black'
	markeredgewidth = 2
	linewidth       = 6

	# Marker
	m_2apx    = 's'
	m_4apx    = '*'
	m_d_r_max = 'o'

	#Line colors
	lc_2apx    = 'blue'
	lc_4apx    = 'red'
	lc_d_r_max = 'green'

	# Style
	ls_2apx   = 'solid'
	ls_4apx   = 'dashed'
	ls_d_r_max = ':'

	# grid
	grid_on = True
	grid_lc = 'gray'
	grid_ls = ':'

	fig.set_size_inches(fig_length, fig_breadth)
	ax.grid(b=grid_on)

	ax.plot(rArray, diameters_2apx , label =  legend_2apx,    linestyle = ls_2apx    ,
		marker = m_2apx    , markersize = markersize    , linewidth = linewidth, markeredgecolor = markeredgecolor, mew = markeredgewidth) 

	ax.plot(rArray, diameters_4apx , label =  legend_4apx,    linestyle = ls_4apx    ,
		marker = m_4apx    , markersize = markersize*1.6, linewidth = linewidth, markeredgecolor = markeredgecolor, mew = markeredgewidth)

	ax.plot(rArray, d_r_max        , label =  legend_d_r_max, linestyle = ls_d_r_max ,
		marker = m_d_r_max , markersize = markersize    , linewidth = linewidth, markeredgecolor = markeredgecolor, mew = markeredgewidth)

	# Set names
	ax.legend(loc='upper_left', markerscale=0.5, handlelength=4)
	ax.set_xlabel(xlabel, fontdict={'fontsize':xlabel_size}, labelpad = labelpad)
	ax.set_ylabel(ylabel, fontdict={'fontsize':ylabel_size}, labelpad = labelpad)
	ax.set_title(plot_title, fontdict={'fontsize':title_size})

	# Make the ticks larger than default
	plt.xticks(xticks, fontsize = xtick_size)
	plt.yticks(ax.get_yticks(), fontsize = xtick_size)


	# Save to disk
	fig.savefig( outfolder + core_output_file_name + outfile_extension )


def main():

	print "Hello World"
	print colored ("Started script", "magenta")
	#############################################################################
	# Read the data-file provided as command-line argument. Should be a YAML file
	#############################################################################
	with open( sys.argv[1], 'r') as stream:
		try:
			D = yaml.load( stream )
		except yaml.YAMLError as exc:
			print(exc)
		print "YAML read in successfully...."

	pointCloud = D[ 'coordinates' ] 
	rArray     = sorted( D['2-APX'].keys() ) # Same for both 2-apx and 4-apx
	numSamples = len(pointCloud[0]) # Each trajectory has the same number of samples.
	[rangemin, rangemax] = D['range']

	core_output_file_name = 'max_diameter_traj_clusters-' + \
				str(len(pointCloud))                + \
				str('_range-') + str(rangemin) + '-' + str(rangemax) +\
				'_samples-'  + str(numSamples)

	# Output of the two algorithms for the same set of cars
	diameters_2apx   = [ut.compute_max_cluster_diameter_trajectories( pointCloud, D['2-APX'][r]) for r in rArray]
	diameters_4apx   = [ut.compute_max_cluster_diameter_trajectories( pointCloud, D['4-APX'][r]) for r in rArray]
	d_r_max          = [ut.compute_max_over_rth_nearest_neighbors_trajectories( pointCloud, D['nbrTable_idx'], r) for r in rArray]

	fig, ax = plt.subplots()

	trajectories_compare_max_and_90p_diameters( data = [rArray, diameters_2apx, diameters_4apx, d_r_max],
						    fig = fig,
						    ax  = ax,
						    core_output_file_name = core_output_file_name)
	plt.show()


if __name__=="__main__":
	main()
