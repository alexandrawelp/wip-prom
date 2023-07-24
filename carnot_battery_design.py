# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 09:50:48 2023
general structure of Carnot battery
@author: alexa
"""
import fluid_props



class CarnotBattery:
    def __init__(self, name):
        self.name == name
    
class HeatPump(CarnotBattery):
    def __init__(self, hp_definition, hp_conditions, hp_working_fluid, hp_case_specific):
        self.compressor = hp_definition('hp_compressor')
        self.expander = hp_definition('hp_expander')
        self.heat_exchanger_HT = hp_definition('heat_exchanger_HT')
        self.heat_exchanger_LT = hp_definition('heat_exchanger_LT')
        self.storage_LT = hp_definition('storage_LT')
        self.storage_HT = hp_definition('storage_HT')
        self.fluid_model = fluid_props.FluidModel(hp_working_fluid('fluid'))
        self.working_fluid = fluid_props.Fluid(self.fluid_model, hp_working_fluid('comp'))
        
        
    def set_up(self, hp_conditions):
        self.compressor.inlet = self.working_fluid.set_state(
            [hp_conditions('compressor_inlet_temperature'), 
             hp_conditions('compressor_inlet_pressure')], 'TP')
        self.call_compressor()
        
        
    
    def call_compressor(self, hp_case_specific):
        if self.compressor == 'compressor_constant_is_eff':
            self.compressor_constant_is_eff()
            
    def call_ht_storage(self, hp_case_specific):
        if self.storage_HT == 'sensible_one_tank':
            if self.heat_exchanger_HT == 'double_tube_he_counterflow':
                self.storage_HT_inlet = self.compressor.outlet 
                
                
            
    def compressor_constant_is_eff(self, hp_case_specific):
        s_outlet_is = self.compressor.inlet.entropy
        p_outlet = hp_conditions('compressor_inlet_pressure') *\
                    hp_conditions('compressor_pressure_ratio')
        self.compressor.outlet.isentropic = self.working_fluid.set_state(
            [p_outlet, s_outlet_is], 'PS')
        h_outlet = (self.compressor.outlet.isentropic.enthalpy - self.compressor.inlet.enthalpy) / \
                hp_case_specific('compressor_is_efficiency') + self.compressor.inlet.enthalpy
        self.compressor.outlet = self.working_fluid.set_state(
            [p_outlet, h_outlet], 'PH')
        
        
        
if __name__ == '__main__':
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
    
    
    # connecting parts