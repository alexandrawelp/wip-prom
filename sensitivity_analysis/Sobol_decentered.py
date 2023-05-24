# -*- coding: utf-8 -*-
"""
Created on Mon May 30 12:14:14 2022

issue:
    https://github.com/SALib/SALib/issues/109
    https://gist.github.com/sofianehaddad/f3bb2ac1b9c20fbf739fad7a1994dd1f

solution:
    https://github.com/SALib/SALib/pull/128
    https://github.com/SALib/SALib/pull/128/commits/68fa4fc95c2a7a4fa2813346203db23bb98ed85c

@author: Freund

"""
from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.test_functions import Ishigami
import numpy as np

problem = {
    'num_vars': 3,
    'names': ['x1', 'x2', 'x3'],
    'bounds': [[-np.pi, np.pi],
               [-np.pi, np.pi],
               [-np.pi, np.pi]]
}
size = 1000
param_values = saltelli.sample(problem, size, calc_second_order=False)
Y = Ishigami.evaluate(param_values)
Si = sobol.analyze(problem, Y, print_to_console=False, calc_second_order=False)
print("Usual Ishigami")
print(Si['S1'])
print(Si['ST'])
Z = Ishigami.evaluate(param_values) + 1000
Si = sobol.analyze(problem, Z, print_to_console=False, calc_second_order=False)
print("Decentered Ishigami")
print(Si['S1'])
print(Si['ST'])