
#Section to import all the libraries needed for the project
import numpy as np
import os
from pyhdf.SD import SD, SDC

#section to define the function that parses the hdf file and returns the three data numpy arrays
def parse_hdf_file(filename):
    try:
        filepath = os.path.relpath(filename)
    except:
        print(filename)

    # Identify the data field.
    DATAFIELD_NAME = 'Feature_Classification_Flags'

    hdf = SD(filepath, SDC.READ)
            
    # Read dataset.
    data2D = hdf.select(DATAFIELD_NAME).get()
    data = data2D[:,:]
    data = np.stack(data)
    #print(data.shape)

    # Extract Feature Type only (1-3 bits) through bitmask.
    data = data & 7

    #We will read the data numpy array into three different arrays for each of the three altitude ranges -0.5 to 8.2 to 20.2 to 30.1 km.
    lowAlt_data = data[:,1165:5515]
    midAlt_data = data[:,165:1165]
    highAlt_data = data[:,0:165]

    #generate other "tags" for a specific file (time, data, etc.)
    timeStamp = hdf.select('Profile_UTC_Time').get()
    latitude = hdf.select('Latitude').get()
    longitude = hdf.select('Longitude').get()
    minLat, maxLat = float(min(latitude)), float(max(latitude))
    minLong, maxLong = float(min(longitude)), float(max(longitude))
    minTime, maxTime = timeStamp[0], timeStamp[-1]

    #work for formatting timestamp information
    minTime = str(minTime[0]).split(".")[0]
    maxTime = str(maxTime[0]).split(".")[0]

    #day night flag want to store as either all day (0) or all night (1) or mixed (2)
    daynightFlag = hdf.select('Day_Night_Flag').get()
    # if all values are zero
    if all(value == 0 for value in daynightFlag):
        daynightFlag = 0
    # if all values are one
    elif all(value == 1 for value in daynightFlag):
        daynightFlag = 1
    # if values are mixed
    else:
        daynightFlag = sum(daynightFlag) / len(daynightFlag)


    #parse time string from "yymmdd.ffffff" to "mm/dd/yy"
    minTime = str(minTime[2:4]) + "/" + str(minTime[4:6]) + "/" + str(minTime[0:2])
    maxTime = str(maxTime[2:4]) + "/" + str(maxTime[4:6]) + "/" + str(maxTime[0:2])



    return lowAlt_data, midAlt_data, highAlt_data, minLat, maxLat, minLong, maxLong, minTime, maxTime, daynightFlag