#parser

import os
import numpy as np
from numpy import ma
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors

from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *

def parse_hdf_file(filepath):
    # Identify the data field.
    DATAFIELD_NAME = 'Total_Attenuated_Backscatter_532'

    hdf = SD(filepath, SDC.READ)
    # print(hdf.datasets().keys())

    hdfFile = HDF(filepath, HC.READ)
    vs = hdfFile.vstart()
    vd = vs.attach('metadata')
    rec = vd.read()
    alt = rec[0][-2]
    alt = np.array(alt)
    alt = alt[::-1]

    vd.detach()
    vs.end()
    hdfFile.close()

    # Read dataset.
    tempData = hdf.select(DATAFIELD_NAME).get()
    data = np.stack(tempData)
    data = np.rot90(data)
    # Mask missing values.
    #data = np.ma.masked_equal(data, -9999)

    def replace_values(array, value, replacement):
        array[array == value] = replacement
        return array

    data = replace_values(data, -9999, 0)

    #function to average the horizontal data to fit the desired data size
    def avg_horz_data(data, N):
        nAlts = data.shape[0]
        nProfiles = data.shape[1]                                                  

        nOutProfiles = latitude.shape[0]
        out = np.zeros((int(nAlts), int(nOutProfiles)))
    
        for i in range(0, int(nOutProfiles) - 1): 
            out[:, i] = ma.mean(data[:, i*N:(i+1)*N - 1], axis=1)  
    
        return out

    # #extract the latitude and longitude data
    latitude = hdf.select('Latitude').get()
    longitude = hdf.select('Longitude').get()
    latitude = np.hstack(latitude).flatten()
    longitude = np.hstack(longitude).flatten()

    x1 = 0
    x2 = len(longitude)
    averaging_width = int((x2-x1)/1000)
    if averaging_width < 5:
        averaging_width = 5
    if averaging_width > 15:
        averaging_width = 15

    latitude = latitude[::averaging_width]

    avg_dataset = avg_horz_data(data, averaging_width)
    avg_dataset = np.clip(avg_dataset,0,0.11)

    highAlt = avg_dataset[0:33,:]
    midAlt = avg_dataset[33:88,:]
    lowAlt = avg_dataset[88:288,:]
    highSurf = avg_dataset[288:578,:]
    lowSurf = avg_dataset[578:,:]

    return highAlt, midAlt, lowAlt, highSurf, lowSurf, latitude, longitude, alt

# filename = "CAL_LID_L1-Standard-V4-51.2020-10-20T05-10-45ZD_Subset.hdf"
# file_directory = "C:/Users/ga10027553/OneDrive - General Atomics/Desktop/ga_repo/Backscatter_Simulation/CALIPSO_L1_Data/"
# filepath = file_directory + filename
# parsedData = parse_hdf_file(filepath)
# for data in parsedData:
#     print(data.shape)