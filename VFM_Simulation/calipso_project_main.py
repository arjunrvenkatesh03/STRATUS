#this will be the main file where everything is run from.

#Section to import all the libraries needed for the project
import numpy as np
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import pyhdf
from pyhdf.SD import SD, SDC
from matplotlib import colors

#section to pull the functions from the other modules that make up this project
from VoxelHomogenization import homogenize_array_size
from Visualizer import visualise_data
from Parser import parse_hdf_file
from PointsSampler import generate_coordinate_pairs
from BresenhamAlg import bresenham_line, is_clear_path
#from PointsSampler import sample_points

# Specify the HDF file.
# file_directory = "C:/Users/ga10027553/OneDrive - General Atomics/Desktop/ga_repo/VFM_Simulation/CALIPSO_VFM_Data/"
# filename = file_directory + "CAL_LID_L2_VFM-Standard-V4-20.2014-06-12T03-58-02ZD_Subset.hdf"
# filepath = os.path.abspath(filename)
# print(filepath)

#section to define the main function that will be run
def main(filename):
    #call file parser function to get the three data arrays
    lowAlt_data, midAlt_data, highAlt_data, minLat, maxLat, minLong, maxLong, minTime, maxTime, daynightFlag = parse_hdf_file(filename)

    #call the function to generate the random points to be used to sample the paths through the 3D matrix representing real space
    #first for this part of the project we only care if the voxel is cloud or not
    

    #call the voxel homogenization function to homogenize the voxel size of the three data arrays
    lowAlt_data = homogenize_array_size(lowAlt_data,"low")
    midAlt_data = homogenize_array_size(midAlt_data,"mid")
    highAlt_data = homogenize_array_size(highAlt_data,"high")
    formattedData = np.concatenate((highAlt_data, midAlt_data, lowAlt_data), axis=1)

    # Create a mask: 1 where array is 7, the low/no confidence flag value
    mask = np.where(formattedData == 7, 1, 0)
    
    # Sum up the masked array to count values less than -10
    error_count = np.sum(mask)
    print(error_count)

    #make a copy of the cloud data to filter out locations of clouds (=2)
    cloudData = formattedData.copy()
    cloudData[cloudData != 2] = 0
    cloudData[cloudData == 2] = 1
    np.rot90(cloudData)

    plt.imshow(cloudData, cmap="viridis")
    plt.show()

    #call the function to generate the random points to be used to sample the paths through the 3D matrix representing real space
    #for now have hard-coded altitude values, will change this later to have a JSON setting file or something, same thing with the number of samples (ideally some sort of convergence thing)
    sourceAlt = 800
    destAlt = 1020
    #num_paths = 1000

    #Simulate paths through the 3D matrix until the % of paths that are clear has converged to some solution within some tolerance
    convergenceBound = True
    totalClearPaths = 0
    totalPaths = 0
    while convergenceBound:

        num_paths = 1000
        coordinate_pairs_list = generate_coordinate_pairs(sourceAlt, destAlt, cloudData.shape[0], num_paths)
        num_clear_paths = 0
        for pair in coordinate_pairs_list:
            if not is_clear_path(cloudData, pair):
                num_clear_paths += 1


        if totalPaths == 0:
            totalPaths += num_paths
            totalClearPaths += num_clear_paths
            continue

        # if totalPaths > 20000:
        #     print("Convergence not reached in 20000 iterations")
        #     break

        else:
            previousClearedPaths = totalClearPaths
            previousTotalPaths = totalPaths
            totalPaths += num_paths
            totalClearPaths += num_clear_paths
            
            #calculate if the % of cleared paths has converged to within some tolerance
            prevSuccessRate = (previousClearedPaths / previousTotalPaths) * 100
            successRate = (totalClearPaths / totalPaths) * 100
            if abs(successRate - prevSuccessRate) < 0.1:
                if totalPaths < 300:
                    continue
                else:
                    convergenceBound = False
                    break


    #the successRate variable should now be the converged value of the % of paths that are clear
    #print(f"In {totalPaths} iterations, {successRate}% of paths did not encounter clouds")


    #call the function to visualize the data
    #visualise_data(filename,formattedData[:,800:1020]) #Note the tags and labels are not yet formatted correctly, displays bits still (but underlying data visualization is correct (i think))
    latRange = [minLat, maxLat]
    longRange = [minLong, maxLong]
    timeRange = [minTime, maxTime]
    return totalPaths, successRate, latRange, longRange, timeRange, daynightFlag

#main(filename)

#section to do any neccasary File I/O  such as a text file characterizing a region and time of interest


