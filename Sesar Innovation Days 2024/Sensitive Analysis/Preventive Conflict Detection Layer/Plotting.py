import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

models = {'RA20': {'TA40': '1.0.1', 'TA50': '1.1.1', 'TA60': '1.2.1', 'TA70': '1.3.1', 'TA80': '1.4.1', 'TA90': '1.5.1', 'TA100': '1.6.1', 'TA110': '1.7.1', 'TA120': '1.8.1'},
        'RA25': {'TA40': '1.0.2', 'TA50': '1.1.2', 'TA60': '1.2.2', 'TA70': '1.3.2', 'TA80': '1.4.2', 'TA90': '1.5.2', 'TA100': '1.6.2', 'TA110': '1.7.2', 'TA120': '1.8.2'},
        'RA30': {'TA40': '1.0.3', 'TA50': '0.2.3', 'TA60': '1.2.3', 'TA70': '1.3.3', 'TA80': '1.4.3', 'TA90': '1.5.3', 'TA100': '1.6.3', 'TA110': '1.7.3', 'TA120': '1.8.3'}}

data = {'Conflict': {'Flight Hour': [], 'Risk Ratio': []}, 
        'Collision': {'Flight Hour': [], 'Risk Ratio': []}, 
        'Protocol1': {'Flight Hour': [], 'Ratio': []}, 
        'Protocol2': {'Flight Hour': [], 'Ratio': []}}

folders = ['0.5.2', '0.1', '0.0', '0.2.3', '0.4']
colours = ['#002060', '#990033', '#678A50']

for RA in list(models.keys()):
    liste = {'Conflict': {'Flight Hour': [], 'Risk Ratio': []}, 
             'Collision': {'Flight Hour': [], 'Risk Ratio': []}, 
             'Protocol1': {'Flight Hour': [], 'Ratio': []}, 
             'Protocol2': {'Flight Hour': [], 'Ratio': []}}
    
    for TA in list(models[RA].keys()):
        df = {'Open': pd.read_csv('model_'+models[RA][TA]+'\\data_clone_'+models[RA][TA]),
              'Close': pd.read_csv('model_'+models[RA][TA]+'\\data_trained_'+models[RA][TA])}
        Conflicts = [(sum(df['Close']['C2TA'])+sum(df['Close']['C2RA']))/sum(df['Close']['Hours of flight (h)']),
                      (sum(df['Open']['C2TA'])+sum(df['Open']['C2RA']))/sum(df['Open']['Hours of flight (h)'])]

        liste['Conflict']['Flight Hour'].append(Conflicts[0])
        liste['Conflict']['Risk Ratio'].append(Conflicts[0]/Conflicts[1]-1)
 
        Collisions = [sum(df['Close']['Total Collision (s)'])/sum(df['Close']['Hours of flight (h)']),
                      sum(df['Open']['Total Collision (s)'])/sum(df['Open']['Hours of flight (h)'])]
        
        liste['Collision']['Flight Hour'].append(Collisions[0])
        liste['Collision']['Risk Ratio'].append(1-Collisions[0]/Collisions[1])

        Protocol1 = [sum(df['Close']['C2TA'])/sum(df['Close']['Hours of flight (h)']),
                     sum(df['Open']['C2TA'])/sum(df['Open']['Hours of flight (h)'])]
        Protocol2 = [(sum(df['Close']['C2RA'])+sum(df['Close']['TA2RA']))/sum(df['Close']['Hours of flight (h)']),
                      (sum(df['Open']['C2RA'])+sum(df['Open']['TA2RA']))/sum(df['Open']['Hours of flight (h)'])]
        
        liste['Protocol1']['Flight Hour'].append(Protocol1[0])
        liste['Protocol1']['Ratio'].append(100*(1-Protocol1[0]/Protocol1[1]))
        liste['Protocol2']['Flight Hour'].append(Protocol2[0])
        liste['Protocol2']['Ratio'].append(100*(1-Protocol2[0]/Protocol2[1]))

    data['Conflict']['Flight Hour'].append(liste['Conflict']['Flight Hour'])
    data['Collision']['Flight Hour'].append(liste['Collision']['Flight Hour'])
    data['Conflict']['Risk Ratio'].append(liste['Conflict']['Risk Ratio'])
    data['Collision']['Risk Ratio'].append(liste['Collision']['Risk Ratio'])
    data['Protocol1']['Flight Hour'].append(liste['Protocol1']['Flight Hour'])
    data['Protocol1']['Ratio'].append(liste['Protocol1']['Ratio'])
    data['Protocol2']['Flight Hour'].append(liste['Protocol2']['Flight Hour'])
    data['Protocol2']['Ratio'].append(liste['Protocol2']['Ratio'])

