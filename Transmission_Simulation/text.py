import pandas as pd
import os

def merge_ACPro(csv_file1, csv_file2, output_path):
    # Load the CSV files into DataFrames
    df1 = pd.read_csv(csv_file1)
    df2 = pd.read_csv(csv_file2)

    # Ensure the 'Date' columns are in datetime format for proper sorting
    df1['Date'] = pd.to_datetime(df1['Date'])
    df2['Date'] = pd.to_datetime(df2['Date'])

    # Sort the DataFrames by the 'Date' column
    df1_sorted = df1.sort_values(by='Date')
    df2_sorted = df2.sort_values(by='Date')

    # Merge the two DataFrames on 'Date', keeping only the rows with matching dates in both DataFrames
    merged_df = pd.merge(df1_sorted, df2_sorted, on='Date', suffixes=('_df1', '_df2'))
    # Calculate the sum of 'ExtinctionCoef 532', 'FlagCount 532', and 'numPaths' for each date
    merged_df['ExtinctionCoef 532 Sum'] = merged_df['ExtinctionCoef 532_df1'] + merged_df['ExtinctionCoef 532_df2']
    merged_df['FlagCount 532 Sum'] = merged_df['FlagCount 532_df1'] + merged_df['FlagCount 532_df2']
    merged_df['numPaths Sum'] = merged_df['numPaths_df1'] + merged_df['numPaths_df2']

    # Create a new DataFrame with the required columns
    result_df = merged_df[['Filename_df1', 'Filename_df2', 'Date', 'ExtinctionCoef 532 Sum', 'FlagCount 532 Sum', 'numPaths Sum']]

    # Save the result DataFrame to the specified output path
    result_df.to_csv(output_path, index=False)

# Base directory where the original data is stored
base_dir = "Transmission_Simulation/CALIPSO_CSV_Data"

# New base directory for the merged CSV files
new_base_dir = "Transmission_Simulation/mergedCSV_Data"

# Ensure the new base directory exists
os.makedirs(new_base_dir, exist_ok=True)

# Loop through each subdirectory in the base directory
for altitude_folder in os.listdir(base_dir):
    altitude_folder_path = os.path.join(base_dir, altitude_folder)
    
    # Check if it's a directory
    if os.path.isdir(altitude_folder_path):
        # Construct the output folder path
        output_folder_path = os.path.join(new_base_dir, altitude_folder)
        os.makedirs(output_folder_path, exist_ok=True)
        
        # Assuming there are exactly two CSV files to merge in each folder
        csv_files = [os.path.join(altitude_folder_path, f) for f in os.listdir(altitude_folder_path) if f.endswith('.csv')]
        if len(csv_files) == 2:
            # Construct the path for the merged CSV file within the new structure
            output_csv_path = os.path.join(output_folder_path, f"merged_{altitude_folder}.csv")
            
            # Call the merge function
            merge_ACPro(csv_files[0], csv_files[1], output_csv_path)
        else:
            print(f"Skipping {altitude_folder_path} as it does not contain exactly two CSV files.")
