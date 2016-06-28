import datetime
import itertools

import numpy as np
import pandas as pd

import pytest
from numpy.testing import assert_allclose

from pvlib.location import Location
from pvlib import solarposition
from pvlib import atmosphere


# setup times and location to be tested.
times = pd.date_range(start=datetime.datetime(2014,6,24),
                      end=datetime.datetime(2014,6,26), freq='1Min')

tus = Location(32.2, -111, 'US/Arizona', 700)

times_localized = times.tz_localize(tus.tz)

ephem_data = solarposition.get_solarposition(times_localized, tus.latitude,
                                             tus.longitude)


# need to add physical tests instead of just functional tests

def test_pres2alt():
    atmosphere.pres2alt(100000)


def test_alt2press():
    atmosphere.pres2alt(1000)


@pytest.mark.parametrize("model",
    ['simple', 'kasten1966', 'youngirvine1967', 'kastenyoung1989',
     'gueymard1993', 'young1994', 'pickering2002'])
def test_airmass(model):
    atmosphere.relativeairmass(ephem_data['zenith'], model)


def test_airmass_invalid():
    with pytest.raises(ValueError):
        atmosphere.relativeairmass(ephem_data['zenith'], 'invalid')


def test_absoluteairmass():
    relative_am = atmosphere.relativeairmass(ephem_data['zenith'], 'simple')
    atmosphere.absoluteairmass(relative_am)
    atmosphere.absoluteairmass(relative_am, pressure=100000)


def test_absoluteairmass_numeric():
    atmosphere.absoluteairmass(2)


def test_absoluteairmass_nan():
    np.testing.assert_equal(np.nan, atmosphere.absoluteairmass(np.nan))


def test_gueymard94_pw():
    temp_air = np.array([0, 20, 40])
    relative_humidity = np.array([0, 30, 100])
    temps_humids = np.array(
        list(itertools.product(temp_air, relative_humidity)))
    pws = atmosphere.gueymard94_pw(temps_humids[:, 0], temps_humids[:, 1])

    expected = np.array(
        [  0.1       ,   0.33702061,   1.12340202,   0.1       ,
         1.12040963,   3.73469877,   0.1       ,   3.44859767,  11.49532557])

    assert_allclose(pws, expected, atol=0.01)


@pytest.mark.parametrize("module_type,expect", [
    ('cdte', np.array(
        [[ 0.99134828,  0.97701063,  0.93975103],
         [ 1.02852847,  1.01874908,  0.98604776],
         [ 1.04722476,  1.03835703,  1.00656735]])),
    ('monosi', np.array(
        [[ 0.9782842 ,  1.02092726,  1.03602157],
         [ 0.9859024 ,  1.0302268 ,  1.04700244],
         [ 0.98885429,  1.03351495,  1.05062687]])),
    ('polysi', np.array(
        [[ 0.9774921 ,  1.01757872,  1.02649543],
         [ 0.98947361,  1.0314545 ,  1.04226547],
         [ 0.99403107,  1.03639082,  1.04758064]]))
])
def test_first_solar_spectral_correction(module_type, expect):
    ams = np.array([1, 3, 5])
    pws = np.array([1, 3, 5])
    ams, pws = np.meshgrid(ams, pws)
    out = atmosphere.first_solar_spectral_correction(pws, ams, module_type)
    assert_allclose(out, expect, atol=0.001)


def test_first_solar_spectral_correction_supplied():
    # use the cdte coeffs
    coeffs = (0.87102, -0.040543, -0.00929202, 0.10052, 0.073062, -0.0034187)
    out = atmosphere.first_solar_spectral_correction(1, 1, coefficients=coeffs)
    expected = 0.99134828
    assert_allclose(out, expected, atol=1e-3)


def test_first_solar_spectral_correction_ambiguous():
    with pytest.raises(TypeError):
        atmosphere.first_solar_spectral_correction(1, 1)
