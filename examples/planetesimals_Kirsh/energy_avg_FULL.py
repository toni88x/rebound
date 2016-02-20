#This macro calculates the average energy for a set of runs. Assumes that all the files are in energy_avg/.

import glob
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cmx
import matplotlib.colors as colors
import sys
import os
import re

def natural_key(string_):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

plot_choice = 2      #1 = plot energy, 2 = plot semi-major axis
time_sort = 0        #sort runs according to time?

ms = 0.25
alpha = 0.5
names = ['time (years)','dE/E(0)','semi-major axis of planet(AU)']
outputn = ['time (years)','dE','a']

N_files = 0
dirP = str('energy_avg/')
files = glob.glob(dirP+'*.txt')
files = sorted(files, key = natural_key)
data = []
n_it = 10e10

g_c = 0
b_c = 0
colors = []
colorsg = ['lime','chartreuse','forestgreen','springgreen','olivedrab','green']
#colorsg = ['red','orange','blue']
colorsb = ['dodgerblue','blue','mediumblue','darkblue','royalblue','navy']
time_array = ['dt4.00','dt12.76']
HSR=[]
for f in files:
    try:
        ff = open(f, 'r')
        lines = ff.readlines()
        length = len(lines)
        if length < n_it:   #need to find array with shortest length
            n_it = length
        data.append(lines)
        N_files += 1
        split = f.split("_")
        if time_sort == 1:
            if split[-3] == time_array[0]:
                colors.append(colorsg[g_c])
                g_c += 1
            else:
                colors.append(colorsb[b_c])
                b_c += 1
        else:
            HSR.append(split[-2])
    except:
        print 'couldnt read in data file '+f

E = np.zeros(shape=(N_files,n_it))
Eavg = np.zeros(n_it)
time = np.zeros(n_it)
vals_for_med = np.zeros(N_files)
for i in xrange(0,n_it):
    for j in range(0,N_files):
        split = data[j][i].split(",")
        vals_for_med[j] = float(split[plot_choice])
        E[j][i] = vals_for_med[j]
    Eavg[i] = np.median(vals_for_med)
    time[i] = float(split[0])/6.283185

j=0
k=0
if time_sort == 0:
    colors = colorsg
for i in xrange(0,N_files):
    if time_sort == 1:
        if colors[j] == colorsg[0]:
            plt.plot(time,E[i], ms=ms, color=colors[j], alpha=alpha, label = 'dt = 0.637')
        elif colors[j] == colorsb[0]:
            plt.plot(time,E[i], ms=ms, color=colors[j], alpha=alpha, label = 'dt = 2')
        else:
            plt.plot(time,E[i], ms=ms, color=colors[j], alpha=alpha)
    else:
        plt.plot(time,E[i], ms=ms, color=colors[j], alpha=alpha, label = HSR[k])
        k += 1
    j += 1
    if j >= len(colors):
        j = 0
#plt.plot(time, Eavg, 'o', markeredgecolor='none', color='black', label='avg.')
if plot_choice == 1:
    plt.plot(time,3e-10*time**(0.5),color='black')


##############################################
#Final plotting stuff
plt.legend(loc='lower left',prop={'size':10})
plt.ylabel(names[plot_choice])
plt.xlabel('time (years)')
if plot_choice == 1:
    plt.yscale('log')
    plt.xscale('log')
plt.xlim([0.5,time[-1]])
plt.title('Median '+names[plot_choice]+' from '+str(N_files)+' files')
plt.savefig(dirP+'energy_avg_'+outputn[plot_choice]+'.png')
plt.show()