import pandas as pd
import matplotlib.pyplot as plt
#import seaborn as sns
import numpy as np

folders = ['0.5.2', '0.1', '0.0', '0.2.3', '0.4']
data = {}

for model in folders:
    data.update({model: {'Open': pd.read_csv('model_'+model+'\\data_clone_'+model), 'Close': pd.read_csv('model_'+model+'\\data_trained_'+model)}})

'''
print(f'')
print(f'MODEL {model}:')
print(f"Flight hours:  {[sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
ClCollisions = [sum(data[model]['Close']['Total Collision (s)'])/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]
OlCollisions = [sum(data[model]['Open']['Total Collision (s)'])/sum(data[model]['Open']['Hours of flight (h)']) for model in folders]
print(f"Collisions/(flt.hr): {ClCollisions}")
print(f"Prevented Collisions/(flt.hr): {np.array(OlCollisions)- np.array(ClCollisions)}")
print(f"NMAC/(flt.hr): {[sum(data[model]['Close']['Total LOS (s)'])/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
print(f"LoWC/(flt.hr): {[sum(data[model]['Close']['Total conflicts (s)'])/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
ClConflicts = [(sum(data[model]['Close']['C2TA'])+sum(data[model]['Close']['C2RA']))/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]
OlConflicts = [(sum(data[model]['Open']['C2TA'])+sum(data[model]['Open']['C2RA']))/sum(data[model]['Open']['Hours of flight (h)']) for model in folders]
print(f"Conflicts/(flt.hr): {ClConflicts}")
print(f"Prevented Conflicts/(flt.hr): {np.array(OlConflicts)-np.array(ClConflicts)}")
ClEscalation = [(sum(data[model]['Close']['C2TA'])+sum(data[model]['Close']['TA2RA'])+sum(data[model]['Close']['C2RA']))/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]
OlEscalation = [(sum(data[model]['Open']['C2TA'])+sum(data[model]['Open']['TA2RA'])+sum(data[model]['Open']['C2RA']))/sum(data[model]['Open']['Hours of flight (h)']) for model in folders]
print(f"Escalation/(flt.hr): {ClEscalation}")
print(f"Prevented Escalation/(flt.hr): {np.array(OlEscalation)-np.array(ClEscalation)}")
print(f"De-escalation/(flt.hr): {[(sum(data[model]['Close']['TA2C'])+sum(data[model]['Close']['RA2C'])+sum(data[model]['Close']['RA2TA']))/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
print(f"Protocol1/(flt.hr): {[sum(data[model]['Close']['C2TA'])/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
print(f"Protocol2/(flt.hr): {[(sum(data[model]['Close']['C2RA'])+sum(data[model]['Close']['TA2RA']))/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
print(f"SARL/(flt.hr): {[sum(data[model]['Close']['SARL use'])/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
print(f"MARL/(flt.hr): {[sum(data[model]['Close']['MARL use'])/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
print(f"FD/(flt.hr): {[sum(data[model]['Close']['FD use'])/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
print(f"SPD instructions/(flt.hr): {[sum(data[model]['Close']['Spd instructions'])/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
print(f"ALT instructions/(flt.hr): {[sum(data[model]['Close']['Alt instructions'])/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
print(f"DEV instructions/(flt.hr): {[sum(data[model]['Close']['Dev instructions'])/sum(data[model]['Close']['Hours of flight (h)']) for model in folders]}")
'''

def plot_boxplots(data, models):
    fig, axs = plt.subplots(1, 4, figsize=(12, 10))
    offset = 1

    for i, model in enumerate(models):
        ax = axs[0]
        ax.boxplot((data[model]['Close']['C2TA']/data[model]['Close']['TA2RA']),
                   positions=[offset], vert=True, widths=[0.6])
        ax.set_title('Total LOS/Hours of flight', fontsize=14)

        offset += 1

    for ax in axs.flat:
        ax.set_xlabel('Protocol Modelling', fontsize=12)
        ax.set_xticks(range(1, len(models) + 1))
        ax.set_xticklabels(models)

    plt.tight_layout()
    plt.show()

plot_boxplots(data, folders)
'''
df = pd.read_csv('file.csv')
for idx1, contingency_rate in enumerate(filenames):
    data3, data4 = [], []
    for idx2, activation in enumerate(contingency_rate):
        try:
            dataset = pd.read_csv(filenames[idx1][idx2])
            data1, data2 = [], []
            for index in range(len(dataset)):
                if dataset['flight status'][index] =='contingent/contingent':
                    data1.append(dataset['separation'][index])
                else:
                    data2.append(dataset['separation'][index])
            data3.append(data1)
            data4.append(data2)
        except:
            data3.append([])
            data4.append([])
    data_contcont.append(data3)
    data_tactcont.append(data4)

offset = 0
fig, ax = plt.subplots()
sample_counts = [len(data_contcont[i][0]+data_contcont[i][1]+data_contcont[i][2]+data_contcont[i][3]) for i in range(4)]
for idx1 in range(len(data_contcont)):
    ax.boxplot(data_contcont[idx1][0]+data_contcont[idx1][1]+data_contcont[idx1][2]+data_contcont[idx1][3], positions=[offset], vert=True, widths=[0.6] )
    offset += 1

ax.set_xlabel('Failure rates', fontsize = 21)
ax.set_ylabel('In-flight separation (ft)', fontsize = 21)

ax.set_yscale('log')  # Set the y-axis to logarithmic scale
ax.axhline(y=2000, color='orange', linestyle='--', label='2000ft')
ax.axhline(y=500, color='red', linestyle='--', label='500ft')

ax.text(-0.45, 520, 'Near Mid-Air Collision tolerance')
ax.text(-0.45, 2100, 'Loss of Well-Clear')
ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(['-50%', 'Standard', '+100%', '+500%'], rotation=45, fontsize='large')  # Custom labels for x-ticks

# Customizing y-ticks - Note: choose values relevant for log scale
ax.set_yticks([500, 1000, 2000, 10000, 50000])
ax.set_yticklabels(['500', '1,000', '2,000', '10,000', '50,000'], fontsize='large')  # Custom labels for y-ticks

ax2 = ax.twinx()
ax2.bar([0, 1, 2, 3], sample_counts, color='gray', alpha=0.04, width=0.8)
ax2.set_ylabel('Number of Interactions', fontsize=21, color='gray')  # Setting the y-axis label color to gray

# Customizing tick labels and tick parameters in gray
ax2.tick_params(axis='y', colors='gray', labelsize=14)  # Changes the tick color and size
ax2.set_yticks(sample_counts)

plt.show()
'''