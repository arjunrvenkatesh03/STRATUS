import numpy as np
import matplotlib.pyplot as plt
from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *
from scipy import interpolate

# Specify the HDF file.
file_directory = "C:/Users/ga10027553/OneDrive - General Atomics/Desktop/ga_repo_temp/CALIPSO_extData/"
filename = "CAL_LID_L2_05kmAPro-Standard-V4-21.2022-01-13T04-09-53ZD_Subset.hdf"
filename = file_directory + filename
# Open the HDF file.
hdf = SD(filename, SDC.READ)
# Read the data.
data = hdf.select('Extinction_Coefficient_532').get()
data = np.clip(data,0,1.5)

#mask the data so that all values -9999 are set to 0
data[data == -9999] = 0

lat = hdf.select('Latitude').get()
lat = np.hstack(lat).flatten()

#interpolate the data to match the dimension of the lat array
interp_func = interpolate.interp1d(np.arange(N), data, axis=0, fill_value="extrapolate")

num_samples = data.shape[1]


#read altitude data from the metadata file
hdfFile = HDF(filename, HC.READ)
vs = hdfFile.vstart()
vd = vs.attach('metadata')
rec = vd.read()
# for i in range(len(rec[0])):
#     print(rec[0][i])
#     print("............................................................")
alt = rec[0][-1] #altitude from -0.5 km to 30.1 km split up into 399 bins
# print(len(rec[0][-1]))
vd.detach()
vs.end()
hdfFile.close()


#flip the data so that the altitude axis is increasing
# data = np.flip(data,1)
#determine if all the values in data are the same (note that axis are not yet actually sized correctly just to plot data)

plt.contourf(lat,alt,np.rot90(data),levels=100)
plt.colorbar()
plt.ylim(0,29.9)
plt.show()