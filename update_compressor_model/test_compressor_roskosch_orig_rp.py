"""
testcase for compressor_roskosch model

Verification values obtained before modification of global variables etc
but AFTER changing to fluid mixtures and refprop, validation of these parts still to be performed

author: Alexandra Welp
"""
import sys
sys.path.insert(1, "C:/Users/welp/sciebo/Kollaboration")
sys.path.insert(1, "C:/Users/welp/sciebo/Kollaboration/Carbatpy/carbaty/carbatpy")
import compressor_roskosch_orig_rp_aw as comros
import numpy as np
import compressor_welp_ivp_changed_interation as comwel
import pytest
import compressor_roskosch_orig_rp_june2023 as comros_orig

def test_basic_script():
    IS = 360  # Anzahl der differentiellen Schritte für einen Zyklus
    IS0 = IS
    pV = np.zeros(8, float)
    pZ = np.zeros(7, float)
    pZyk = np.zeros(2, float)
    z_it = np.zeros([IS, 16])
    # fluid = []
    comp = [1.0]  # must be checked BA
    fluid = 'Propane * Butane'
    comp = [1.0, 0.]
    pe = comros_orig.z_Tx(263, 0, fluid, comp)[1]  # fl.zs_kg(['T','q'],[0.,0.],['p'],fluid)[0]
    pa = comros_orig.z_Tx(355, 0, fluid, comp)[1]  # fl.zs_kg(['T','q'],[35.,0.],['p'],fluid)[0]
    dt_all = np.linspace(9.5, 20.5, 3)
    out = []
    pV = [34e-3, 34e-3, 3.5, .04, .06071, 48.916, 50., 50. / 2., 2.]  # parameter see above
    for dt in dt_all:
        o1 = comros_orig.getETA(dt + 273.15, pe, pa, fluid, comp)
        # o1.append((np.max(z_it[:,11]) - np.min(z_it[:,11]) * pV[7]))  # Massenstrom
        out.append(o1)
        print(dt, o1)
    actual_out = [[0.69124745, 0.40855443],[0.69800568, 0.41455612],[0.70437112, 0.42013682]]
    assert round(pe, 2) == 343.57
    assert round(pa, 2) == 3241.82
    assert (round(out[0][0], 3) == round(actual_out[0][0], 3))
    assert (round(out[0][1], 3) == round(actual_out[0][1], 3))
    assert (round(out[1][0], 3) == round(actual_out[1][0], 3))
    assert (round(out[1][1], 3) == round(actual_out[1][1], 3))
    assert (round(out[2][0], 3) == round(actual_out[2][0], 3))
    assert (round(out[2][1], 3) == round(actual_out[2][1], 3))


def test_overall_script():
    IS = 360  # Anzahl der differentiellen Schritte für einen Zyklus
    IS0 = IS
    pV = np.zeros(8, float)
    pZ = np.zeros(7, float)
    pZyk = np.zeros(2, float)
    z_it = np.zeros([IS, 16])
    # fluid = []
    comp = [1.0]  # must be checked BA
    fluid = 'Propane * Butane'
    comp = [1.0, 0.]
    pe = comros.z_Tx(263, 0, fluid, comp)[1]  # fl.zs_kg(['T','q'],[0.,0.],['p'],fluid)[0]
    pa = comros.z_Tx(355, 0, fluid, comp)[1]  # fl.zs_kg(['T','q'],[35.,0.],['p'],fluid)[0]
    dt_all = np.linspace(9.5, 20.5, 3)
    out = []
    pV = [34e-3, 34e-3, 3.5, .04, .06071, 48.916, 50., 50. / 2., 2.]  # parameter see above
    for dt in dt_all:
        o1 = comros.getETA(dt + 273.15, pe, pa, fluid, comp, pV, pZ, z_it, IS, pZyk, IS0)
        # o1.append((np.max(z_it[:,11]) - np.min(z_it[:,11]) * pV[7]))  # Massenstrom
        out.append(o1)
        print(dt, o1)
    actual_out = [[0.69124745, 0.40855443],[0.69800568, 0.41455612],[0.70437112, 0.42013682]]
    assert round(pe, 2) == 343.57
    assert round(pa, 2) == 3241.82
    assert (round(out[0][0], 3) == round(actual_out[0][0], 3))
    assert (round(out[0][1], 3) == round(actual_out[0][1], 3))
    assert (round(out[1][0], 3) == round(actual_out[1][0], 3))
    assert (round(out[1][1], 3) == round(actual_out[1][1], 3))
    assert (round(out[2][0], 3) == round(actual_out[2][0], 3))
    assert (round(out[2][1], 3) == round(actual_out[2][1], 3))

def test_overall_script_welp():
    resolution = 3600
    fluid = 'Propane * Butane'
    comp = [1.0, 0.]
    pe = comros.z_Tx(263, 0, fluid, comp)[1]  # fl.zs_kg(['T','q'],[0.,0.],['p'],fluid)[0]
    pa = comros.z_Tx(355, 0, fluid, comp)[1]  # fl.zs_kg(['T','q'],[35.,0.],['p'],fluid)[0]
    dt_all = np.linspace(9.5, 20.5, 3)
    out = []
    for dt in dt_all:
        result, count, y_timetrack_m, y_timetrack_u, y_timetrack_t, is_eff, degree_delivery = comwel.set_up(dt + 273.15, pe, pa, resolution)
        # o1.append((np.max(z_it[:,11]) - np.min(z_it[:,11]) * pV[7]))  # Massenstrom
        out.append([is_eff, degree_delivery])
        print(dt, is_eff, degree_delivery)
    actual_out = [[0.69124745, 0.40855443],[0.69800568, 0.41455612],[0.70437112, 0.42013682]]

    assert round(pe, 2) == 343.57
    assert round(pa, 2) == 3241.82
    assert (round(out[0][0], 3) == round(actual_out[0][0], 3))
    assert (round(out[0][1], 3) == round(actual_out[0][1], 3))
    assert (round(out[1][0], 3) == round(actual_out[1][0], 3))
    assert (round(out[1][1], 3) == round(actual_out[1][1], 3))
    assert (round(out[2][0], 3) == round(actual_out[2][0], 3))
    assert (round(out[2][1], 3) == round(actual_out[2][1], 3))