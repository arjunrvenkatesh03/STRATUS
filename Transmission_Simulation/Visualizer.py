#module to visualize the transmission path data
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.dates import MonthLocator, YearLocator

# Load the data
# df = pd.read_csv('Transmission_Simulation/10y_Ukraine_results.csv')

def make_plot(dataframe, filename, altitude):

    df = dataframe

    # Convert 'Date' to datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # Sort the DataFrame by 'Date'
    df.sort_values(by='Date', inplace=True)

    # Create a 'DayOfYear' column
    df['DayOfYear'] = df['Date'].dt.dayofyear

    # # Group by 'DayOfYear' and calculate mean of each dataset
    # df_avg_532 = df.groupby('DayOfYear')["Count_532"].sum().reset_index()
    # df_avg_532 = df.groupby('DayOfYear')["numPaths"].sum().reset_index()
    # df_avg_532["Percentage of Path's > Threshold @ 532"] = df_avg_532["Count_532"] / df_avg_532["numPaths"]
    #df_avg_1064 = df.groupby('DayOfYear')["Percentage of Path's > Threshold @ 1064"].mean().reset_index()

    # Step 1: Group by 'DayOfYear' and sum 'Count_532'
    df_sum_532 = df.groupby('DayOfYear')['Count_532'].sum().reset_index(name='Total_Count_532')

    # Step 2: Group by 'DayOfYear' and sum 'numPaths'
    df_paths = df.groupby('DayOfYear')['numPaths'].sum().reset_index(name='Total_numPaths')

    # Step 3: Merge the two DataFrames on 'DayOfYear'
    df_avg_532 = pd.merge(df_sum_532, df_paths, on='DayOfYear')

    # Step 4: Calculate 'Percentage of Paths > Threshold @532'
    df_avg_532['Percentage_532'] = (df_avg_532['Total_Count_532'] / df_avg_532['Total_numPaths']) * 100

    # df_merged now contains 'DayOfYear', 'Total_Count_532', 'Total_numPaths', and 'Percentage_532'



    # Calculate the mean and the uncertainty of the new columns
    # df['Mean_NWL'] = df[['Percentage of Path\'s > Threshold @ NWL(lower)', 'Percentage of Path\'s > Threshold @ NWL(upper)']].mean(axis=1)
    # df_avg_nwl = df.groupby('DayOfYear')['Mean_NWL'].mean().reset_index()
    # df_avg_nwl['Lower'] = df.groupby('DayOfYear')['Percentage of Path\'s > Threshold @ NWL(lower)'].mean().reset_index()['Percentage of Path\'s > Threshold @ NWL(lower)']
    # df_avg_nwl['Upper'] = df.groupby('DayOfYear')['Percentage of Path\'s > Threshold @ NWL(upper)'].mean().reset_index()['Percentage of Path\'s > Threshold @ NWL(upper)']

    # Step 1: Group and sum FlagCount_1064 and numPaths by DayOfYear
    # df_sum = df.groupby('DayOfYear').agg({'FlagCount_1064': 'sum', 'numPaths': 'sum'}).reset_index()
    #print(df_sum["FlagCount_1064"])
    # Step 2: Calculate uncertainty for 1064 data
    # df_sum['uncertainty_1064'] = df_sum['FlagCount_1064'] / df_sum['numPaths']

    # Merge the uncertainty data with your average data
    # df_avg_1064 = df_avg_1064.merge(df_sum[['DayOfYear', 'uncertainty_1064']], on='DayOfYear')

    # uncertainty_1064 = df_avg_1064["uncertainty_1064"]
    #print(uncertainty_1064.shape)
    


    # Convert 'DayOfYear' back to datetime for all datasets
    convert_day_of_year = lambda df: pd.to_datetime('2019' + '-' + df['DayOfYear'].astype(str), format='%Y-%j')
    df_avg_532['Date'] = convert_day_of_year(df_avg_532)
    # df_avg_1064['Date'] = convert_day_of_year(df_avg_1064)
    # df_avg_nwl['Date'] = convert_day_of_year(df_avg_nwl)

    # Function to determine season with overlapping winter
    def get_season(date):
        if date.month in [12, 1, 2]:
            return 'winter'
        elif date.month in [3, 4, 5]:
            return 'spring'
        elif date.month in [6, 7, 8]:
            return 'summer'
        elif date.month in [9, 10, 11]:
            return 'fall'

    # Apply function to get season for both datasets
    df_avg_532['Season'] = df_avg_532['Date'].apply(get_season)
    # df_avg_1064['Season'] = df_avg_1064['Date'].apply(get_season)
    # df_avg_nwl['Season'] = df_avg_nwl['Date'].apply(get_season)

    # Perform the rolling average calculation with a 7-day and 15-day window for both datasets
    df_avg_532['RollingAvg'] = df_avg_532["Percentage_532"].rolling(window=7).mean()
    #df_avg_532['RollingAvg_15'] = df_avg_532["Percentage of Path's > Threshold @ 532"].rolling(window=15).mean()

    # df_avg_1064['RollingAvg'] = df_avg_1064["Percentage of Path's > Threshold @ 1064"].rolling(window=7).mean()
    # #df_avg_1064['RollingAvg_15'] = df_avg_1064["Percentage of Path's > Threshold @ 1064"].rolling(window=15).mean()
    

    # df_avg_nwl['RollingAvg'] = df_avg_nwl['Mean_NWL'].rolling(window=7).mean()
    #df_avg_nwl['RollingAvg_15'] = df_avg_nwl['Mean_NWL'].rolling(window=15).mean()

    # Define colors for each season
    color_dict = {'winter': 'blue', 'spring': 'green', 'summer': 'yellow', 'fall': 'orange'}

    # Define patches for legend
    patches = [mpatches.Patch(color=color, label=season) for season, color in color_dict.items()]

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot data for the first dataset (532)
    ax.plot(df_avg_532['Date'], df_avg_532["Percentage_532"], label='Original Data @ 532', linestyle='--', alpha=0.1)
    ax.plot(df_avg_532['Date'], df_avg_532['RollingAvg'], label='7-day Rolling Average @ 1064', linewidth=1.3, color="r",alpha=0.5)
    #ax.plot(df_avg_532['Date'], df_avg_532['RollingAvg_15'], label='15-day Rolling Average @ 532', linewidth=2)

    # Plot data for the second dataset (1064)
    # ax.plot(df_avg_1064['Date'], df_avg_1064["Percentage of Path's > Threshold @ 1064"], label='Original Data @ 1064', linestyle='--', alpha=0.1)
    # ax.plot(df_avg_1064['Date'], df_avg_1064['RollingAvg'], label='7-day Rolling Average @ 1064', linewidth=1.3, color='r',alpha=0.5)
    #print(df_avg_1064["Percentage of Path's > Threshold @ 1064"].shape)
    #ax.plot(df_avg_1064['Date'], df_avg_1064['RollingAvg_15'], label='15-day Rolling Average @ 1064', linewidth=2, linestyle='--')
    # ax.fill_between(df_avg_1064['Date'], 
    #             df_avg_1064['RollingAvg'] - df_avg_1064["uncertainty_1064"], 
    #             df_avg_1064['RollingAvg'] + df_avg_1064["uncertainty_1064"], 
    #             color='g', alpha=0.2, label='Uncertainty')

    # flagCount = np.sum(df_avg_1064["uncertainty_1064"])
    # print(flagCount)

    # #plot NWL data
    # ax.plot(df_avg_nwl['Date'], df_avg_nwl['Mean_NWL'], label='Original Data @ NWL', linestyle='--', alpha=0.1)
    # ax.plot(df_avg_nwl['Date'], df_avg_nwl['RollingAvg'], label='7-day Rolling Average @ NWL', linewidth=1.3, color='g')
    # plt.fill_between(df_avg_nwl['Date'], df_avg_nwl['Lower'].rolling(window=7).mean(), df_avg_nwl['Upper'].rolling(window=7).mean(), color='g', alpha=0.3)

    # Add season color bars (using either dataset for the season as they share the same dates)
    for season, color in color_dict.items():
        ax.fill_between(df_avg_532['Date'], 0, 1, where=df_avg_532['Season']==season, color=color, alpha=0.05, transform=ax.get_xaxis_transform())

    ax.set_xlabel('Date')
    ax.set_ylabel('Percentage of Paths with > 90% Transmission')
    ax.set_title(f'Transmission Plot at 1064nm ({altitude}k - {altitude}k) Link')

    # Add grid
    ax.grid(True)

    # Limit x values (using either dataset as the date range should be the same)
    ax.set_xlim([df_avg_532['Date'].min(), df_avg_532['Date'].max()])

    # Set x-axis major and minor ticks
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_minor_locator(MonthLocator())

    # Line legend elements for both datasets
    line_legend_elements = [plt.Line2D([0], [0], color='tab:red', lw=2, label='7-day Rolling Average @ 1064'),
                            #plt.Line2D([0], [0], color='tab:red', lw=2, label='7-day Rolling Average @ 1064')]
                            #plt.Line2D([0], [0], color='tab:green', lw=2, label='7-day Rolling Average @ NWL')]
    ]
    # All legend elements
    all_legend_elements = patches + line_legend_elements

    # Add legend outside of plot
    ax.legend(handles=all_legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1), fontsize="x-large")

    # Create an array of dates you want to display on the x-axis (using either dataset as the date range should be the same)
    selected_dates = df_avg_532['Date'][::30]  # Every 30th date

    # Set these dates as x-ticks
    ax.set_xticks(selected_dates)

    plt.rcParams.update({'font.size': 14})  # Sets the default font size for all text elements

    # Format the x-tick labels as desired (for example, in 'MM-DD' format)
    ax.set_xticklabels(selected_dates.dt.strftime('%m-%d'), rotation=45, ha='right')

    plt.tight_layout()
    return plt


