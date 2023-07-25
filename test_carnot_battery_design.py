# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 14:28:03 2023

@author: welp
"""
import pytest
#import os, sys
#sys.path.append(os.path.join(os.path.dirname(__file__)))
from carnot_battery_design import *

hp_definition = {
    'compressor' : 'compressor_constant_is_eff',
    'expander' : 'isenthalp_throttle',
    'heat_exchanger_HT' : 'double_tube_he_counterflow',
    'storage_LT' : 'sensible_one_tank',
    'heat_exchanger_LT' : 'double_tube_he_counterflow',
    'storage_HT' : 'sensible_one_tank'
    }



hp_working_fluid = {
    'fluid' : 'Propane * Pentane',
    'comp' : [0.4, 0.6]
    }

# case specific conditions
@pytest.fixture
def hp_case_specific():
    hp_case_specific = {
    'compressor_is_efficiency' : 0.8,
    'HT_storage_fluid' :'water',
    'HT_outlet_temperature' : 90 + 273.15,
    'HT_outlet_pressure' : 10e5
    }
    return hp_case_specific

@pytest.fixture 
def hp_conditions():
    hp_conditions = {
        'compressor_inlet_temperature' : 298.15,
        'compressor_inlet_pressure' : 1e5,
        'compressor_pressure_ratio' : 6
        }
    return hp_conditions

@pytest.fixture
def dummy():
    dummy_cb = HeatPump(hp_definition, hp_conditions, hp_working_fluid, 
                        hp_case_specific)
    return dummy_cb

def test_initialization(dummy):
    assert dummy.fluid_model.fluid == 'Propane * Pentane'
    assert dummy.working_fluid.composition == [0.4, 0.6]
    assert dummy.expander == "isenthalp_throttle"
    
def test_set_up(dummy, hp_conditions):
    dummy.set_up(hp_conditions)
    assert dummy.compressor_inlet.temperature == pytest.approx(
        hp_conditions['compressor_inlet_temperature'])
    assert dummy.compressor_inlet.pressure == pytest.approx(
        hp_conditions['compressor_inlet_pressure'])
    assert dummy.compressor_inlet.enthalpy == pytest.approx(423610,rel=1e-3)
    
    
def test_compressor_constant_is_eff(dummy, hp_case_specific, hp_conditions):
    dummy.working_fluid.set_state(
        [hp_conditions['compressor_inlet_temperature'],
         hp_conditions['compressor_inlet_pressure']], 'TP')
    dummy.compressor_inlet = dummy.working_fluid.properties
    dummy.compressor_constant_is_eff(hp_case_specific, hp_conditions)
    assert dummy.compressor_outlet.pressure == pytest.approx(hp_conditions[
        'compressor_inlet_pressure'] * hp_conditions['compressor_pressure_ratio'])
    assert dummy.compressor_outlet.enthalpy == pytest.approx(515198,rel=1e-3)
    
    