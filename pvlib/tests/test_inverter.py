# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

from pandas.util.testing import assert_series_equal
from numpy.testing import assert_allclose

from pvlib import inverter
from conftest import needs_numpy_1_10


def test_adr(adr_inverter_parameters):
    vdcs = pd.Series([135, 154, 390, 420, 551])
    pdcs = pd.Series([135, 1232, 1170, 420, 551])

    pacs = inverter.adr(vdcs, pdcs, adr_inverter_parameters)
    assert_series_equal(pacs, pd.Series([np.nan, 1161.5745, 1116.4459,
                                         382.6679, np.nan]))


def test_adr_vtol(adr_inverter_parameters):
    vdcs = pd.Series([135, 154, 390, 420, 551])
    pdcs = pd.Series([135, 1232, 1170, 420, 551])

    pacs = inverter.adr(vdcs, pdcs, adr_inverter_parameters, vtol=0.20)
    assert_series_equal(pacs, pd.Series([104.8223, 1161.5745, 1116.4459,
                                         382.6679, 513.3385]))


def test_adr_float(adr_inverter_parameters):
    vdcs = 154.
    pdcs = 1232.

    pacs = inverter.adr(vdcs, pdcs, adr_inverter_parameters)
    assert_allclose(pacs, 1161.5745)


def test_adr_invalid_and_night(sam_data):
    # also tests if inverter.adr can read the output from pvsystem.retrieve_sam
    inverters = sam_data['adrinverter']
    testinv = 'Zigor__Sunzet_3_TL_US_240V__CEC_2011_'
    vdcs = np.array([39.873036, 0., np.nan, 420])
    pdcs = np.array([188.09182, 0., 420, np.nan])

    pacs = inverter.adr(vdcs, pdcs, inverters[testinv])
    assert_allclose(pacs, np.array([np.nan, -0.25, np.nan, np.nan]))


def test_sandia(cec_inverter_parameters):
    vdcs = pd.Series(np.linspace(0, 50, 3))
    idcs = pd.Series(np.linspace(0, 11, 3))
    pdcs = idcs * vdcs

    pacs = inverter.sandia(vdcs, pdcs, cec_inverter_parameters)
    assert_series_equal(pacs, pd.Series([-0.020000, 132.004308, 250.000000]))


def test_sandia_float(cec_inverter_parameters):
    vdcs = 25.
    idcs = 5.5
    pdcs = idcs * vdcs

    pacs = inverter.sandia(vdcs, pdcs, cec_inverter_parameters)
    assert_allclose(pacs, 132.004278, 5)


def test_sandia_Pnt_micro():
    """
    Test for issue #140, where some microinverters were giving a positive AC
    power output when the DC power was 0.
    """
    inverter_parameters = {
        'Name': 'Enphase Energy: M250-60-2LL-S2x (-ZC) (-NA) 208V [CEC 2013]',
        'Vac': 208.0,
        'Paco': 240.0,
        'Pdco': 250.5311318,
        'Vdco': 32.06160667,
        'Pso': 1.12048857,
        'C0': -5.76E-05,
        'C1': -6.24E-04,
        'C2': 8.09E-02,
        'C3': -0.111781106,
        'Pnt': 0.043,
        'Vdcmax': 48.0,
        'Idcmax': 9.8,
        'Mppt_low': 27.0,
        'Mppt_high': 39.0,
    }
    vdcs = pd.Series(np.linspace(0, 50, 3))
    idcs = pd.Series(np.linspace(0, 11, 3))
    pdcs = idcs * vdcs

    pacs = inverter.sandia(vdcs, pdcs, inverter_parameters)
    assert_series_equal(pacs, pd.Series([-0.043, 132.545914746, 240.0]))


def test_pvwatts_scalars():
    expected = 85.58556604752516
    out = inverter.pvwatts(90, 100, 0.95)
    assert_allclose(out, expected)
    # GH 675
    expected = 0.
    out = inverter.pvwatts(0., 100)
    assert_allclose(out, expected)


def test_pvwatts_possible_negative():
    # pvwatts could return a negative value for (pdc / pdc0) < 0.006
    # unless it is clipped. see GH 541 for more
    expected = 0
    out = inverter.pvwatts(0.001, 1)
    assert_allclose(out, expected)


@needs_numpy_1_10
def test_pvwatts_arrays():
    pdc = np.array([[np.nan], [0], [50], [100]])
    pdc0 = 100
    expected = np.array([[np.nan],
                         [0.],
                         [47.60843624],
                         [95.]])
    out = inverter.pvwatts(pdc, pdc0, 0.95)
    assert_allclose(out, expected, equal_nan=True)


def test_pvwatts_series():
    pdc = pd.Series([np.nan, 0, 50, 100])
    pdc0 = 100
    expected = pd.Series(np.array([np.nan, 0., 47.608436, 95.]))
    out = inverter.pvwatts(pdc, pdc0, 0.95)
    assert_series_equal(expected, out)
