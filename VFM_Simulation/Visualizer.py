
#Section to import all the libraries needed for the project
import numpy as np
from numpy import ma
import PointsSampler as sampler
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from pyhdf.SD import SD, SDC
from matplotlib import colors
from numba import njit
#section to do all the plotting of the data (can be made uncalled if not needed)
def visualise_data(filename, data):
    filepath = os.path.abspath(filename)

    # # Identify the data field.
    DATAFIELD_NAME = 'Feature_Classification_Flags'

    hdf = SD(filepath, SDC.READ)
            
    # # Read dataset.
    # data2D = hdf.select(DATAFIELD_NAME).get()
    # data = data2D[:,:]
    # data = np.stack(data)


    # Read geolocation datasets.
    latitude = hdf.select('Latitude').get()
    lat = latitude[:]
    lat = np.hstack(lat).flatten()

    new_indices = np.linspace(0, len(lat), data.shape[0])
    old_indices = np.arange(len(lat))
    lat = np.interp(new_indices, old_indices, lat)


    #number of samples is the y dimension of the data array --- which is already homogenized (should be 1020 for all VFM data)
    num_samples = data.shape[1]
    alt = np.zeros(num_samples)

    for i in range (0, num_samples):
        alt[i] = -0.5 + i*0.03
            
    #latitude, altitude = np.meshgrid(lat,alt)

    #create tempData, to see the parameters that Z is supposed to have for contourf to work
    #tempData = np.sin(np.sqrt(altitude**2 + latitude**2))
    #print(tempData.shape)

    # Extract Feature Type only (1-3 bits) through bitmask.
    #data = data & 7
    
    #horizontally average the data so that it is easier to see the features
    #function to average the horizontal data to fit the desired data size
    # def avg_horz_data(data, N):
    #     nAlts = data.shape[0]
    #     nProfiles = data.shape[1]                                                  

    #     nOutProfiles = latitude.shape[0]
    #     out = np.zeros((int(nAlts), int(nOutProfiles)))
    
    #     for i in range(0, int(nOutProfiles) - 1): 
    #         out[:, i] = ma.mean(data[:, i*N:(i+1)*N - 1], axis=1)  
    
    #     return out
    
    # data = avg_horz_data(data, )
    # print(data.shape)

    #For now we only care if the feature is a cloud (=2)
    # data[data > 2 ] = 0
    # data[data < 2 ] = 0
    # data[data == 2 ] = 1

    # Make a color map of fixed colors.
    #cmap = colors.ListedColormap(['white', 'blue', 'blue'])

    # Define the bins and normalize.
    bounds = np.linspace(0,2,3)
    #norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    long_name = 'Feature Type (Bits 1-3) in Feature Classification Flag'
    basename = os.path.basename(filename)
    plt.contourf(lat, alt, np.rot90(data), cmap='viridis')
    plt.title('{0}\n{1}'.format(basename, long_name))
    plt.xlabel('Latitude (degrees north)')
    plt.ylabel('Altitude (km)')
    plt.ylim(-0.5,30.1)
    plt.colorbar()

    fig = plt.gcf()
    plt.close()
    pngfile = "{0}.v.py.png".format(basename)
    fig.savefig(pngfile)


    