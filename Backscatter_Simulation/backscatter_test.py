#test python file to get the visualisation and parsing modules working for the LIDAR backscattering data

import os
import numpy as np
from numpy import ma
from scipy import interpolate
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.colors as mcolors

from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *

# def parse_colormap(filename):
#     with open(filename, 'r') as f:
#         lines = f.readlines()
        
#     #color_lines = lines[lines.index('COLORS\n')+1:]  # extract lines after 'COLORS'
#     rgb_values = [list(map(int, line.split())) for line in lines]  # convert to list of RGB values
#     rgb_values = np.array(rgb_values)  # convert list of lists to numpy array
#     for i in range(len(rgb_values)-1):
#         for j in range(0,3):
#             rgb_values[i][j] = rgb_values[i][j] / 255.0

#     rgb_values = rgb_values[0:-1]
#     print(len(rgb_values))
#     return ListedColormap(rgb_values)

# # load colormap from the cmap file
# colormap = 'calipso-backscatter.cmap'
# custom_cmap = parse_colormap(colormap)

filename = "CAL_LID_L1-Standard-V4-51.2020-10-20T05-10-45ZD_Subset.hdf"
# Specify the HDF file.
file_directory = "C:/Users/ga10027553/OneDrive - General Atomics/Desktop/ga_repo/Backscatter_Simulation/CALIPSO_L1_Data"
filepath = file_directory + "/" + filename

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
print(alt.shape)

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
    """
    This function will average lidar data for N profiles.
    Inputs: 
        data - the lidar data to average. Profiles are assumed to be stored in columns and to be a masked array.
        N    - the number of profile to average

    Outputs:
        out - the averaged data array.

    """
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
print(latitude.shape)

print(data.shape)
avg_dataset = avg_horz_data(data, averaging_width)
print(avg_dataset.shape)
avg_dataset = np.clip(avg_dataset,0,0.11)

# colormap = 'calipso-backscatter.cmap'
custom_cmap_filename = "calipso-backscatter.cmap"
custom_cmap_filepath = os.path.abspath(custom_cmap_filename)
custom_cmap = mcolors.ListedColormap(np.loadtxt(custom_cmap_filepath)/255.0)
# print(custom_cmap)

levs = [0.0001,0.0002,0.0003,0.0004,0.0005,0.0006,0.0007,0.0008,0.0009,0.001,0.0015,0.002,0.0025,0.003,0.0035,0.004,0.0045,0.005,0.0055,0.006,0.0065,0.007,0.0075,0.008,0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1]
# print(len(levs))


norm = mcolors.BoundaryNorm(levs, custom_cmap.N) #seems like the cmap


# Create contour plot
plt.contourf(latitude, alt, avg_dataset,levels=np.linspace(0, 0.11, 1000),cmap=custom_cmap,norm=norm)
plt.colorbar(spacing='uniform')
plt.ylim(0,40)
plt.show()