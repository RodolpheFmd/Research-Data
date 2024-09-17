import matplotlib.pyplot as plt
from geopy.distance import geodesic
import pandas as pd
import numpy as np

BVLOS = 'UAS0-rodolphe02'

def pairing(ac1, ac2):
    if 'UAS0' in ac1 or 'UAS0' in ac2:
        if not ' -' in ac1 and not ' -' in ac2:
            return 'RP-AUTO'
        else:
            return 'RP-CT'
    else:
        if ' -' not in ac1 and ' -' not in ac2:
            return 'AUTO-AUTO'
        else:
            if (' -' in ac1 and ' -' not in ac2) or (' -' not in ac1 and ' -' in ac2):
                return 'AUTO-CT'
            else:
                return 'CT-CT'

separation = {'RP-AUTO' : {'under100': [], '0': []}, 'RP-CT': {'under100': [], '0': []}, 'AUTO-AUTO' : {'under100': [], '0': []}, 'AUTO-CT': {'under100': [], '0': []}, 'CT-CT': {'under100': [], '0': []}}

data = pd.read_csv('dataLogInspection1.csv')

data['Latitude'] = pd.to_numeric(data['Latitude'], errors='coerce')
data['Longitude'] = pd.to_numeric(data['Longitude'], errors='coerce')

fig, ax = plt.subplots(1, 1, figsize=(12, 15), sharex=True)

times = data['Time'].unique()

TA = []

for time in times:
    operations_time = data[data['Time'] == time]
    for i, operation in operations_time.iterrows():
        coords = (operation['Latitude'], operation['Longitude'])
        for j, intruder in operations_time.iterrows():
            if i != j:
                intruder_coords = (intruder['Latitude'], intruder['Longitude'])
                distance = geodesic(coords, intruder_coords).feet 
                verti = abs(operation['Altitude']- intruder['Altitude'])
                if distance <= 2000:
                    if verti<=100:
                        separation[pairing(operation['Operation'], intruder['Operation'])]['under100'].append(distance)
                    if verti<=6:
                        separation[pairing(operation['Operation'], intruder['Operation'])]['0'].append(distance)

colors = ['lightblue', 'lightgreen', 'lightcoral', 'gold', 'lightpink']

for idx, pair in enumerate(list(separation.keys())):
    if pair != 'CT-CT':  
        box = plt.boxplot(separation[pair]['under100'], vert=False, patch_artist=True, positions=[idx], widths=0.8, 
                          boxprops=dict(facecolor=colors[idx]),
                          medianprops=dict(color='black', linewidth=4),
                          capprops=dict(color=colors[idx], linewidth=6),
                          whiskerprops=dict(color=colors[idx], linewidth=6))
        box = plt.boxplot(separation[pair]['0'], vert=False, patch_artist=True, positions=[idx], widths=0.3, 
                          boxprops=dict(facecolor=colors[idx], hatch='//'),
                          medianprops=dict(color='black', linewidth=3),
                          capprops=dict(color='k', linewidth=3),
                          whiskerprops=dict(color='k', linewidth=3))
    print(f"{pair}: {len(separation[pair]['under100'])}")
    print(f"{pair}: {len(separation[pair]['0'])}")

plt.xlabel("Horizontal Separation (ft)", fontsize=21)
plt.yticks([]) 

plt.axvline(x=500, color='red', linestyle='--', linewidth=0.5)

handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in colors[:-1]] 
plt.legend(handles, [f"{key}" if key != 'CT-CT' else key for key in separation.keys() if key != 'CT-CT'], loc="upper left", fontsize=16)
plt.xticks([0, 500, 1000, 1500, 2000], ['0', '500', '1,000', '1,500', '2,000'], fontsize=21)

plt.show()
