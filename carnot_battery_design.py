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
        self.compressor = hp_definition['compressor']
        self.expander = hp_definition['expander']
        self.heat_exchanger_HT = hp_definition['heat_exchanger_HT']
        self.heat_exchanger_LT = hp_definition['heat_exchanger_LT']
        self.storage_LT = hp_definition['storage_LT']
        self.storage_HT = hp_definition['storage_HT']
        self.fluid_model = fluid_props.FluidModel(hp_working_fluid['fluid'])
        self.working_fluid = fluid_props.Fluid(self.fluid_model, hp_working_fluid['comp'])
        
        
    def set_up(self, hp_conditions):
        self.working_fluid.set_state(
            [hp_conditions['compressor_inlet_temperature'],
             hp_conditions['compressor_inlet_pressure']], 'TP')
        self.compressor_inlet = self.working_fluid.properties
        #self.call_compressor()
        
        
    
    def call_compressor(self, hp_case_specific):
        # choice of different compressor models
        if self.compressor == 'compressor_constant_is_eff':
            self.compressor_constant_is_eff()
            
            
    def call_ht_storage(self, hp_case_specific):
        if self.storage_HT == 'sensible_one_tank':
            if self.heat_exchanger_HT == 'double_tube_he_counterflow':
                self.storage_HT_inlet = self.compressor.outlet 
                
                
            
    def compressor_constant_is_eff(self, hp_case_specific, hp_conditions):
        s_outlet_is = self.compressor_inlet.entropy
        p_outlet = hp_conditions['compressor_inlet_pressure'] *\
                    hp_conditions['compressor_pressure_ratio']
        
        self.working_fluid.set_state(
            [s_outlet_is, p_outlet], 'SP')
        self.compressor_outlet_isentropic = self.working_fluid.properties
        h_outlet = (self.compressor_outlet_isentropic.enthalpy - self.compressor_inlet.enthalpy) / \
                hp_case_specific['compressor_is_efficiency'] + self.compressor_inlet.enthalpy
        self.working_fluid.set_state(
            [p_outlet, h_outlet], 'PH')
        self.compressor_outlet = self.working_fluid.properties
        return self.compressor_outlet
        
        
        
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
        'compressor_inlet_pressure' : 1e5,
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
    test1.set_up(hp_conditions)
    # connecting parts