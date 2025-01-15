#function for parsing hdf file and returning the relevant data sets
from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *
import numpy as np
from scipy import interpolate
from geopy.distance import geodesic


def parse_hdf_file(filename):
    CPro_filename = filename
    # hdf_APro = SD(APro_filename, SDC.READ)
    hdf_CPro = SD(CPro_filename, SDC.READ)

    # Read the data. CPro is the cloud data, APro is the aerosol data (if you want to use both just add the two arrays together)
    # data532 = hdf_APro.select('Extinction_Coefficient_532').get()
    data532_CPro = hdf_CPro.select("Extinction_Coefficient_532").get()


    #calculate how many total flag values are in the path array
    flagCount_532 = np.sum(np.where(data532_CPro == -333.0)) + np.sum(np.where(data532_CPro == -444.0))
    #flagCount_1064 = np.sum(np.where(data1064 == -333.0)) + np.sum(np.where(data1064 == -444.0))

    # data532 = np.clip(data532, -5555.0, 10)
    data532_CPro = np.clip(data532_CPro, -5555.0, 10)

    data532 = data532_CPro

    #data532 = np.clip(data532,0,1.5)
    #data532 = np.rot90(data532)
    dataUnc532 = hdf_CPro.select("Extinction_Coefficient_Uncertainty_532").get()

    # Read the data.
    #data1064 = hdf.select('Extinction_Coefficient_1064').get()
    #data1064 = np.clip(data1064,0,1.5)
    #data1064 = np.rot90(data532)
    #dataUnc1064 = hdf.select("Extinction_Coefficient_Uncertainty_1064").get()

    #mask the data so that all values -9999 are set to 0
    # data532[data532 == -9999] = 0
    # data1064[data1064 == -9999] = 0

    lat = hdf_CPro.select('Latitude').get()
    lat = np.hstack(lat).flatten()
    long = hdf_CPro.select('Longitude').get()
    long = np.hstack(long).flatten()

    #interpolate the data to match the dimension of the lat array
    # create an array of indices for your original array
    # indices = np.arange(data.shape[0])
    # # create an array of indices for your larger array
    # new_indices = np.linspace(0, data.shape[0]-1, lat.shape)
    # # create a placeholder for your new, larger array
    # new_array = np.empty((X, 399))
    #loop over each colum in the array

    num_samples = data532.shape[1]


    #read altitude data from the metadata file
    hdfFile = HDF(CPro_filename, HC.READ)
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

    timeStamp = hdf_CPro.select('Profile_UTC_Time').get()

    #work for formatting timestamp information
    timeStamp = str(timeStamp[0]).split(".")[0]
    timeStamp = timeStamp[1:]
    #parse time string from "yymmdd.ffffff" to "mm/dd/yy"
    timeStamp = str(timeStamp[2:4]) + "/" + str(timeStamp[4:6]) + "/" + str(timeStamp[0:2])
    #startTime, endTime = timeStamp[0], timeStamp[-1]

    data1064 = 0
    dataUnc1064 = 0
    
    return data532, data1064, lat, long, alt, timeStamp, dataUnc532, dataUnc1064, flagCount_532

def lat_long_to_km(start_lat, start_long, end_lat, end_long):
    start_coordinates = (start_lat, start_long)
    end_coordinates = (end_lat, end_long)
    distance = geodesic(start_coordinates, end_coordinates).kilometers
    return distance
    #flip the data so that the altitude axis is increasing
    # data = np.flip(data,1)