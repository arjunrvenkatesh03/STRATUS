#main function for the backscatter simulation --- for now having the VFM simulation and backscatter simulation seperate

import numpy as np
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors
import time

from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *

from Parser import parse_hdf_file
from PixelHomogenizer import homogenize_pixels
from Sampler import generate_coordinate_pairs
from BresenhamAlg import bresenham_line



def main(filename):
    filepath = os.path.abspath(filename)
    print("Reading HDF file")

    #read the data from hdf file and parse it into a set of numpy arrays that can be used
    print("Parsing HDF file")
    highAlt, midAlt, lowAlt, highSurf, lowSurf, latitude, longitude, alt = parse_hdf_file(filepath)
    print("Homogenizing pixels")
    parsedData, interpolatedAlt = homogenize_pixels(highAlt, midAlt, lowAlt, highSurf, lowSurf, alt) #backscatter data interpolated such that the pixels are of the same size

    #call bresenham algorithm line function to find all the pixels that are along path connecting two sample points and sample a set amount of points
    print("Sampling points")
    numSamples = 100000
    coordinatePairs = generate_coordinate_pairs(400, 600, 50, 0,  lowAlt.shape[0], numSamples)

    print("Simulating paths through  matrix")
    paths = []
    for pair in coordinatePairs:
        source = pair[0]
        dest = pair[1]
        path = bresenham_line(source[0],source[1],dest[0],dest[1])
        paths.append(path)



    #visualize the data
    print("Visualizing data")
    custom_cmap_filename = "calipso-backscatter.cmap"
    file_directory = "C:/Users/ga10027553/OneDrive - General Atomics/Desktop/ga_repo/Backscatter_Simulation/"
    custom_cmap_filepath = file_directory + custom_cmap_filename
    custom_cmap = mcolors.ListedColormap(np.loadtxt(custom_cmap_filepath)/255.0)

    levs = [0.0001,0.0002,0.0003,0.0004,0.0005,0.0006,0.0007,0.0008,0.0009,0.001,0.0015,0.002,0.0025,0.003,0.0035,0.004,0.0045,0.005,0.0055,0.006,0.0065,0.007,0.0075,0.008,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1]
    norm = mcolors.BoundaryNorm(levs, custom_cmap.N) #seems like the cmap

    # Create contour plot
    print(latitude.shape)
    print(interpolatedAlt.shape)
    print(parsedData.shape)
    plt.contourf(latitude, interpolatedAlt, parsedData,levels=np.linspace(0, 0.11, 1000),cmap=custom_cmap,norm=norm)
    plt.colorbar(spacing='uniform')
    plt.ylim(0,30.1)
    plt.savefig('calipso-backscatter.png')





    return parsedData, interpolatedAlt, latitude, paths

filename = "CAL_LID_L1-Standard-V4-51.2020-10-20T05-10-45ZD_Subset.hdf"
file_directory = "C:/Users/ga10027553/OneDrive - General Atomics/Desktop/ga_repo/Backscatter_Simulation/CALIPSO_L1_Data/"
filepath = file_directory + filename
startTime = time.time()
parsedData, interpolatedAlt, latitude, paths = main(filepath)
endTime = time.time()
print("Time elapsed: " + str(endTime - startTime) + " seconds")
# print(parsedData.shape)
# print(interpolatedAlt.shape)
# print(latitude.shape)
# print(len(paths))
# totalHeight = 0
# for data in parsedData:
#     print(data.shape)
#     totalHeight += data.shape[0]

# print(totalHeight)