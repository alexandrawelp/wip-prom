# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 09:50:48 2023
general structure of Carnot battery
@author: alexa
"""
import fluid_props
from scipy.integrate import solve_bvp
import numpy as np
import sys
sys.path.insert(1, "C:/Users/welp/sciebo/Kollaboration/Carbatpy/carbatpy/carbatpy")
import fluid_properties_rp as fprop

class CarnotBattery:
    def __init__(self, name):
        self.name == name
##############################################################################    
class HeatPump(CarnotBattery):
    def __init__(self, hp_definition, compressor_conditions, hp_working_fluid, 
                 hp_case_specific):
        self.compressor = hp_definition['compressor']
        self.expander = hp_definition['expander']
        self.heat_exchanger_HT = hp_definition['heat_exchanger_HT']
        self.heat_exchanger_LT = hp_definition['heat_exchanger_LT']
        self.storage_LT = hp_definition['storage_LT']
        self.storage_HT = hp_definition['storage_HT']
        self.lower_pressure = compressor_conditions['inlet_pressure']
        self.pressure_ratio = compressor_conditions['pressure_ratio']
        self.higher_pressure = self.lower_pressure * self.pressure_ratio
        self.fluid_name = hp_working_fluid['fluid']
        self.comp = hp_working_fluid['comp']
        self.fluid_model = fluid_props.FluidModel(self.fluid_name)
        self.working_fluid = fluid_props.Fluid(self.fluid_model, self.comp)
        self.mdot = hp_definition['mass_flow']
        
        
    def set_up(self, hp_definition, compressor_conditions, hp_working_fluid, 
               hp_case_specific, he_HT_conditions, hp_secondary_fluid_HT, he_LT_conditions, hp_secondary_fluid_LT):
        part_comp = Compressor(hp_definition, compressor_conditions, 
                               hp_working_fluid, hp_case_specific)
        part_comp.call_compressor(hp_case_specific)
        part_he_HT = HeatExchanger(he_HT_conditions, hp_secondary_fluid_HT, hp_definition, 
                     compressor_conditions, hp_working_fluid, hp_case_specific)
        part_he_HT.secondary_fluid.set_state([hp_secondary_fluid_HT['inlet_temperature'], 
                                        hp_secondary_fluid_HT['inlet_pressure']], 'TP')
        part_he_HT.input_heat_exchanger(part_comp.outlet, part_he_HT.secondary_fluid.properties)
        part_he_HT.call_heat_exchanger(hp_case_specific)
        part_throttle = Expander(hp_definition, compressor_conditions, hp_working_fluid, hp_case_specific)
        part_throttle.input_expander(part_he_HT.outlet)
        part_throttle.call_expander()
        part_he_LT = HeatExchanger(he_LT_conditions, hp_secondary_fluid_LT, hp_definition, 
                     compressor_conditions, hp_working_fluid, hp_case_specific)
        part_he_LT.secondary_fluid.set_state([hp_secondary_fluid_LT['inlet_temperature'], 
                                        hp_secondary_fluid_LT['inlet_pressure']], 'TP')
        part_he_LT.input_heat_exchanger(part_throttle.outlet, part_he_LT.secondary_fluid.properties)
        part_he_LT.call_heat_exchanger(hp_case_specific)
        return part_comp, part_he_HT, part_throttle, part_he_LT
        
                
##############################################################################
class HeatExchanger(HeatPump):
    def __init__(self, he_conditions, hp_secondary_fluid, hp_definition, 
                 compressor_conditions, hp_working_fluid, hp_case_specific):
        HeatPump.__init__(self, hp_definition, compressor_conditions, 
                          hp_working_fluid, hp_case_specific)
        self.length = he_conditions['length']
        self.di = he_conditions['inner_diameter']
        self.alpha = he_conditions['alpha']
        self.sf_name = hp_secondary_fluid['fluid']
        self.sf_model = fluid_props.FluidModel(self.sf_name)
        self.secondary_fluid = fluid_props.Fluid(self.sf_model)
        self.sf_mdot = he_conditions['mass_flow']
        
    def call_heat_exchanger(self, hp_case_specific):
        # choice of heat exchanger
        if self.heat_exchanger_HT == 'double_tube_he_counterflow':
            self.he_counter_current()
        else:
            raise NameError('heat exchanger model not implemented')
    
    def input_heat_exchanger(self, inlet_wf, inlet_sf):
        self.inlet = inlet_wf 
        self.sf_inlet = inlet_sf
        
    def he_counter_current(self, resolution=100):
        def heat_exchanger_counter_current(x, h, p1, p2, fluid_1, fluid_2, comp, 
                                           di, alpha_local, m_dot_1, m_dot_2):
            T_AF = fprop.hp_v(h[0], p1, fluid_1, comp)[0]
            T_SF = fprop.hp_v(h[1], p2, fluid_2)[0]
            delta_T = T_AF - T_SF
            dhdx_0 = -np.pi * di * alpha_local * delta_T / m_dot_1
            dhdx_1 = -np.pi * di * alpha_local * delta_T / m_dot_2
            return np.array([dhdx_0, dhdx_1])

        def bc_he_counter(hlinks, hrechts):
            return np.array([hlinks[0]-self.inlet.enthalpy, 
                             hrechts[1]-self.sf_inlet.enthalpy])
        
        p_KM = self.inlet.pressure
        p_W = self.sf_inlet.pressure
        fluid_1 = self.fluid_name
        fluid_2 = self.sf_name
        comp = self.comp        
        di = self.di
        alpha_local = self.alpha
        m_dot_1 = self.mdot
        m_dot_2 = self.sf_mdot
        x_var = np.linspace(0, self.length, resolution)
        h_schaetz = np.zeros((2, resolution))
        h_schaetz[0, :] = self.inlet.enthalpy
        h_schaetz[1, :] = self.sf_inlet.enthalpy
        res = solve_bvp(lambda x, h: heat_exchanger_counter_current(x, h, p_KM, 
                        p_W, fluid_1, fluid_2, comp, di, alpha_local, m_dot_1, 
                        m_dot_2), bc_he_counter, x_var, h_schaetz)
        
        if res.message != "The algorithm converged to the desired accuracy.":
            print(res.message)
            raise ValueError("The solver did not converge.")
            
        self.working_fluid.set_state([res.y[0,-1], self.inlet.pressure], 'HP')
        self.outlet = self.working_fluid.properties 
        self.secondary_fluid.set_state([res.y[1,-1], self.sf_inlet.pressure], 'HP')
        self.sf_outlet = self.secondary_fluid.properties
            
##############################################################################
class Storage(HeatPump):
    def __init__(self):
        HeatPump.__init__(self, hp_definition, compressor_conditions, 
                          hp_working_fluid, hp_case_specific)
        
    def call_storage(self, temperature_level):
        # choice of storage
        if temperature_level == 'HT':
            if self.storage_HT == 'sensible_two_tank':
                self.sensible_two_tank()
            else:
                raise NameError('storage model not implemented')
                
        if temperature_level == 'LT':
            if self.storage_LT == 'sensible_two_tank':
                self.sensible_two_tank()
            else:
                raise NameError('storage model not implemented')

##############################################################################                
class Expander(HeatPump):
    def __init__(self, hp_definition, compressor_conditions, hp_working_fluid, 
                 hp_case_specific):
        HeatPump.__init__(self,  hp_definition, compressor_conditions, 
                          hp_working_fluid, hp_case_specific)
        
    def input_expander(self, inlet_state):
        self.inlet = inlet_state
        
    def call_expander(self):
        # choice of expander
        if self.expander == 'isenthalp_throttle':
            self.isenthalp_throttle()
        else:
            raise ValueError('expander not implemented')
            
    def isenthalp_throttle(self):
        self.working_fluid.set_state([
            self.lower_pressure, self.inlet.enthalpy], 'PH')
        self.outlet = self.working_fluid.properties
        
        
##############################################################################
class Compressor(HeatPump):
    def __init__(self, hp_definition, compressor_conditions, hp_working_fluid, 
                 hp_case_specific):
        HeatPump.__init__(self, hp_definition, compressor_conditions, 
                          hp_working_fluid, hp_case_specific)
        self.inlet_temperature = compressor_conditions['inlet_temperature']
        self.inlet_pressure = compressor_conditions['inlet_pressure']
        self.pressure_ratio = compressor_conditions['pressure_ratio']
        self.outlet_pressure = self.inlet_pressure * self.pressure_ratio
        self.working_fluid.set_state([self.inlet_temperature, self.inlet_pressure],
                                                      'TP')
        self.inlet = self.working_fluid.properties
        
    def call_compressor(self, hp_case_specific):
        # choice of different compressor models
        if self.compressor == 'compressor_constant_is_eff':
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
        'storage_HT' : 'sensible_two_tank',
        'mass_flow' : 10e-3
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
    
    hp_secondary_fluid_HT = {
        'fluid' : 'Water',
        'inlet_temperature' : 285., 
        'inlet_pressure' : 1e5
        }
    
    hp_secondary_fluid_LT = {
        'fluid' : 'Water',
        'inlet_temperature' : 288.15,
        'inlet_pressure' : 1e5}
    
    he_HT_conditions = {
        'length' : 6.,
        'inner_diameter' : 12e-3,
        'alpha' : 600.,
        'mass flow' : 0.1
        }
    
    he_LT_conditions = {
        'length' : 6., 
        'inner diameter' : 12e-3,
        'alpha' : 400,
        'mass flow' : 0.15
        }
    
    # case specific conditions
    hp_case_specific = {
        'compressor_is_efficiency' : 0.8,
        'HT_storage_fluid' :'water',
        'HT_outlet_temperature' : 90 + 273.15,
        'HT_outlet_pressure' : 10e5
        }
    
    test1 = HeatPump(hp_definition, compressor_conditions, hp_working_fluid, 
                     hp_case_specific)
    #test1.set_up(hp_conditions)
    test2 = Compressor(hp_definition, compressor_conditions, hp_working_fluid, 
                       hp_case_specific)
    # connecting parts