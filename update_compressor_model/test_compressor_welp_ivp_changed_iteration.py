# -*- coding: utf-8 -*-
"""
Created on Thu May 25 14:25:49 2023
tests for compressor_welp_ivp_changed_iteration
@author: welp
"""

from compressor_welp_ivp_changed_interation import * 
import pytest

# Unit testing
def test_getalp():
    pV = [34e-3, 34e-3, 3.5, .04, .06071, 48.916, 50., 50. / 2., 2.]
    dxdt = -0.1 
    Ti = 300.
    pi = 10e5
    result = [21.116, 40.712, 21.116, 40.712]
    for step in [0,1,2,3]:    
        assert round(getalp(pV, step, dxdt, Ti, pi),3) ==  result[step]
        
        
def test_state_th_Masse():
    y = [0.001, 600000, 330]
    Q = 10000 
    pV = [34e-3, 34e-3, 3.5, .04, .06071, 48.916, 50., 50. / 2., 2.]
    result = 199050.916
    assert round(state_th_Masse(y, Q, pV), 3) == result
    

def test_compression(mocker):
    pV = [34e-3, 34e-3, 3.5, .04, .06071, 48.916, 50., 50. / 2., 2.]
    pos_piston = np.pi/2
    dxdt = 0.1
    Ti = 330.
    pi = 10e5
    mocker.patch('compressor_welp_ivp_changed_interation.getalp', return_value = 100)
    assert compression(pV, pos_piston, dxdt, Ti, pi) == (100, 0., 0.)
    
    
def test_push_out(mocker):
    pV = [34e-3, 34e-3, 3.5, .04, .06071, 48.916, 50., 50. / 2., 2.]
    pos_piston = np.pi/2
    dxdt = 0.1
    Ti = 330.
    pi = 10e5
    pZ = [1, 2, 3, 4, 5, 6, 7]
    pZyk = [0.1, 0.2]
    vi = 0.001
    mocker.patch('compressor_welp_ivp_changed_interation.getalp', return_value = 100)
    assert pytest.approx(push_out(pV, pos_piston, dxdt, Ti, pi, pZ, pZyk, vi),0.1) == (100, 0, 8944.2406)
    
    
def test_expansion(mocker):
    pV = [34e-3, 34e-3, 3.5, .04, .06071, 48.916, 50., 50. / 2., 2.]
    pos_piston = np.pi/2
    dxdt = 0.1
    Ti = 330.
    pi = 10e5
    mocker.patch('compressor_welp_ivp_changed_interation.getalp', return_value = 100)
    assert expansion(pV, pos_piston, dxdt, Ti, pi) == (100, 0., 0.)
    
    
def test_suction(mocker):
    pV = [34e-3, 34e-3, 3.5, .04, .06071, 48.916, 50., 50. / 2., 2.]
    pos_piston = np.pi/2
    dxdt = 0.1
    Ti = 330.
    pi = 10e5
    pZ = [1, 2e6, 3, 4, 5, 6, 7]
    pZyk = [0.1, 0.2]
    vi = 0.001
    mocker.patch('compressor_welp_ivp_changed_interation.getalp', return_value = 100)
    assert pytest.approx(suction(pV, pos_piston, dxdt, Ti, pi, pZ, pZyk),0.1) == (100, 81.6497, 0)

