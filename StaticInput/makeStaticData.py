# Extract coordinates of a specified number of cars at any time of the day.
# and write them to file in the current directory.
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from scipy import io
import sys

# We can choose an arbitrary subset of cars. Specify the corresponding 
# the column numbers in indicesOfCarsPlotted
start = 3000
end = 3060
timeSliceIndex = 144 # there are 288 rows in the data-file

# Trajectory data from Shenzhen. Binary file in matlab
data = io.loadmat('finalShenzhen9386V6.mat')
#------------------------------------------------------------------

lats = data.get('lat')  # Latitudes
longs= data.get('long') # Longitudes

indicesOfCars  =  range( start , end )
f = open("shenzhenCars" + str(int(end-start)) + ".txt", "w")

numCars        =  len(indicesOfCars)
print "Writing to file"
for i, index in  zip(  range(len(indicesOfCars)), indicesOfCars  ):

    # Coordinates of car labelled index
    x = lats[timeSliceIndex][index]
    y = longs[timeSliceIndex][index]
    f.write( str(i+1) + ' ')
    f.write( str(x) + ' ')
    f.write( str(y) + '\n')
