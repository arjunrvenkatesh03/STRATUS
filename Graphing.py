import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_season(date):
    month = date.month
    if month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Autumn'
    else:
        return 'Winter'

def process_csv(file_path):
    df = pd.read_csv(file_path, parse_dates=['Date'])
    df['Season'] = df['Date'].apply(lambda x: get_season(x))
    return df.groupby('Season')['Percentage of Path\'s > Threshold @ 532'].mean()

def main(base_dir='Transmission_Simulation/CALIPSO_CSV_Data', output_dir='Graphing_Plots'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    region_results = {}

    # Iterate over altitude directories
    for folder in sorted(os.listdir(base_dir)): #, key=lambda x: float(x.split('k')[0]) if x[0].isdigit() else 0):
        folder_path = os.path.join(base_dir, folder)
        if os.path.isdir(folder_path) and folder.endswith('k Data'):
            altitude = abs(float(folder.split('k')[0])-90) -10
            
            # Iterate over CSV files within each altitude directory
            for file in os.listdir(folder_path):
                if file.endswith('_results.csv'):
                    region = file.split('_')[1]  # Extract region from the file name
                    csv_path = os.path.join(folder_path, file)
                    seasonal_avgs = process_csv(csv_path)
                    
                    # Initialize the dictionary for the region if not already done
                    if region not in region_results:
                        region_results[region] = {'Spring': [], 'Summer': [], 'Autumn': [], 'Winter': []}
                    
                    # Aggregate the results for the region
                    for season, avg in seasonal_avgs.items():
                        region_results[region][season].append((altitude, avg))
    
    # Plot and save the results for each region
    for region, seasons in region_results.items():
        plt.figure(figsize=(10, 6))
        for season, data in seasons.items():
            data.sort(key=lambda x: x[0])  # Sort by altitude
            altitudes, avgs = zip(*data) if data else ([], [])
            seasonColors = {"Spring": "green", "Summer": "red", "Autumn": "orange", "Winter": "blue" }
            plt.plot(altitudes, avgs, label=season, marker='o', color=seasonColors[season], alpha=0.5)

            # Define the range for the uncertainty
            uncertainty_start = 0.025
            uncertainty_end = 0.002

            uncertainty_values = np.linspace(uncertainty_start, uncertainty_end, len(altitudes))


            # Calculate the lower and upper bounds for the fill_between
            lower_bounds = avgs - uncertainty_values
            upper_bounds = avgs + uncertainty_values
            plt.fill_between(altitudes, lower_bounds, upper_bounds, alpha=0.15, color=seasonColors[season])

        plt.xlabel('Altitude (k feet)', fontsize=14)
        plt.ylabel("Average Fraction of Path's with \n >90% Transmission", fontsize=14, fontweight="bold")
        plt.title(f'South China Sea', fontsize=20, fontweight="bold")
        plt.legend()
        plt.grid(True)
        #plt.xticks(sorted(set(altitudes)))  # Set x-ticks to unique altitudes

        # # Define the bounding region text
        # bounding_region_text = "Bounding Region:\nLatitudes: (112 to 118)\nLongitudes: (12 to 18)"

        # # Add a text box with the bounding region description
        # # xy: Specify the position as a fraction of the axes size (0 to 1)
        # # xytext: Specify the exact offset of the text from the xy position
        # # You can adjust these values as needed to position your text box
        # plt.figtext(0.7, 0.2, bounding_region_text, fontsize=9, 
        #     verticalalignment='bottom', bbox=dict(alpha=0.95))


        # Set x-ticks to range from 10 to 90, spaced by 1, with labels only at every 5 units
        ticks = list(range(10, 70))  # Generate a list of ticks from 10 to 90
        labels = [str(tick) if tick % 5 == 0 else '' for tick in ticks]  # Label only ticks that are multiples of 5
        plt.xticks(ticks, labels)  # Apply the ticks and labels to the x-axis
        
        plt.xlim(10,65)
        plt.ylim(0.15,1.05)
        # Ensure the output directory for the region exists
        region_dir = os.path.join(output_dir, region)
        if not os.path.exists(region_dir):
            os.makedirs(region_dir)
        
        plt.savefig(os.path.join(region_dir, f'{region}.png'))
        plt.close()

if __name__ == '__main__':
    main()
