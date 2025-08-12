import matplotlib.pyplot as plt
from geopy.distance import geodesic
import pandas as pd
import numpy as np
import datetime

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15), sharex=True)

data = pd.read_csv('dataLogInspection1.csv')
operation = 'UAS0-rodolphe02'

ownship_data = data[data['Operation'] == operation]

colors = {'None': 'green', 
          'Clear of Conflict': 'green', 
          'TA': 'orange', 
          'TA Clearance': 'yellow', 
          'RA': 'red'}

target_operation = 'UAS0-rodolphe02'
data = data.dropna(subset=['Latitude', 'Longitude'])
unique_times = data['Time'].unique()
valid_statuses = ["TA", "RA", "TA Clearance"]

start_time = ownship_data['Time'].iloc[0]

def format_seconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}:{seconds:02d}"



times, lats, lons, alts = [], [], [], []
status = 'None'
all_times = []
all_formatted_times = []



for index, row in ownship_data.iterrows():
    if pd.isna(row['Status']):
        status = 'None'
        new_status = 'None'
    else:
        new_status = row['Status']

    elapsed_time = row['Time'] - start_time
    formatted_time = format_seconds(int(elapsed_time))

    all_times.append(elapsed_time) 
    all_formatted_times.append(formatted_time) 

    if status == new_status:
        times.append(formatted_time)
        lats.append(row['Latitude'])
        lons.append(row['Longitude'])
        alts.append(row['Altitude'])
    elif len(lats) == 1:
        ax1.scatter(times[0], alts[0], marker='o', s=16, color=colors[status])
    else:
        times.append(formatted_time)
        lats.append(row['Latitude'])
        lons.append(row['Longitude'])
        alts.append(row['Altitude'])

        ax1.plot(times, alts, color=colors[status], linewidth=7)
        status = row['Status']
        times, lats, lons, alts = [formatted_time], [row['Latitude']], [row['Longitude']], [row['Altitude']]
ax1.plot([], [], color='green', linewidth=6, label='Nominal')
ax1.plot([], [], color='orange', linewidth=6, label='TA')
ax1.plot([], [], color='red', linewidth=6, label='RA')
ax1.plot([], [], color='yellow', linewidth=6, label='TA Clearance')

ax1.axhline(y=150, color='grey', linestyle='--', linewidth=0.8)
ax3.axhline(y=100, color='grey', linestyle='--', linewidth=0.8)
ax2.axhline(y=500, color='grey', linestyle='--', linewidth=0.8)



ticks_interval = 30 
max_time = int(max(all_times))  

tick_positions = np.arange(0, max_time, ticks_interval)
tick_labels = [format_seconds(int(t)) for t in tick_positions] 

ax1.set_xticks(tick_positions)
ax1.set_xticklabels(tick_labels)
ax1.set_ylabel('Altitude (ft)', fontsize=21)
ax1.tick_params(axis='both', which='major', labelsize=21)

ax1.legend(fontsize=21)

times, operations, Hseparations, Vseparations = [], [], [], []
for time in unique_times:
    current_time_data = data[data['Time'] == time]
    
    target_data = current_time_data[current_time_data['Operation'] == target_operation]
    
    if not target_data.empty and target_data.iloc[0]['Status'] in valid_statuses:
        target_lat = target_data.iloc[0]['Latitude']
        target_lon = target_data.iloc[0]['Longitude']
        target_alt = target_data.iloc[0]['Altitude']
        
        for index, row in current_time_data.iterrows():
            if row['Operation'] != target_operation and row['Status'] in valid_statuses:
                other_lat = row['Latitude']
                other_lon = row['Longitude']
                other_alt = row['Altitude']
                
                target_coords = (target_lat, target_lon)
                other_coords = (other_lat, other_lon)
                distance = geodesic(target_coords, other_coords).feet  
                times.append(time)
                operations.append(row['Operation'])
                Hseparations.append(distance)
                Vseparations.append(abs(other_alt-target_alt))

for time, Hseparation, Vseparation in zip(times, Hseparations, Vseparations):
    elapsed_time = time - start_time
    formatted_time = format_seconds(int(elapsed_time))
    if Hseparation<=2000 and Vseparation<=100:
        if Hseparation<=500:
            color = 'red'
        else:
            color = 'orange'
    else:
        color= 'green'
    ax2.scatter(formatted_time, Hseparation, marker = 'o', s=40, color=color)
    ax3.scatter(formatted_time, Vseparation, marker='o', s=40, color=color)

ax1.set_xticks(tick_positions)
ax1.set_xticklabels(tick_labels)
ax1.set_yticks([100, 150, 200, 250])
ax1.set_ylabel('BVLOS Operation \n Altitude (ft)', fontsize=16)
ax1.tick_params(axis='both', which='major', labelsize=21)
ax1.legend(fontsize=18)

ax2.set_xticks(tick_positions)
ax2.set_xticklabels(tick_labels)
ax2.set_yticks([500, 1000, 1500, 2000])
ax2.set_yticklabels(['500', '1,000', '1,500', '2,000'])
ax2.set_ylabel('Horizontal \n Separation (ft)', fontsize=16)
ax2.tick_params(axis='both', which='major', labelsize=21)

ax3.set_xticks(tick_positions)
ax3.set_xticklabels(tick_labels)

ax3.set_yticks([50, 100, 150])
ax3.set_ylabel('Vertical \n Separation (ft)', fontsize=16)
ax3.set_xlabel('Time (m:ss)', fontsize=21)
ax3.tick_params(axis='both', which='major', labelsize=21)

plt.show()