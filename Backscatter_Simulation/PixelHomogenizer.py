#homogenize the backscatter pixels
import numpy as np
from numpy import ma

def homogenize_pixels(highAlt, midAlt, lowAlt, highSurf, lowSurf, alt):

    #for high altitude data (30.1 to 40.0 km)
    og_highAlt = highAlt.shape
    og_midAlt = midAlt.shape
    og_lowAlt = lowAlt.shape
    og_highSurf = highSurf.shape
    og_lowSurf = lowSurf.shape

    target_highAlt = (33*10, highAlt.shape[1])
    target_midAlt = (55*6, midAlt.shape[1])
    target_lowAlt = (200*2, lowAlt.shape[1])
    target_highSurf = (290, highSurf.shape[1])
    target_lowSurf = (5*10, lowSurf.shape[1])

    highAlt_resized = np.zeros(target_highAlt)
    midAlt_resized = np.zeros(target_midAlt)
    lowAlt_resized = np.zeros(target_lowAlt)
    highSurf_resized = np.zeros(target_highSurf)
    lowSurf_resized = np.zeros(target_lowSurf)

    x_original = np.linspace(0, 1, og_highAlt[0])
    x_target = np.linspace(0, 1, target_highAlt[0])
    for i in range(0, highAlt.shape[1]):
        highAlt_resized[:,i] = np.interp(np.linspace(0, og_highAlt[0], target_highAlt[0]), np.linspace(0, og_highAlt[0], og_highAlt[0]), highAlt[:,i])

    x_original = np.linspace(0, 1, og_midAlt[0])
    x_target = np.linspace(0, 1, target_midAlt[0])
    for i in range(0, midAlt.shape[1]):
        midAlt_resized[:,i] = np.interp(np.linspace(0, og_midAlt[0], target_midAlt[0]), np.linspace(0, og_midAlt[0], og_midAlt[0]), midAlt[:,i])

    x_original = np.linspace(0, 1, og_lowAlt[0])
    x_target = np.linspace(0, 1, target_lowAlt[0])
    for i in range(0, lowAlt.shape[1]):
        lowAlt_resized[:,i] = np.interp(np.linspace(0, og_lowAlt[0], target_lowAlt[0]), np.linspace(0, og_lowAlt[0], og_lowAlt[0]), lowAlt[:,i])

    x_original = np.linspace(0, 1, og_highSurf[0])
    x_target = np.linspace(0, 1, target_highSurf[0])
    for i in range(0, highSurf.shape[1]):
        highSurf_resized[:,i] = np.interp(np.linspace(0, og_highSurf[0], target_highSurf[0]), np.linspace(0, og_highSurf[0], og_highSurf[0]), highSurf[:,i])

    x_original = np.linspace(0, 1, og_lowSurf[0])
    x_target = np.linspace(0, 1, target_lowSurf[0])
    for i in range(0, lowSurf.shape[1]):
        lowSurf_resized[:,i] = np.interp(np.linspace(0, og_lowSurf[0], target_lowSurf[0]), np.linspace(0, og_lowSurf[0], og_lowSurf[0]), lowSurf[:,i])

    tempFormattedData = np.concatenate((highAlt_resized, midAlt_resized, lowAlt_resized, highSurf_resized, lowSurf_resized), axis=0)


    #resize the altitude to match the formatted Data size
    original_length = alt.shape[0]
    target_length = tempFormattedData.shape[0]
    x_original = np.linspace(0, 1, original_length)
    x_target = np.linspace(0, 1, target_length)

    interpolated_alt = np.interp(x_target, x_original, alt)


    return tempFormattedData, interpolated_alt

# filename = "CAL_LID_L1-Standard-V4-51.2020-10-20T05-10-45ZD_Subset.hdf"
# file_directory = "C:/Users/ga10027553/OneDrive - General Atomics/Desktop/ga_repo/Backscatter_Simulation/CALIPSO_L1_Data/"
# filepath = file_directory + filename
# parsedData = homogenize_pixels(filepath)
# for data in parsedData:
#     print(data.shape)