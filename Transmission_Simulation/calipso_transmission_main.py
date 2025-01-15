#main file for the transmission simulation

import numpy as np
import os
import matplotlib.pyplot as plt
from numba import njit
from geopy.distance import geodesic

from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *

from Parser import parse_hdf_file, lat_long_to_km
from Sampler import generate_coordinate_pairs
from BresenhamAlg import bezier_curve
from wavelengthDependence import wavelength_dependence_extCoef


def main(filepath, sourceAlt):
    
    #parse hdf file to get desired datasets
    data532, data1064, latitude, longitude, altitude, timeStamp, data532_Unc, data1064_Unc, flagCount_532 = parse_hdf_file(filepath)
    
    #calculate pixel width from latitude and longitude
    startLat, endLat = latitude[0], latitude[-1]
    startLong, endLong = longitude[0], longitude[-1]
    pixelWidth = lat_long_to_km(startLat, startLong, endLat, endLong) / data532.shape[1]


    # data532 = np.rot90(data532)
    # data1064 = np.rot90(data1064)
    #call bresenham algorithm line function to find all the pixels that are along path connecting two sample points and sample a set amount of points
    #print("Sampling Paths")
    #Altitude conversion ft to index in the data array
    #10K ft = 40
    #20K ft = 80
    #30K ft = 120
    #40K ft = 160
    #50K ft = 200
    #60K ft = 240

    # sourceAlt = 240
    # destAlt = 240

    #Some simulation parameters
    sourceAlt = sourceAlt
    destAlt = sourceAlt
    num_paths = 1000
    std_dev = 3
    min_seperation = 8
    max_seperation = 12
    #data532 = np.rot90(data532)
    #data1064 = np.rot90(data1064)

    # print(data532.shape)
    # print(data1064.shape)

    #generate the coordinate pairs for each of the paths
    coordinatePairs = generate_coordinate_pairs(sourceAlt, destAlt, std_dev, 0, data532.shape[0] - 1, num_paths, min_seperation, max_seperation)
    #generate a list that stores the dx,dy for each coordinate pair in coordinatePairs
    #differences = []
    # print(coordinatePairs[0:10])
    # print(data532.shape)


    # for pair in coordinatePairs:
    #     x_diff = abs(pair[1][0] - pair[0][0])
    #     y_diff = abs(pair[1][1] - pair[0][1])
    #     x_diff = x_diff * 0.06
    #     y_diff = (abs(endLat - startLat) * pixelWidth)

    #     difference = np.sqrt(x_diff**2 + y_diff**2)
    #     differences.append(difference)

    #generate the paths through data array connecting each coordinate pair
    pathArray = []
    error_count = 0
    #print("Simulating paths through 532 matrix")
    for pair in coordinatePairs:
        #generate path 
        # print(pair)
        # print(data532.shape)
        path = bezier_curve(pair)
        #path = bresenham_line(data532,pair)

        #check if path is not an empty list (return condition for minimum path length)
        if path.shape[0] <= 1:
            continue

        pathArray.append(path)

    # print(pathArray[0])
    # Create a mask: 1 where array is less than -10, 0 otherwise
    # mask = np.where(abs(data532) < 300, 1, 0)
    # mask_333 = np.where(data532 == -333.0, 1, 0)
    # mask_444 = np.where(data532 == -444.0, 1,0)

    # flagCount_532 = np.sum(mask_333) + np.sum(mask_444)
    # flagCount_1064 = flagCount_532
    
    # print(flagCount_532)
    # Sum up the masked array to count values less than -10
    # error_count += np.sum(mask)
    # temp_error_count = np.sum(mask)
    # print(temp_error_count)


    pathArray532 = pathArray
    pathArray1064 = pathArray
    # print(pathArray532)
    # print(pathArray1064)
    #print(pathArray532 != pathArray1064) #test to show if the two path arrays are the same (they should be so this should print False)

    #once the coordinate path is generated, we can calculate the attenuation as a percentage of the original signal using the Beer-Lambert Law A = eL so I/I0 =10^(-eL)
    #print("Calculating Extinction Coefficients")
    #pathLength = 3.879 #km average path length through pixel (formula based on size of pixel)
    #calculate the attenuation for each path

    data532 = np.rot90(data532)
    #data1064 = np.rot90(data1064)
    data532 = np.rot90(data532)
    #data1064 = np.rot90(data1064)

    # pathArray532 = [lst for lst in pathArray532 if lst]
    # pathArray1064 = [lst for lst in pathArray1064 if lst]
    
    pathLengthList = []

    # data532 = np.rot90(data532)
    # data1064 = np.rot90(data1064)
    # data532 = np.clip(data532,0,5)
    # data1064 = np.clip(data1064,0,5)
    #plt.imshow(data532)
    #plt.imshow(data1064)
    #plt.show()
    #print(data.shape)
    extincCoefList532 = []
    extincCoefList1064 = []
    extCoefUncList_532 = []
    extCoefUncList_1064 = []
    flagCount_532 = 0

    extincCoef532 = 0
    extincCoef1064 = 0
    extCoefUnc_532 = 0
    extCoefUnc_1064 = 0
    #print(data532.shape)


    #calculate the effective extinction coefficient for each path
    for path in pathArray532:

        flagCounter = 0

        for i,j in path:

            #finding attenuation for multiple sections with different extinc coef is the same as adding up all the ectinc coeff
            extincCoef = data532[i,j]

            if extincCoef < 0:

                if flagCounter == 0:
                    flagCount_532 += 1
                    flagCounter = 1

                extincCoef = 0

            extincCoef532 += extincCoef


            

            #extincCoef1064 += data1064[i,j]
            extCoefUnc_532 += data532_Unc[i,j]
            #extCoefUnc_1064 += data1064_Unc[i,j]
        
        extincCoefList532.append(extincCoef532)
        #extincCoefList1064.append(extincCoef1064)
        extCoefUncList_532.append(extCoefUnc_532)
        #extCoefUncList_1064.append(extCoefUnc_1064)

        # extincCoefList.append(extincCoef)
        #reset loop parameters for next path in pathArray
        extincCoef532 = 0
        #extincCoef1064 = 0
        extCoefUnc_532 = 0
        #extCoefUnc_1064 = 0

        #get the length of the path and average distance traveled through a pixel for transmission calculation
        startCoord = path[0]
        endCoord = path[-1]
        dAlt = endCoord[1] - startCoord[1]
        dHor = endCoord[0] - startCoord[0]
        pathLength = np.sqrt((dAlt * 0.08)**2 + (dHor * 5)**2)
        avgPathLength =  5 #pathLength / np.sqrt((dAlt**2) + (dHor)**2)
        pathLengthList.append(avgPathLength)

    #check extencCoefLists for the flag values - this is wrong since the values in array are summed over entire path
    # flagCount_532 = extincCoefList532.count(-444.0) + extincCoefList532.count(-333.0)
    # flagCount_1064 = extincCoefList1064.count(-444.0) + extincCoefList1064.count(-333.0)



    #mask the extincCoef datasets to the range of 0 to 10 (feasible range of extinciton coeff values)
    #extincCoefList532 = np.clip(extincCoefList532,0,10)
    #extincCoefList1064 = np.clip(extincCoefList1064,0,10)


    ########Wavelength dependence calculation based on visibility approximation
    ########here is the section to estimate visibility from extinction coefficient and then make calculations for wavelength dependence
    #we will get two estimates of visibility - one from 1064 and one from 532. This visibility will be a range because the relation between extinction coefficient and visibility also depends on q, which is a discrete parameter that depends on visibility approx(0.451 to 1.6) sigma = 3.61/V(lambda/550nm)^-q). We will use the upper bound to get the upper bound on the wavelength dependence and the lower bound to get the lower bound on the wavelength dependence

    # #calculate visibility arrays from extinction coefficient arrays
    # visibility532 = []
    # # visibility1064 = []
    # for i in range(len(extincCoefList532)):
    # #     #upper bounds
    #     upper532 = 3.61/(extincCoefList532[i] * (532/1064)**(-0.451))
    # #     #upper1064 = 3.61/(extincCoefList1064[i] * (1064/550)**(-0.451))
    # #     #lower bounds
    #     lower532 = 3.61/(extincCoefList532[i] * (532/1064)**(-1.6))
    # #     #lower1064 = 3.61/(extincCoefList1064[i] * (1064/550)**(-1.6))

    # #     #append to visibility arrays
    #     visibility532.append([lower532, upper532])
    #     #visibility1064.append([lower1064, upper1064])


    # print(extincCoefList532[0:20])
    # print(extincCoefList1064[0:20])


    #generate list of transmission values for just 532 and/or 1064
    transmissionList532 = []
    transmissionList1064 = []
    transmissionList1064_UncBound = []
    for i in range(len(extincCoefList532)):
        transmissionList532.append(np.exp(-extincCoefList532[i] * pathLengthList[i]))
        # transmissionList1064.append(10**(-extincCoefList1064[i] * pathLengthList[i]))
        #transmissionList1064_UncBound.append(10**(-(extincCoefList532[i] + extCoefUncList_532[i]) * pathLengthList[i]))


    wavelength = 1064
    #optional run to see wavelength dependence of transmission. For now this will be a single other wavelength, 750nm, but we can change this later. We will also need to change the extinction coefficient calculation to account for this
    #transmission_NWL_upper, transmission_NWL_lower = wavelength_dependence_extCoef(wavelength, extincCoefList532, extincCoefList1064, visibility532, visibility1064)
    
    
    #for now use the average distance a path will travel through a pixel in the matrix - 

    #calculate the rate at which transmission is > 0.9 (0.9 is an arbitrary threshold)
    count532 = 0
    count1064 = 0
    count1064_Unc = 0
    countNWL_upper = 0
    countNWL_lower = 0
    transThreshold = 0.9
    for i in range(len(transmissionList532)):
        if transmissionList532[i] > transThreshold:
            count532 += 1

        # if transmissionList1064[i] > transThreshold:
        #     count1064 += 1

        # if transmissionList1064_UncBound[i] > transThreshold:
        #     count1064_Unc += 1

        # if transmission_NWL_upper[i] > transThreshold:
        #     countNWL_upper += 1
        
        # if transmission_NWL_lower[i] > transThreshold:
        #     countNWL_lower += 1
    
    #calculate the percentage of paths that have a transmission rate > 0.9 (0.9 is arbitrary make this whatever threshold you want)
    percentageMean532 = count532 / len(transmissionList532)
    # percentageMean1064 = count1064 / len(transmissionList1064)
    #percentageMean1064_Unc = count1064_Unc / len(transmissionList1064_UncBound)
    # percentageMeanNWL_upper = countNWL_upper / len(transmission_NWL_upper)
    # percentageMeanNWL_lower = countNWL_lower / len(transmission_NWL_lower)

    numPaths = len(pathArray)

    # percentageMean1064 = 0
    percentageMean1064_Unc=0
    # percentageMeanNWL_upper=0
    # percentageMeanNWL_lower=0
    # flagCount_1064=0

    #depending on what you are doing you may include the counts for other wavelengths, error counts and what not. Toss this all here.
    return count532, percentageMean532, percentageMean1064_Unc, pathLengthList, timeStamp, flagCount_532, numPaths
    #return  percentageMeanNWL_lower, timeStamp, flagCount_532, flagCount_1064, numPaths


# filename = "GA/ga_repo/Transmission_Simulation/CAL_LID_L2_05kmAPro-Standard-V4-51.2019-03-16T03-50-31ZD_Subset.hdf"
# percentageMean532, percentageMean1064, startLat, endLat, startLong, endLong, timeStamp = main(filename)
# print(percentageMean532)
# print("............")
# print(percentageMean1064)

# file_directory = "C:/Users/ga10027553/OneDrive - General Atomics/Desktop/ga_repo_temp/Transmission Simulation/CALIPSO_extData/"
# filename = "CAL_LID_L2_05kmAPro-Standard-V4-21.2022-01-13T04-09-53ZD_Subset.hdf"
# filename = file_directory + filename
# main(filename) 