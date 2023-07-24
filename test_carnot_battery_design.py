# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 14:28:03 2023

@author: welp
"""

from carnot_battery_design import * 
import pytest

def test_initialization():
    # definition of models
    hp_definition = {
        'compressor' : 'compressor_constant_is_eff',
        'expander' : 'isenthalp_throttle',
        'heat_exchanger_HT' : 'double_tube_he_counterflow',
        'storage_LT' : 'sensible_one_tank',
        'heat_exchanger_LT' : 'double_tube_he_counterflow',
        'storage_HT' : 'sensible_one_tank'
        }
    
    hp_conditions = {
        'compressor_inlet_temperature' : 298.15,
        'compressor_inlet_pressure' : 10e5,
        'compressor_pressure_ratio' : 6
        }
    
    hp_working_fluid = {
        'fluid' : 'Propane * Pentane',
        'comp' : [0.4, 0.6]
        }
    
    # case specific conditions
    hp_case_specific = {
        'compressor_is_efficiency' : 0.8,
        'HT_storage_fluid' :'water',
        'HT_outlet_temperature' : 90 + 273.15,
        'HT_outlet_pressure' : 10e5
        }
    
    test1 = HeatPump(hp_definition, hp_conditions, hp_working_fluid, hp_case_specific)
    assert test1.fluid_model.fluid == 'Propane * Pentane'
    assert test1.working_fluid.composition == [0.4, 0.6]
    assert test1.expander == "isenthalp_throttle"