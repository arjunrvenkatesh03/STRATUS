#file i/o module to read and run multiple CALIPSO files, and use pandas to perform some data analysis

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Nate_main import main

#define filepath to the folder containing the CALIPSO VFM data
file_directory = "VFM_Simulation/CALIPSO_VFM_Data"
directory = os.listdir(file_directory)

#filter out any directories in that folder as well as DS_Store 
files = [f for f in directory if os.path.isfile(os.path.join(file_directory, f))]


#loop through files and feed them each to the main function in VFM_Simulation\calipso_project_main.py
# results = []
junkFiles = []
# numErrors = 0
tot_look_up_count = np.zeros(1020,dtype=int)
tot_look_down_count = np.zeros(1020,dtype=int)
tot_count = 0
for file in files:
    file_extension = file.split(".")[-1]
    if file_extension != "hdf":
        junkFiles.append(file)
        continue

    try:
        filename = file_directory + "/" + file
        print(filename)
        look_up_count, look_down_count, horizontalWidth = main(filename)
        tot_look_up_count += look_up_count
        tot_look_down_count += look_down_count
        tot_count += horizontalWidth

    except:
        junkFiles.append(file)
        continue
    # results.append([file, totalPaths, successRate, latRange, longRange, timeRange, daynightFlag])
    # except:
    #     print("Error somewhere")
    #     numErrors += 1
altitude = np.linspace(-1.64,98.753,1020)
plt.plot(altitude, 1 - tot_look_up_count[::-1]/tot_count, color="blue",linewidth=2, label="Look-Up Probability")
plt.plot(altitude, 1 - tot_look_down_count[::-1]/tot_count, color="purple",linewidth=2, label="Look-Down Probability")
plt.legend()
plt.xlabel("Altitude (k feet)")
plt.ylabel("Look Up/Down Probability for \nPresence of Clouds")
plt.title("Look Up/Down Cloud Layer Visibility vs Altitude")
plt.xlim(0,98.753)
plt.ylim(0.0,1.0)
plt.savefig("Nates_Plot.png")
print(len(junkFiles))
#create csv file to store results and maniuplate with pandas
# headers = ["Filename", "Total Paths", "Success Rate", "Latitude Range", "Longitude Range", "Time Range", "Day/Night Flag"]
# data = results
# print(numErrors)
# print(len(junkFiles))

# df = pd.DataFrame(data, columns=headers)
# filename = "results.csv"
# df.to_csv(filename, index=False)
