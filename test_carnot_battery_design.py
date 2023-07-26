# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 14:28:03 2023

@author: welp
"""
import pytest
import fluid_props
#import os, sys
#sys.path.append(os.path.join(os.path.dirname(__file__)))
from carnot_battery_design import *

@pytest.fixture
def hp_definition():
    hp_definition = {
        'compressor' : 'compressor_constant_is_eff',
        'expander' : 'isenthalp_throttle',
        'heat_exchanger_HT' : 'double_tube_he_counterflow',
        'storage_LT' : 'sensible_one_tank',
        'heat_exchanger_LT' : 'double_tube_he_counterflow',
        'storage_HT' : 'sensible_one_tank'
        }
    return hp_definition

@pytest.fixture
def hp_working_fluid():
    hp_working_fluid = {
        'fluid' : 'Propane * Pentane',
        'comp' : [0.4, 0.6]
        }
    return hp_working_fluid

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
def compressor_conditions():
    compressor_conditions = {
        'inlet_temperature' : 298.15,
        'inlet_pressure' : 1e5,
        'pressure_ratio' : 6
        }
    return compressor_conditions

@pytest.fixture
def dummy_hp(hp_definition, compressor_conditions, hp_working_fluid, 
                    hp_case_specific):
    dummy = HeatPump(hp_definition, compressor_conditions, hp_working_fluid, 
                        hp_case_specific)
    return dummy

@pytest.fixture 
def dummy_comp(hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific):
    dummy = Compressor(hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific)
    return dummy

@pytest.fixture 
def dummy_expa(hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific):
    dummy = Expander(hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific)
    return dummy
    
def test_initialization(dummy_hp):
    assert dummy_hp.fluid_model.fluid == 'Propane * Pentane'
    assert dummy_hp.working_fluid.composition == [0.4, 0.6]
    assert dummy_hp.expander == "isenthalp_throttle"
    
def test_set_up(dummy_hp, hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific):
    part_comp = dummy_hp.set_up(hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific)
    assert part_comp.inlet.temperature == pytest.approx(
        compressor_conditions['inlet_temperature'])
    assert part_comp.inlet.pressure == pytest.approx(
        compressor_conditions['inlet_pressure'])
    assert part_comp.inlet.enthalpy == pytest.approx(423610,rel=1e-3)
    
def test_compressor_constant_is_eff(dummy_comp, hp_case_specific, compressor_conditions):
    dummy_comp.compressor_constant_is_eff(hp_case_specific)
    assert dummy_comp.outlet.pressure == pytest.approx(compressor_conditions[
        'inlet_pressure'] * compressor_conditions['pressure_ratio'])
    assert dummy_comp.outlet.enthalpy == pytest.approx(515198,rel=1e-3)
    
def test_isenthalpic_throttle(dummy_expa, hp_working_fluid):
    fluid_model = fluid_props.FluidModel(hp_working_fluid['fluid'])
    working_fluid = fluid_props.Fluid(fluid_model, hp_working_fluid['comp'])
    working_fluid.set_state([295., 6e5], 'TP')
    inlet_state = working_fluid.properties
    dummy_expa.input_expander(inlet_state)
    dummy_expa.isenthalp_throttle()
    
    