X = [40, 50, 60, 70, 80, 90, 100, 110, 120]
fig, ax = plt.subplots(1, 5, figsize=(12, 10)) 
    
ax[0].plot(X, data['Conflict']['Flight Hour'][0], linewidth=6, color=colours[0])
ax[0].plot(X, data['Conflict']['Flight Hour'][1], linewidth=6, color=colours[1])
ax[0].plot(X, data['Conflict']['Flight Hour'][2], linewidth=6, color=colours[2])
ax[0].set_xlabel('Traffic Advisory (s)', fontsize=13)
ax[0].set_xticks([40, 60, 80, 100, 120])
ax[0].tick_params(axis='both', which='major', labelsize=13)
ax[0].set_ylabel('Conflict (per Flight Hour)', fontsize=13)

ax[1].plot(X, data['Conflict']['Risk Ratio'][0], linewidth=6, color=colours[0])
ax[1].plot(X, data['Conflict']['Risk Ratio'][1], linewidth=6, color=colours[1])
ax[1].plot(X, data['Conflict']['Risk Ratio'][2], linewidth=6, color=colours[2])
ax[1].set_xlabel('Traffic Advisory (s)', fontsize=13)
ax[1].yaxis.set_major_formatter(mtick.PercentFormatter(1, decimals=0))
ax[1].set_xticks([40, 60, 80, 100, 120])
ax[1].tick_params(axis='both', which='major', labelsize=13)
ax[1].set_ylabel('Knock-on Conflict Detection', fontsize=13)

ax[2].plot(X, data['Protocol1']['Flight Hour'][0], label='RA: 20 seconds', linewidth=6, color=colours[0])
ax[2].plot(X, data['Protocol1']['Flight Hour'][1], label='RA: 25 seconds', linewidth=6, color=colours[1])
ax[2].plot(X, data['Protocol1']['Flight Hour'][2], label='RA: 30 seconds', linewidth=6, color=colours[2])
ax[2].set_xlabel('Traffic Advisory (s)', fontsize=13)
ax[2].set_xticks([40, 60, 80, 100, 120])
ax[2].tick_params(axis='both', which='major', labelsize=13)
ax[2].set_ylabel('Protocol 1 (per Flight Hour)', fontsize=13)

ax[3].plot(X, np.array(data['Protocol2']['Flight Hour'][0])/np.array(data['Protocol1']['Flight Hour'][0]), linewidth=6, color=colours[0])
ax[3].plot(X, np.array(data['Protocol2']['Flight Hour'][1])/np.array(data['Protocol1']['Flight Hour'][1]), linewidth=6, color=colours[1])
ax[3].plot(X, np.array(data['Protocol2']['Flight Hour'][2])/np.array(data['Protocol1']['Flight Hour'][2]), linewidth=6, color=colours[2])
ax[3].set_xlabel('Traffic Advisory (s)', fontsize=13)
ax[3].set_xticks([40, 60, 80, 100, 120])
ax[3].tick_params(axis='both', which='major', labelsize=13)
ax[3].set_ylabel(r'$\mathbb{P}(Protocol 2 | Protocol 1)$', fontsize=13)

ax[4].plot(X, np.array(data['Collision']['Flight Hour'][0])/np.array(data['Protocol2']['Flight Hour'][0]), linewidth=6, color=colours[0])
ax[4].plot(X, np.array(data['Collision']['Flight Hour'][1])/np.array(data['Protocol2']['Flight Hour'][1]), linewidth=6, color=colours[1])
ax[4].plot(X, np.array(data['Collision']['Flight Hour'][2])/np.array(data['Protocol2']['Flight Hour'][2]), linewidth=6, color=colours[2])
ax[4].set_xlabel('Traffic Advisory (s)', fontsize=13)
ax[4].set_xticks([40, 60, 80, 100, 120])
ax[4].tick_params(axis='both', which='major', labelsize=13)
ax[4].set_ylabel(r'$\mathbb{P}(Collision | Protocol 2)$', fontsize=13)

ax[2].legend(fontsize=12)

plt.tight_layout()
plt.show()