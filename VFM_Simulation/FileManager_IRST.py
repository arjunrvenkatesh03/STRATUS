import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from IRST_main import main

#define filepath to the folder containing the CALIPSO VFM data
file_directory = "VFM_Simulation/CALIPSO_VFM_Data"
directory = os.listdir(file_directory)

#filter out any directories in that folder as well as DS_Store 
files = [f for f in directory if os.path.isfile(os.path.join(file_directory, f))]

results_directory = "VFM_Simulation/IRST_CSV_Results"
os.makedirs(results_directory, exist_ok=True)
region = "SCS"


junkFiles = []
results = []
coverageMean_results = [0] * 1010
numFiles = 0
for file in files:
    file_extension = file.split(".")[-1]
    if file_extension != "hdf":
        junkFiles.append(file)
        continue

    try:
        filename = file_directory + "/" + file
        print(filename)
        filename, altitude_list, coverage_list = main(filename)
        results.append([filename, altitude_list, coverage_list])
        coverageMean_results += coverage_list
        numFiles += 1
    # results.append([filename, altitudeList, coverageList, coverageMean])
    except:
        junkFiles.append(file)
        continue
        
coverageMean_list = coverageMean_results / numFiles

# # Convert the results to a DataFrame
# df = pd.DataFrame(results, columns=['Filename', 'Altitude', 'Coverage'])

# # Calculate the average coverageMean for each altitude
# average_coverage = df.groupby('Altitude')['Coverage'].mean().tolist()

# # Concatenate the results into a single DataFrame
# results_df = pd.concat(results)

# result_filename = f"{results_directory}/{region}_{os.path.basename(file).split('_')[0]}_results.csv"
# results_df.to_csv(result_filename, index=False)
# headers = ["Filename", "Altitude", "Coverage", "CoverageMean"]
# # results = list(zip(filename, altitudeList, coverageList))
# df = pd.DataFrame(results, columns=headers)
# result_filename = f"{results_directory}/{region}_{os.path.basename(file).split('_')[0]}_results.csv"
# df.to_csv(result_filename, index=False)

# print(len(junkFiles))

# # Read the CSV file
# df = pd.read_csv(result_filename)

# # Convert the 'Altitude' and 'Coverage' columns to lists of integers/floats
# df['altitude'] = df['altitude'].apply(lambda x: list(map(int, x.strip('[]').split(','))))
# df['coverage_mean'] = df['coverage_mean'].apply(lambda x: list(map(float, x.strip('[]').split(','))))

# # Explode the lists into separate rows
# df = df.explode('altitude')
# df = df.explode('coverage_mean')

# # Group by 'Altitude' and calculate the mean 'Coverage'
# grouped = df.groupby('altitude')['coverage_mean'].mean().reset_index()
# altitude_list = results[0][1]
# print(altitude_list[0:20])

altitude_list = np.linspace(0,30,1010)

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(altitude_list, coverageMean_list[::-1]* 100, marker='o', color='b')
# plt.plot(altitude_list, average_coverage, marker='o', color='r')
plt.xlabel('Altitude')
plt.ylabel('Average Coverage')
plt.title('Average Coverage at Each Altitude')
plt.grid(True)
plt.show()
plt.savefig("AverageCoverage.png")