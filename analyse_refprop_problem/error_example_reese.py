# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 20:40:12 2023

@author: Max
"""

"==========================================   IMPORT   ==========================================="

import numpy as np
import os

from scipy.integrate import solve_ivp
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary

os.environ['RPPREFIX'] = r'C:/Program Files (x86)/REFPROP'
RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
RP.SETPATHdll(os.environ['RPPREFIX'])
RP.SETFLUIDSdll("Water")
SP = REFPROPFunctionLibrary(os.environ['RPPREFIX']) #secondary fluid
SP.SETPATHdll(os.environ['RPPREFIX'])
SP.SETFLUIDSdll("Isobutane")
MASS_BASE_SI = RP.GETENUMdll(0, "MASS BASE SI").iEnum


def diffeq_enthalpy_ivp(ort, y, input_values, wf='Isobutane', sf='Water'):
    '''
    Differential equations of enthalpy for working and secondary fluid in an double-pipe heat exchanger.
    '''
    global counter_call_refprop
    p_wf_0, p_sf_0, di, ds, area_wf, area_sf, lam_rohr, m_wf, m_sf, z, T_sf_0 = input_values
    h_wf, h_sf = y

    # Stoffeigenschaften der Fluide: Dichte, Wärmekapazität, kinematische Viskosität, Thermische Leitfähigkeit, Prandtl-Zahl, Temperatur
    result = RP.REFPROPdll("", "PH", "D;CP;VIS;TCX;PRANDTL;T", MASS_BASE_SI, 0, 0, 10e5, h_wf, [0])
    Zustand_wf_x = result.Output[0:6]
    counter_call_refprop += 1
    if Zustand_wf_x[0] == -9999990.:
        print(f"counter_refprop: {counter_call_refprop}")
        print(f"input values: p = 10e5 bar, h_wf = {h_wf}")
        print(f"error flag: {result.ierr} error string: {result.herr}")
        raise ValueError(f"Unplausible state in Zustand_wf_x: {Zustand_wf_x}")

    Zustand_sf_x = SP.REFPROPdll("", "PH", "D;CP;VIS;TCX;PRANDTL;T", MASS_BASE_SI, 0, 0, 1e5, h_sf, [0]).Output[0:6]
    counter_call_refprop += 1
    if Zustand_sf_x[0] == -9999990.:
        print(f"counter_refprop: {counter_call_refprop}")
        print(f"input values: p = 1e5 bar, h_wf = {h_sf}")
        raise ValueError(f"Unplausible state in Zustand_sf_x: {Zustand_sf_x}")

    # Temperaturen der Fluide in: K
    T_wf = Zustand_wf_x[5]
    T_sf = Zustand_sf_x[5]

    # Wärmeübergangskoeffizient
    alpha_wf = 1000
    alpha_sf = 1000

    # Übertragener Wärmestrom
    R = (alpha_wf * np.pi * di) ** -1 + np.log((di + 2 * ds) / di) / (2 * np.pi * lam_rohr) + (
                alpha_sf * np.pi * (di + 2 * ds)) ** -1
    dQdx_R = (T_wf - T_sf) / R

    # DGL
    dhwf = 1 / (m_wf) * dQdx_R
    dhsf = 1 / (m_sf) * dQdx_R

    return [dhwf, dhsf]


if __name__ == "__main__":
    sf = "Water"
    wf = "Isobutane"


    int_method = 'BDF'
    L = 2

    p_wf_0 = 15e5
    p_sf_0 = 1e5
    dT_max = 10
    m_wf = 10e-3
    m_sf = 40e-3

    lam_rohr = 50
    ds = 1e-3
    z = [0]

    T_wf_sat = RP.REFPROPdll("", "PQ", "T", MASS_BASE_SI, 0, 0, p_wf_0, 1, z).Output[0]
    T_sf_0 = T_wf_sat - dT_max

    area_wf = 0.000247
    area_sf = 4.1016e-5

    di = np.sqrt(4 * area_wf / np.pi)

    parameter_values = [p_wf_0, p_sf_0, di, ds, area_wf, area_sf, lam_rohr, m_wf, m_sf, z, T_sf_0]

    h_wf_sat = RP.REFPROPdll("", "PQ", "H", MASS_BASE_SI, 0, 0, p_wf_0, 1, z).Output[0]
    h_sf_0 = SP.REFPROPdll("", "PT", "H", MASS_BASE_SI, 0, 0, p_sf_0, T_sf_0, [0]).Output[0]
    y_bc = [h_wf_sat, h_sf_0]
    counter_call_refprop = 3        # 5 times called already
    orte = np.linspace(0, L, 100)  # Definition der Stützstellen
    print("\n______________________________________________\nstarting for-loop....\n")

    n = 10000
    for i in range(n):
        res = solve_ivp(lambda ort, y: diffeq_enthalpy_ivp(ort, y, parameter_values, wf, sf), (0, L),
                        y_bc, t_eval=orte, method="DOP853")
        if res.message != "The solver successfully reached the end of the integration interval.":
            raise ValueError("The solver didn't converge.")
        if (i % ( n / 100)) == 0:
            print('Run: ' + str(i) + ', Prozent: ' + str(round(i / n * 100, 3)) + ' %')

    print(f"Script finished successfully after {counter_call_refprop} refprop calls")





