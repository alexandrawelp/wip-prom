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

### set-up environment #######################################################
@pytest.fixture
def hp_definition():
    hp_definition = {
        'compressor' : 'compressor_constant_is_eff',
        'expander' : 'isenthalp_throttle',
        'heat_exchanger_HT' : 'double_tube_he_counterflow',
        'storage_LT' : 'sensible_one_tank',
        'heat_exchanger_LT' : 'double_tube_he_counterflow',
        'storage_HT' : 'sensible_one_tank',
        'mass_flow' : 10e-3
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
def hp_secondary_fluid():
    hp_secondary_fluid = {
        'fluid' : 'Water',
        'inlet_temperature' : 285., 
        'inlet_pressure' : 1e5
        }
    return hp_secondary_fluid

@pytest.fixture 
def he_HT_conditions():
    he_HT_conditions = {
        'length' : 6.,
        'inner_diameter' : 12e-3,
        'alpha' : 600.,
        'mass_flow' : 0.1
        }
    return he_HT_conditions
    
### set-up dummy classes #####################################################
@pytest.fixture
def dummy_hp(hp_definition, compressor_conditions, hp_working_fluid, 
                    hp_case_specific):
    dummy = HeatPump(hp_definition, compressor_conditions, hp_working_fluid, 
                        hp_case_specific)
    return dummy

@pytest.fixture 
def dummy_comp(hp_definition, compressor_conditions, hp_working_fluid, 
               hp_case_specific):
    dummy = Compressor(hp_definition, compressor_conditions, hp_working_fluid, 
                       hp_case_specific)
    return dummy

@pytest.fixture 
def dummy_co_he(he_HT_conditions, hp_secondary_fluid, hp_definition, 
                compressor_conditions, hp_working_fluid, hp_case_specific):
    dummy = HeatExchanger(he_HT_conditions, hp_secondary_fluid, hp_definition, 
                          compressor_conditions, hp_working_fluid, hp_case_specific)
    return dummy

@pytest.fixture 
def dummy_expa(hp_definition, compressor_conditions, hp_working_fluid, 
               hp_case_specific):
    dummy = Expander(hp_definition, compressor_conditions, hp_working_fluid, 
                     hp_case_specific)
    return dummy

### tests ####################################################################    
def test_initialization(dummy_hp):
    assert dummy_hp.fluid_model.fluid == 'Propane * Pentane'
    assert dummy_hp.working_fluid.composition == [0.4, 0.6]
    assert dummy_hp.expander == "isenthalp_throttle"
    
    
def test_set_up(dummy_hp, hp_definition, compressor_conditions, hp_working_fluid, 
                hp_case_specific):
    part_comp = dummy_hp.set_up(hp_definition, compressor_conditions, 
                                hp_working_fluid, hp_case_specific)
    
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
    
    assert dummy_expa.outlet.enthalpy == pytest.approx(dummy_expa.inlet.enthalpy)
    assert dummy_expa.outlet.temperature == pytest.approx(261.83)
    
    
def test_counterflow_he(dummy_co_he, hp_working_fluid, hp_secondary_fluid):
    fluid_model = fluid_props.FluidModel(hp_working_fluid['fluid'])
    working_fluid = fluid_props.Fluid(fluid_model, hp_working_fluid['comp'])
    working_fluid.set_state([374., 6e5], 'TP')
    inlet_state = working_fluid.properties
    
    sf_model = fluid_props.FluidModel(hp_secondary_fluid['fluid'])
    sf_fluid = fluid_props.Fluid(sf_model)
    sf_fluid.set_state([280., 1e5], 'TP')
    inlet_sf_fluid = sf_fluid.properties
    
    dummy_co_he.input_heat_exchanger(inlet_state, inlet_sf_fluid)
    dummy_co_he.he_counter_current()
    
    
    