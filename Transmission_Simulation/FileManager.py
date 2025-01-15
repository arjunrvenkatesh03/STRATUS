#module to iterate over all files in the extData folder and do some analytics

import os
import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection

from calipso_transmission_main import main


# def extract_key_for_matching(filename):
#     # Regular expression pattern to find the segment between "-51." and "_Subset"
#     pattern = r"-51\.(?P<key>.+?)_Subset"
#     match = re.search(pattern, filename)
#     if match:
#         return match.group('key')
#     else:
#         return None

# def list_files_with_keys(folder_path):
#     files_with_keys = {}
#     for filename in os.listdir(folder_path):
#         key = extract_key_for_matching(filename)
#         if key:
#             files_with_keys[key] = os.path.join(folder_path, filename)
#     return files_with_keys

# def match_files(base_folder_path):
#     folders = [os.path.join(base_folder_path, f) for f in os.listdir(base_folder_path) if os.path.isdir(os.path.join(base_folder_path, f))]
#     if len(folders) != 2:
#         raise ValueError(f"Expected exactly 2 folders inside {base_folder_path}, found {len(folders)}.")

#     folder1_files = list_files_with_keys(folders[0])
#     folder2_files = list_files_with_keys(folders[1])

#     common_keys = set(folder1_files.keys()) & set(folder2_files.keys())

#     paired_files = [(folder1_files[key], folder2_files[key]) for key in common_keys]

#     return paired_files

# # Base folder containing the two folders with files to be matched
# base_folder_path = "Transmission_Simulation/CALIPSO_Data"

# # Match files by date
# matched_file_pairs = match_files(base_folder_path)
# # for file1,file2 in matched_file_pairs:
# #     print(file1)
# #     print(file2)
# #     print("....................")

# print(len(matched_file_pairs))

# Output the matched file pairs
# for file1, file2 in matched_file_pairs:
#     print(f"Matched files: {file1} and {file2}")
def run(CPro_directory, sourceAlt):
    altitude = sourceAlt / 4  # Assuming integer division is intended
    alt_directory = f"Transmission_Simulation/{altitude}k Data"
    os.makedirs(alt_directory, exist_ok=True)

    results = []
    junkFiles = []

    #define filepath to the folder containing the CALIPSO VFM data
    # print(CPro_directory)
    CPro_dirPath = "Transmission_Simulation/CALIPSO_Data/" + CPro_directory
    print(CPro_dirPath)
    CPro_directory = os.listdir(CPro_dirPath)
    # print(CPro_directory)

    for file in CPro_directory:
        # file_extension_APro = os.path.splitext(file1)
        # file_extension_CPro = os.path.splitext
        # if file_extension != ".hdf":
        #     junkFiles.append(os.path.basename(filename))
        #     continue
        # print(file1)
        # print(file2)

        #should be able to run for all the hdf files (there are two files that are txt files that will trigger this try/except wrapper, so if you have more than two errors you might have another issue in the code)
        try:
                # Placeholder for the actual processing function
                # Replace `main(filename, sourceAlt)` with your actual function call
            # print(file1)
            # print(file2)
            filename = CPro_dirPath + "/" + file

            #pass the necessary simulation inputs to the main function to start running the simulation
            count532, percentageMean_532, percentageMean_Unc, pathLengthList, timeStamp, flagCount_532, numPaths = main(filename, sourceAlt)
            results.append([file, count532, percentageMean_532, percentageMean_Unc, pathLengthList, timeStamp, flagCount_532, numPaths])
        except Exception as e:
            print(f"Error in: {file} - {e}")
            junkFiles.append(os.path.basename(file))
            continue

    
    #this is to format the csv file that contains the output. Might have to change this a bit if you want to store multiple wavelegnths for example or any other parameters
    headers = ["Filename_CPro", "Count_532", "Percentage of Path's > Threshold @ 532", "PercentageMean_Unc", "PathLengthList", "Date", "FlagCount 532", "numPaths"]
    df = pd.DataFrame(results, columns=headers)
    result_filename = f"{alt_directory}/{sourceAlt}k_{os.path.basename(file).split('_')[0]}_results.csv"
    df.to_csv(result_filename, index=False)

    return len(junkFiles), junkFiles

# Main process
sourceAlts = range(20, 390, 10)
# base_folder_path = "Transmission_Simulation/CALIPSO_Data"
# matched_file_pairs = match_files(base_folder_path)


#this does a sweep and calls the run() function over the range of altitudes, so for this setup a datafile is created for each altitude
for sourceAlt in sourceAlts:
    print(f"Running Simulation for Source Altitude: {sourceAlt}")
    CPro_directory = os.listdir("Transmission_Simulation/CALIPSO_Data")
    print(CPro_directory)
    for folder in CPro_directory:
        if "10y" in folder:
            print(folder)
            # print(CPro_directory)
            error_count, junkFiles = run(folder, sourceAlt)
            print(f"Error count for altitude {sourceAlt}: {error_count}")
    # if junkFiles:
    #     print(f"Junk files for altitude {sourceAlt}: {junkFiles}")

# def run(folderName, sourceAlt):

#     # Create a directory for the current sourceAlt if it doesn't exist
#     altitude = sourceAlt/4
#     alt_directory = f"Transmission_Simulation/{altitude}k Data"
#     os.makedirs(alt_directory, exist_ok=True)


#     #define filepath to the folder containing the CALIPSO VFM data
#     print(folderName)
#     file_directory = "Transmission_Simulation/CALIPSO_Data/" + folderName
#     print(file_directory)
#     directory = os.listdir(file_directory)


#     #filter out any directories in that folder as well as DS_Store 
#     files = [f for f in directory if os.path.isfile(os.path.join(file_directory, f))]

#     results = []
#     numErrors = 0
#     junkFiles = []
#     count = 0
#     for file in directory:
#         file_extension = file.split(".")[-1]
#         if file_extension != "hdf":
#             junkFiles.append(file)
#             continue

        
#         try:
#             filename = file_directory + "/" + file
#                         #print(".......")
#             transmissionRate_532, pathLengthList, timeStamp, flagCount_532, numPaths = main(filename, sourceAlt)
#             results.append([filename, transmissionRate_532, pathLengthList, timeStamp, flagCount_532, numPaths]) #note that the timestamp is a day of the year, so for more specific times, we will need to do some more work
#             #print(f"Running: {filename}")
#         except:
#             junkFiles.append(file)
#             print(f"Error in: {filename}")
#             continue
        
#     print(f"Number of files that threw errors in {sourceAlt} run: ", len(junkFiles))
#     headers = ["Filename", "Transmission 532","PathLengthList", "Date","FlagCount 532", "numPaths"]
#     df = pd.DataFrame(results, columns=headers)
#     filename = f"Transmission_Simulation/{altitude}k Data/" + folderName + "_results.csv"
#     df.to_csv(filename, index=False)

#     return flagCount_532, junkFiles

# sourceAlts = range(40,220,40)

# # Dictionary to hold error counts organized by folder name and sourceAlt
# errorsDict = {}

# error_countTot = 0
# junkFiles = []
# # List all the CALIPSO dataset folders
# folderNames = os.listdir("Transmission_Simulation/CALIPSO_Data")
# for folderName in folderNames:
#     if "10y" in folderName:
#         errorsDict[folderName] = {}
#         for sourceAlt in sourceAlts:
#             error_count, junkFile = run(folderName, sourceAlt)
#             error_countTot += error_count
#             junkFiles.append(junkFile)

# print(error_countTot)
# print(len(junkFiles))
# #print(junkFiles[0:100])