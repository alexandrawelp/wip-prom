# -*- coding: utf-8 -*-
"""
___________________________________________________________________________________________________

SensAnalysis_example

    "xample of a sensitivity analysi based on the polygeneration process concept v 4.5.
    The process concept itself was removed and only sensitivity analysis function is still included."
       
    v1.0        01.02.2023      built example python file

    
    --------------------------------------------------------------------------------------------

    created on Wed Jan 24 12:27:07 2018

    author:     Dominik Freund
___________________________________________________________________________________________________

"""

"==========================================   IMPORT   ==========================================="

from SALib.sample import saltelli
from SALib.analyze import sobol
from scipy.optimize import root, fsolve 

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import sys
import os


"==========================================   CLASS   ============================================"

class SensAnalysis(object):

    # =============================================================================================
    #       Initialization    
    # =============================================================================================   
    def __init__(self):

        self.plots = True
        self.file_name  = os.path.basename(sys.argv[0]).strip('.py')
    
        # =========================================================================================
        #       Excel sheet path 
        # =========================================================================================

        self.file_in      = self.file_name+"_data.xlsx"
        
        self.xl = pd.ExcelFile(self.file_in, engine="openpyxl")
 
        self.sheet_numbers  = [0]
        self.sheet_names    = ["sensData"]

        self.sensData = (self.xl.parse(self.xl.sheet_names[self.sheet_numbers[0]])).values
                
        # =========================================================================================
        #       Sensitivity analysis
        # =========================================================================================
        self.N_sample       = 2**10      # number of samples (input) created for S.A.
        self.cut_off        = 0.005     # threshold for important S.A. results
                
    "====================================   FUNCTIONS   =========================================="
    
    def readSensrange_xl(self, delimiter=None):
        """
        Unpacks a excel file which includes parameter bounds into a dictionary
        
        """
        self.names   = []
        self.bounds  = []
        self.groups  = []
        self.dists   = []
        
        self.num_vars    = 0
        
        
        for i in range(len(self.sensData)):
                self.num_vars += 1
                self.names.append(self.sensData[i,0])
                self.bounds.append([float(self.sensData[i,1]), float(self.sensData[i,2])])
                self.groups.append(self.sensData[i,4])
                self.dists.append('unif')
    
    
        return {'names': self.names, 'bounds': self.bounds, 'num_vars': self.num_vars,
                'dists': self.dists}                
            

# =================================================================================================
                    
    def sensitivity_analysis(self):

        self.date = str((datetime.datetime.now()).strftime("%Y%m%d-%H%M%S"))
        self.file_out = 'Results/'+self.date+'/'
        os.makedirs(self.file_out)

        # read the parameter range file and generate samples
        self.problem = self.readSensrange_xl()
        
        self.param_values        = saltelli.sample(problem=self.problem, N=self.N_sample, calc_second_order=False )
        self.results             = []
        
        print("\n______________________________________________\nrun sensitivity analyis....\n")
        for i in range(len(self.param_values[:,0])):
            self.param_values_SA = self.param_values[i,:]
            
            # print("param_values_SA: ",self.param_values_SA)
            
            # run the model
            res_temp = self.model(self.param_values_SA) # example only, no function
                                            
            self.results.append(res_temp)
            
        self.results = np.array(self.results)        
        self.results_SA = {}
        self.result_labels = ['label']*int(len((self.results)[0,:]))
        
        for r in range(len(self.results[0,:])):
            print("\n >>> ", self.result_labels[r], "\n")

            self.results_SA[self.result_labels[r]] = sobol.analyze(self.problem, self.results[:,r], calc_second_order=False)
            
            self.si             = self.results_SA[self.result_labels[r]]
            
            self.i_highSens1    = np.where(self.si["S1"]>self.cut_off)[0]
            self.i_highSensT    = np.where(self.si["ST"]>self.cut_off)[0]

            if len(self.i_highSens1) > 0:
                
                for j,i in enumerate(self.i_highSens1):
                        
                    if self.plots:
                        # single plots
                        plt.figure()
                        plt.xlabel(self.names[i])
                        plt.ylabel(self.result_labels[r])
                        plt.title(self.result_labels[r])
                        plt.plot(self.param_values[:,i],self.results[:,r],"o", markersize=2)
                        plt.savefig(self.file_out+self.date+'_'+self.result_labels[r]+'_'+self.names[i]+'.png')
                        # plt.close()

                    # print results in console
                    self.oii = "{0:2d}, {1:20s} S1: {2:= 9.4f}, ST: {3:= 9.4f}" \
                        .format(i,self.names[i],self.si["S1"][i],self.si["ST"][i])
                    print(self.oii)
        
            else: print("\n no sensitivity found")

# =================================================================================================

    def model(self,args):
        import random
        return args*random.randint(1, 100)

"==========================================   RUN   =============================================="

if __name__=="__main__":
    
    import time  
    # import datetime
    s = time.time()
   
    # =============================================================================
    # Sensitivity analysis
    # =============================================================================
    
    SA = SensAnalysis()
    SA.N_sample     = 2**10         # number of samples (2^n)
    SA.cut_off      = -1e5 #0.01   # threshold for important S.A. results
    
    # run sensitivity analysis
    SA.sensitivity_analysis()
    
    problem     = SA.problem
    results     = SA.results
    sensIndex   = SA.si
    paramVal    = SA.param_values 
    
    results_SA = SA.results_SA
    
    import pickle
    pickle.dump(problem, open(SA.file_out+SA.date+"_sa_problem.p","wb"))    
    pickle.dump(results, open(SA.file_out+SA.date+"_sa_results.p","wb"))        
    pickle.dump(paramVal, open(SA.file_out+SA.date+"_sa_paramVal.p","wb"))
    pickle.dump(SA.result_labels, open(SA.file_out+SA.date+"_sa_result_labels.p","wb"))

    e = time.time()
    print("\nRuntime = {} s ({} h)".format(np.round(e-s,1),np.round((e-s)/3600,2)))
        