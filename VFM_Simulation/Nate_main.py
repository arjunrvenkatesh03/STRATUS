#Section to import all the libraries needed for the project
import numpy as np
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import pyhdf
from pyhdf.SD import SD, SDC
from matplotlib import colors
from numba import njit, jit

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
# @njit
@jit(nopython=True)
def calc_above_below(cloudData_rotated):
    x = cloudData_rotated.shape[1]
    # Use an integer array instead of boolean to ensure compatibility
    above_below_presence = np.zeros((1020, x, 2), dtype=np.int32)

    for altitude in range(1019, -1, -1):  # Start from the highest index, corresponding to the lowest altitude
        for index in range(x):
            # Check 'below', ensuring we don't go out of bounds (now 'below' is towards higher indices)
            if altitude < 1019:  # There's room below
                for i in range(altitude + 1, 1020):
                    if cloudData_rotated[i, index] == 1:
                        above_below_presence[altitude, index, 1] = 1  # '1' now corresponds to below
                        break

            # Check 'above', ensuring we don't go out of bounds (now 'above' is towards lower indices)
            if altitude > 0:  # There's room above
                for i in range(altitude - 1, -1, -1):
                    if cloudData_rotated[i, index] == 1:
                        above_below_presence[altitude, index, 0] = 1  # '0' now corresponds to above
                        break

    counts_above = np.sum(above_below_presence[:, :, 0], axis=1)  # Counts for 'above'
    counts_below = np.sum(above_below_presence[:, :, 1], axis=1)  # Counts for 'below'

    return counts_above, counts_below, x

#section to define the main function that will be run
def main(filename):
    # Call file parser function to get the three data arrays
    lowAlt_data, midAlt_data, highAlt_data, minLat, maxLat, minLong, maxLong, minTime, maxTime, daynightFlag = parse_hdf_file(filename)

    # Call the function to generate the random points to be used to sample the paths through the 3D matrix representing real space
    # For this part of the project, we only care if the voxel is cloud or not

    # Call the voxel homogenization function to homogenize the voxel size of the three data arrays
    lowAlt_data = homogenize_array_size(lowAlt_data, "low")
    midAlt_data = homogenize_array_size(midAlt_data, "mid")
    highAlt_data = homogenize_array_size(highAlt_data, "high")
    formattedData = np.concatenate((highAlt_data, midAlt_data, lowAlt_data), axis=1)

    # # Create a mask: 1 where array is 7, the low/no confidence flag value
    # mask = np.where(formattedData == 7, 1, 0)

    # # Sum up the masked array to count values less than -10
    # error_count = np.sum(mask)
    # print(error_count)

    # Make a copy of the cloud data to filter out locations of clouds (=2)
    cloudData = formattedData.copy()
    cloudData[cloudData != 2] = 0
    cloudData[cloudData == 2] = 1

    # Rotate the cloudData array 90 degrees twice and assign it back
    cloudData_rotated = np.rot90(cloudData, 3)
    print(cloudData_rotated.shape)

    # Display the rotated data
    # plt.imshow(cloudData_rotated, cmap="viridis")
    # plt.show()


    counts_above, counts_below, totalCount = calc_above_below(cloudData_rotated)
    # print(counts_above[0:10])
    # print(counts_above.shape)
    # print(counts_below.shape)
    # print(totalCount)

    # Display the rotated data
    # plt.imshow(cloudData_rotated)
    # plt.show()


    return counts_above, counts_below, totalCount
