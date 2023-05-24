# -*- coding: utf-8 -*-
"""
___________________________________________________________________________________________________

ee_SensAnalysisPickle

    "Imports the problem and the results of the exergoeconomic analysis and performs 
    a sensitivity"
    
    v1.0        02.03.2020      
    v2.0        03.11.2021      automatically calculates the sensitivity for all products
    
    --------------------------------------------------------------------------------------------

    created on Fri Feb 28 17:08:59 2020

    author:     Dominik Freund
___________________________________________________________________________________________________

"""

import numpy as np
import matplotlib.pyplot as plt
import datetime
import pickle
from SALib.analyze import sobol, delta
from SALib.sample import saltelli

def filtData(array1, threshold, array2):
    new_array1  = np.zeros([0,len(array1[0,:])]) 
    new_array2 = np.zeros([0,len(array2[0,:])])        
    
    for l in range(len(array1[:,0])):
        if (array1[l,:] > threshold).any() == False:
            new_array1 = np.append(new_array1,  [array1[l,:]], axis=0)
            new_array2 = np.append(new_array2,[array2[l,:]], axis=0)
    
    D = 16
    print(new_array1[:,0].size, (D+2), new_array1.size % (D + 2))
    while new_array1[:,0].size % (D + 2) != 0:
        print(new_array1[:,0].size, (D+2), new_array1.size % (D + 2))
        new_array1 = np.delete(new_array1, -1, 0)
        new_array2 = np.delete(new_array2, -1, 0)
    
    # delete some rows at the end to reach an array length of 2**n with type(n)==int
    # N_rows = len(new_array1[:,0])
    # N_rows_new = 2**int(np.round(np.log2(N_rows)))
    # dN = N_rows - N_rows_new
    # new_array1 = np.delete(new_array1, [-1,-dN], 0)
    # new_array2 = np.delete(new_array2, [-1,-dN], 0)

    return new_array1, new_array2

# fig = True
fig = False

# filt = True
filt = False

time = str((datetime.datetime.now()).strftime("%Y%m%d-%H%M%S"))

prefix = '20220530-135215_'

problem = pickle.load(open(prefix+"sa_problem.p","rb"))
results = pickle.load(open(prefix+"sa_results.p","rb"))
param_values = pickle.load(open(prefix+"sa_paramVal.p","rb"))
mainProd = pickle.load(open(prefix+"sa_mainProducts.p","rb"))

if filt:
    results, param_values = filtData(results, 1e2, param_values)
# new_array = np.zeros([0,len(results[0,:])])am_values[l,:]], axis=0)
        
# import sys
# sys.exit()

N_sample = 1000
cut_off = -10

# param_values   = saltelli.sample(problem, N_sample,calc_second_order=False )
names          = np.array(problem['names'],str)

results_SA = {}

print(results[:,0].size)


for r in range(len(results[0,:])):
    print("\n >>> ", mainProd[r], "\n")
    results_SA[mainProd[r]] = sobol.analyze(problem, results[:,r], calc_second_order=False)
    
    # results_SA[mainProd[r]] = delta.analyze(problem, param_values, results[:,r])
    
    si             = results_SA[mainProd[r]]
    
    i_highSens1    = np.where(si["S1"]>cut_off)[0]
    # i_highSensT    = np.where(si["ST"]>cut_off)[0]
    
    if len(i_highSens1) > 0:
        # subplots
        # fig, axs = plt.subplots(len(self.i_highSens1))
        # fig.tight_layout()
        
        for j,i in enumerate(i_highSens1):
                # subplots
                # fig.suptitle(self.mainProduct_list[r])
                # axs[j].plot(self.param_values[:,i],self.results[:,r],"o", markersize=2)
                # axs[j].set(xlabel=self.names[i], ylabel='$\\dot{C}$ [€/h]')
                
                # single plots
                plt.figure()
                plt.xlabel(names[i])
                plt.ylabel('model output')
                plt.title(mainProd[r])
                plt.plot(param_values[:,i],results[:,r],"o", markersize=2)
                # plt.savefig('Results/plots/'+time+'_'+mainProd[r]+'_'+names[i]+'.png')
                if fig == False:
                    plt.close()
                
                # print results in console
                oii = "{0:2d}, {1:20s} S1: {2:= 9.4f}, ST: {3:= 9.4f}" \
                    .format(i,names[i],si["S1"][i],si["ST"][i])
                print(oii)
            
    else: print("\n no sensitivity found")