# Create the main directory for graphs if it doesn't exist
graphs_dir = "CALIPSO_Graphs"
if not os.path.exists(graphs_dir):
    os.makedirs(graphs_dir)

base_dir = "Transmission_Simulation/CALIPSO_CSV_Data"
for folder_name in os.listdir(base_dir):
    #print(folder_name)
    # Check if the folder name is in the format "{altitude}k Data" and divisible by 10
    if folder_name.endswith("k Data"):
        altitude = folder_name.split('k')[0]
        #if altitude % 10 == 0:
        if True:
            print(folder_name)
            # Path to the altitude-specific folder
            folder_path = os.path.join(base_dir, folder_name)
            
            # Create a subfolder in CALIPSO_Graphs for this altitude if it doesn't exist
            altitude_graphs_dir = os.path.join(graphs_dir, str(altitude) + 'k')
            if not os.path.exists(altitude_graphs_dir):
                os.makedirs(altitude_graphs_dir)
            
            # Iterate over CSV files in the altitude-specific folder
            for file_name in os.listdir(folder_path):
                #if file_name.startswith("10y_") and file_name.endswith("_results.csv"):
                if True:
                    csv_path = os.path.join(folder_path, file_name)
                    df = pd.read_csv(csv_path)
                    
                    # Define save path for the plot
                    region = file_name.split('_')[1]  # Extract region from file name
                    save_path = os.path.join(altitude_graphs_dir, f"{region}_graph.png")
                    
                    # Read CSV and pass it to the make_plot function
                    plt = make_plot(df, save_path, altitude)

                    plt.savefig(save_path)

# #find the folder with the csv files we want to plot
# directoryName = os.listdir("Transmission_Simulation/40.0k Data")

# #iterate over all the csv files in the folder
# for file in directoryName:
#     if file.split(".")[-1] != "csv":
#         continue
    
#     #load the csv file
#     df = pd.read_csv("Transmission_Simulation/40.0k Data/" + file)
#     filename = file.split(".")[0]
#     make_plot(df, filename)

