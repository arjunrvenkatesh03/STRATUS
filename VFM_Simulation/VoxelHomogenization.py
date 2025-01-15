#script to take in the VFM numpy array and homogenize the voxel size so that Bresenham's line algorithm can be applied smoothly

#calipso VFM voxel size will be homogenized to the size of the smallest voxels in the dataset, which are those in the -0.5 to 8.2 km range

import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from pyhdf.SD import SD, SDC
from matplotlib import colors

#extra library to speed up base python code
from numba import njit

# # Specify the HDF file.
# file_directory = "C:/Users/ga10027553/OneDrive - General Atomics/Desktop/CALIPSO Project/CALIPSO Sample Data"
# filename = "CAL_LID_L2_VFM-Standard-V4-20.2014-06-12T03-58-02ZD_Subset.hdf"
# FILE_NAME = os.path.abspath(filename)
# #print(FILE_NAME)

# # Identify the data field.
# DATAFIELD_NAME = 'Feature_Classification_Flags'

# hdf = SD(FILE_NAME, SDC.READ)
        
# # Read dataset.
# data2D = hdf.select(DATAFIELD_NAME).get()
# data = data2D[:,:]
# data = np.stack(data)
# #print(data.shape)

# #We will read the data numpy array into three different arrays for each of the three altitude ranges -0.5 to 8.2 to 20.2 to 30.1 km.
# lowAlt_data = data[:,1165:5515]
# midAlt_data = data[:,165:1165]
# highAlt_data = data[:,0:165]


#size of the lowAlt voxels are 30m by 333m by whatever the longitude range is (don't think it matters as it should be the same for all three altitude ranges) (15 samples per 5km batch)
#size of the midAlt voxels are 60m by 1000m by whatever the longitude range is (5 samples per 5km batch)
#size of the highAlt voxels are 180m by 1667m by whatever the longitude range is (3 samples per 5km batch) ---- note all horizontal voxels in total added width are the same size (at 5 km total)

#this function makes use of scipy.ndimage zoom function --- you can look up the documentation for this function by typing in "scipy.ndimage.zoom" into google
def homogenize_array_size(array,altitudeBlock):
    #homogenizing the voxel size depends on the altitude range
    if altitudeBlock == "low":
        #reshape array
        array = np.reshape(array, (array.shape[0],15,290))

        #unravel array so that it has shape (15 * array.shape[0], 290)
        array = array.reshape(-1, 290)

        #this is the highest resolution data, so no need to resize/increase resolution
        resizedArray = array

    elif altitudeBlock == "mid":
        #need to reshape inputed data array to represent the array correspond to 3D space
        array = np.reshape(array,(array.shape[0],5,200))

        #create a blank array of the correct size to fill with the data that was previously contained in a lower resolution array
        resizedArray = np.zeros((array.shape[0],15,array.shape[2] * 2))

        #splice the data from the old array into the new array
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                for k in range(array.shape[2]):
                    value = array[i,j,k]
                    #fill a splice of the new array with the value of the old array --- note we don't have to worry about losing resolution because we are artificially increasing the resolution of the array i.e no data is added or lost it is just changed location in the array
                    try:
                        resizedArray[i, j * 3: j * 3 + 3, k * 2: k * 2 + 2] = value
                    except:
                        print("i: " + str(i) + " j: " + str(j) + " k: " + str(k))
        
        resizedArray = resizedArray.reshape(-1, 200 * 2)

    elif altitudeBlock == "high":
        #need to reshape inputed data array to represent the array correspond to 3D space
        array = np.reshape(array,(array.shape[0],3,55))

        #create a blank array of the correct size to fill with the data that was previously contained in a lower resolution array
        resizedArray = np.zeros((array.shape[0],15,array.shape[2] * 6))
 
        #splice the data from the old array into the new array
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                for k in range(array.shape[2]):
                    value = array[i,j,k]
                    try:
                        resizedArray[i, j * 5: j * 5 + 5, k * 6: k * 6 + 6] = value
                    except:
                        #this is for debugging purposes --- will be thrown if the array indexes are out of range. this most likely indicates that the data being pulled from the CALIPSO hdf files is of the incorrect class.
                        print("i: " + str(i) + " j: " + str(j) + " k: " + str(k))

        resizedArray = resizedArray.reshape(-1, 55 * 6)

    return resizedArray

# #generate the test arrays for each altitude range
# np.random.seed(0)

# # Generate the arrays
# array1 = np.random.randint(0, 100, (677, 15, 290))
# array2 = np.random.randint(0, 100, (677, 5, 200))
# array3 = np.random.randint(0, 100, (677, 3, 55))

# print(array1.shape)  # Prints: (677, 15, 290)
# print(array2.shape)  # Prints: (677, 5, 200)
# print(array3.shape)  # Prints: (677, 3, 55)

# Resize the test arrays
# resizedArray1 = homogenize_array_size(lowAlt_data, "low")
# print(resizedArray1.shape) # Prints: (677, 15, 290)
# resizedArray2 = homogenize_array_size(midAlt_data, "mid")
# print(resizedArray2.shape)  # Prints: (677, 15, 290)
# resizedArray3 = homogenize_array_size(highAlt_data, "high")
# print(resizedArray3.shape)  # Prints: (677, 15, 290)

# #now stack the three arrays that 
# homogenizedArray = np.concatenate((resizedArray1,resizedArray2,resizedArray3),axis=2)
# print(homogenizedArray.shape) # Prints: (677, 15, 1020)