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
##############################################################################    
class HeatPump(CarnotBattery):
    def __init__(self, hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific):
        self.compressor = hp_definition['compressor']
        self.expander = hp_definition['expander']
        self.heat_exchanger_HT = hp_definition['heat_exchanger_HT']
        self.heat_exchanger_LT = hp_definition['heat_exchanger_LT']
        self.storage_LT = hp_definition['storage_LT']
        self.storage_HT = hp_definition['storage_HT']
        self.lower_pressure = compressor_conditions['inlet_pressure']
        self.pressure_ratio = compressor_conditions['pressure_ratio']
        self.higher_pressure = self.lower_pressure * self.pressure_ratio
        self.fluid = hp_working_fluid['fluid']
        self.comp = hp_working_fluid['comp']
        self.fluid_model = fluid_props.FluidModel(self.fluid)
        self.working_fluid = fluid_props.Fluid(self.fluid_model, self.comp)
        
        
    def set_up(self, hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific):
        part_comp = Compressor(hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific)
        return part_comp
        
                
##############################################################################
class HeatExchanger(HeatPump):
    def __init__(self):
        HeatPump.__init__(self, hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific)
        self.inlet_temperature = 11
        self.inlet_pressure = 1
        
    def call_heat_exchanger(self, hp_case_specific):
        # choice of heat exchanger
        if HeatPump.heat_exchanger_HT == 'double_tube_he_counterflow':
            self.double_tube_he_counterflow()
        else:
            raise NameError('heat exchanger model not implemented')
            
##############################################################################
class Storage(HeatPump):
    def __init__(self):
        HeatPump.__init__(self, hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific)
        
    def call_storage(self, temperature_level):
        # choice of storage
        if temperature_level == 'HT':
            if HeatPump.storage_HT == 'sensible_two_tank':
                self.sensible_two_tank()
            else:
                raise NameError('storage model not implemented')
                
        if temperature_level == 'LT':
            if HeatPump.storage_LT == 'sensible_two_tank':
                self.sensible_two_tank()
            else:
                raise NameError('storage model not implemented')

##############################################################################                
class Expander(HeatPump):
    def __init__(self, hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific):
        HeatPump.__init__(self,  hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific)
        
    def input_expander(self, inlet_state):
        self.inlet = inlet_state
        
    def call_expander(self):
        # choice of expander
        if HeatPump.expander == 'isenthalp_throttle':
            self.isenthalp_throttle()
        else:
            raise ValueError('expander not implemented')
            
    def isenthalp_throttle(self):
        self.working_fluid.set_state([
            self.lower_pressure, self.inlet.enthalpy], 'PH')
        self.outlet = self.working_fluid.properties
        
        
##############################################################################
class Compressor(HeatPump):
    def __init__(self, hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific):
        HeatPump.__init__(self, hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific)
        self.inlet_temperature = compressor_conditions['inlet_temperature']
        self.inlet_pressure = compressor_conditions['inlet_pressure']
        self.pressure_ratio = compressor_conditions['pressure_ratio']
        self.outlet_pressure = self.inlet_pressure * self.pressure_ratio
        self.working_fluid.set_state([self.inlet_temperature, self.inlet_pressure],
                                                      'TP')
        self.inlet = self.working_fluid.properties
        
    def call_compressor(self, hp_case_specific):
        # choice of different compressor models
        if HeatPump.compressor == 'compressor_constant_is_eff':
            self.compressor_constant_is_eff(hp_case_specific)
        else:
            raise NameError('compressor model not implemented')
    
    def compressor_constant_is_eff(self, hp_case_specific):
        self.working_fluid.set_state([self.inlet.entropy, self.outlet_pressure], 'SP')
        self.outlet_isentropic = self.working_fluid.properties
        h_outlet = (self.outlet_isentropic.enthalpy - self.inlet.enthalpy) / \
                hp_case_specific['compressor_is_efficiency'] + self.inlet.enthalpy          # ha = he + (ha_s - he) / eta_vs
        self.working_fluid.set_state([self.outlet_pressure, h_outlet], 'PH')
        self.outlet = self.working_fluid.properties
        return self.outlet
        
        
##############################################################################        
if __name__ == '__main__':
    # definition of models
    hp_definition = {
        'compressor' : 'compressor_constant_is_eff',
        'expander' : 'isenthalp_throttle',
        'heat_exchanger_HT' : 'double_tube_he_counterflow',
        'storage_LT' : 'sensible_two_tank',
        'heat_exchanger_LT' : 'double_tube_he_counterflow',
        'storage_HT' : 'sensible_two_tank'
        }
    
    compressor_conditions = {
        'inlet_temperature' : 298.15,
        'inlet_pressure' : 1e5,
        'pressure_ratio' : 6
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
    
    test1 = HeatPump(hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific)
    #test1.set_up(hp_conditions)
    test2 = Compressor(hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific)
    # connecting parts