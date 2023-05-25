# -*- coding: utf-8 -*-
"""
Created on Thu May 25 13:45:20 2023
tests for heat_exchanger.py
@author: welp
"""

import sys
sys.path.insert(1, "C:/Users/welp/sciebo/Kollaboration/Carbatpy/carbatpy/carbatpy")


import numpy as np
import CoolProp.CoolProp as CP
from scipy.integrate import solve_bvp
import matplotlib.pyplot as plt
import fluid_properties_rp as fprop
from scipy.optimize import root
import ht as ht

