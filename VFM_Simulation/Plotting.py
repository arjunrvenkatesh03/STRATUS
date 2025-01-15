import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# # Load the data
# data = pd.read_csv("results.csv")

# # Extract and standardize the date
# data['Date'] = data['Time Range'].str.extract(r"\['(\d{2}/\d{2}/\d{2})'").astype('datetime64[ns]')

# # Group by date and calculate average success rate
# avg_success_rate = data.groupby('Date')['Success Rate'].mean().reset_index()

# # Calculate rolling averages
# avg_success_rate['7-day Rolling Avg'] = avg_success_rate['Success Rate'].rolling(window=7).mean()
# avg_success_rate['15-day Rolling Avg'] = avg_success_rate['Success Rate'].rolling(window=15).mean()

# # Define date ranges for seasons
# spring_start, spring_end = "2019-03-20", "2019-06-20"
# summer_start, summer_end = "2019-06-21", "2019-09-22"
# autumn_start, autumn_end = "2019-09-23", "2019-12-20"
# winter_start1, winter_end1 = "2019-01-01", "2019-03-19"
# winter_start2, winter_end2 = "2019-12-21", "2019-12-31"

# # Plotting
# fig, ax = plt.subplots(figsize=(12, 6))

# # Raw data
# ax.plot(avg_success_rate['Date'], avg_success_rate['Success Rate'], 
#         label='Raw Data', color='blue', linewidth=0.5, linestyle='--', alpha=0.5)

# # Rolling averages
# ax.plot(avg_success_rate['Date'], avg_success_rate['7-day Rolling Avg'], 
#         label='7-day Rolling Average', color='green', linewidth=1.2)
# ax.plot(avg_success_rate['Date'], avg_success_rate['15-day Rolling Avg'], 
#         label='15-day Rolling Average', color='red', linewidth=1.2)

# # Set x-axis limits to the min and max dates in the data
# ax.set_xlim(avg_success_rate['Date'].min(), avg_success_rate['Date'].max())

# # Seasons shading
# ax.axvspan(pd.Timestamp(spring_start), pd.Timestamp(spring_end), color='lightgreen', alpha=0.2, label='Spring')
# ax.axvspan(pd.Timestamp(summer_start), pd.Timestamp(summer_end), color='yellow', alpha=0.2, label='Summer')
# ax.axvspan(pd.Timestamp(autumn_start), pd.Timestamp(autumn_end), color='orange', alpha=0.2, label='Autumn')
# ax.axvspan(pd.Timestamp(winter_start1), pd.Timestamp(winter_end1), color='lightblue', alpha=0.2, label='Winter')
# ax.axvspan(pd.Timestamp(winter_start2), pd.Timestamp(winter_end2), color='lightblue', alpha=0.2)

# # Formatting
# ax.xaxis.set_major_locator(mdates.MonthLocator())
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
# ax.set_title('Success Rate vs Date (2019) with Rolling Averages')
# ax.set_xlabel('Month')
# ax.set_ylabel('Success Rate (%)')
# ax.legend(loc='upper right')
# plt.tight_layout()
# plt.savefig("SuccessRate.png")

# Read the CSV file
results_directory = "VFM_Simulation/IRST_CSV_Results"
result_filename = f"{results_directory}/{region}_{os.path.basename(file).split('_')[0]}_results.csv"
df = pd.read_csv(result_filename)

# Convert the 'Altitude' and 'Coverage' columns to lists of integers/floats
df['Altitude'] = df['Altitude'].apply(lambda x: list(map(int, x.strip('[]').split(','))))
df['Coverage'] = df['Coverage'].apply(lambda x: list(map(float, x.strip('[]').split(','))))

# Explode the lists into separate rows
df = df.explode('Altitude')
df = df.explode('Coverage')

# Group by 'Altitude' and calculate the mean 'Coverage'
grouped = df.groupby('Altitude')['Coverage'].mean().reset_index()

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(grouped['Altitude'], grouped['Coverage'])
plt.xlabel('Altitude')
plt.ylabel('Average Coverage')
plt.title('Average Coverage at Each Altitude')
plt.grid(True)
plt.show()
