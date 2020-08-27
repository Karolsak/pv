# -*- coding: utf-8 -*-
"""Test losses"""

import datetime
import numpy as np
import pandas as pd
from conftest import assert_series_equal
from pvlib.soiling import hsu, kimber
from pvlib.iotools import read_tmy3
from conftest import DATA_DIR
import pytest


@pytest.fixture
def expected_output():
    # Sample output (calculated manually)
    dt = pd.date_range(start=pd.Timestamp(2019, 1, 1, 0, 0, 0),
                       end=pd.Timestamp(2019, 1, 1, 23, 59, 0), freq='1h')

    expected_no_cleaning = pd.Series(
        data=[0.97230454, 0.95036146, 0.93039061, 0.91177978, 0.89427556,
              0.8777455 , 0.86211038, 0.84731759, 0.83332881, 0.82011354,
              0.80764549, 0.79590056, 0.78485556, 0.77448749, 0.76477312,
              0.75568883, 0.74721046, 0.73931338, 0.73197253, 0.72516253,
              0.7188578 , 0.71303268, 0.7076616 , 0.70271919],
        index=dt)
    return expected_no_cleaning

@pytest.fixture
def expected_output_1():
    dt = pd.date_range(start=pd.Timestamp(2019, 1, 1, 0, 0, 0),
        end=pd.Timestamp(2019, 1, 1, 23, 59, 0), freq='1h')
    expected_output_1 = pd.Series(
        data=[0.9872406 , 0.97706269, 0.96769693, 0.95884032, 1.,
              0.9872406 , 0.97706269, 0.96769693, 1.        , 1.        ,
              0.9872406 , 0.97706269, 0.96769693, 0.95884032, 0.95036001,
              0.94218263, 0.93426236, 0.92656836, 0.91907873, 0.91177728,
              0.9046517 , 0.89769238, 0.89089165, 0.88424329],
        index=dt)
    return expected_output_1

@pytest.fixture
def expected_output_2():
    dt = pd.date_range(start=pd.Timestamp(2019, 1, 1, 0, 0, 0),
                       end=pd.Timestamp(2019, 1, 1, 23, 59, 0), freq='1h')
    expected_output_2 = pd.Series(
        data=[0.97229869, 0.95035106, 0.93037619, 0.91176175, 1.,
              1.        , 1.        , 0.97229869, 1.        , 1.        ,
              1.        , 1.        , 0.97229869, 0.95035106, 0.93037619,
              0.91176175, 0.89425431, 1.        , 1.        , 1.        ,
              1.        , 0.97229869, 0.95035106, 0.93037619],
        index=dt)

    return expected_output_2

@pytest.fixture
def rainfall_input():

    dt = pd.date_range(start=pd.Timestamp(2019, 1, 1, 0, 0, 0),
                       end=pd.Timestamp(2019, 1, 1, 23, 59, 0), freq='1h')
    rainfall = pd.Series(
        data=[0., 0., 0., 0., 1., 0., 0., 0., 0.5, 0.5, 0., 0., 0., 0., 0.,
              0., 0.3, 0.3, 0.3, 0.3, 0., 0., 0., 0.], index=dt)
    return rainfall


def test_hsu_no_cleaning(rainfall_input, expected_output):
    """Test Soiling HSU function"""

    rainfall = rainfall_input
    pm2_5 = 1.0
    pm10 = 2.0
    depo_veloc = {'2_5': 1.0e-5, '10': 1.0e-4}
    tilt = 0.
    expected_no_cleaning = expected_output

    result = hsu(rainfall=rainfall, cleaning_threshold=10., tilt=tilt,
                 pm2_5=pm2_5, pm10=pm10, depo_veloc=depo_veloc,
                 rain_accum_period=pd.Timedelta('1h'))
    assert_series_equal(result, expected_no_cleaning)


def test_hsu(rainfall_input, expected_output_2):
    """Test Soiling HSU function with cleanings"""

    rainfall = rainfall_input
    pm2_5 = 1.0
    pm10 = 2.0
    depo_veloc = {'2_5': 1.0e-4, '10': 1.0e-4}
    tilt = 0.

    # three cleaning events at 4:00-6:00, 8:00-11:00, and 17:00-20:00
    result = hsu(rainfall=rainfall, cleaning_threshold=0.5, tilt=tilt,
                 pm2_5=pm2_5, pm10=pm10, depo_veloc=depo_veloc,
                 rain_accum_period=pd.Timedelta('3h'))

    assert_series_equal(result, expected_output_2)


def test_hsu_defaults(rainfall_input, expected_output_1):
    """
    Test Soiling HSU function with default deposition velocity and default rain
    accumulation period.
    """
    result = hsu(
        rainfall=rainfall_input, cleaning_threshold=0.5, tilt=0.0,
        pm2_5=1.0e-2,pm10=2.0e-2)
    assert np.allclose(result.values, expected_output_1)


@pytest.fixture
def greensboro_rain():
    # get TMY3 data with rain
    greensboro, _ = read_tmy3(DATA_DIR / '723170TYA.CSV', coerce_year=1990)
    return greensboro.Lprecipdepth


@pytest.fixture
def expected_kimber_nowash():
    return pd.read_csv(
        DATA_DIR / 'greensboro_kimber_soil_nowash.dat',
        parse_dates=True, index_col='timestamp')


def test_kimber_nowash(greensboro_rain, expected_kimber_nowash):
    """Test Kimber soiling model with no manual washes"""
    # Greensboro typical expected annual rainfall is 8345mm
    assert greensboro_rain.sum() == 8345
    # calculate soiling with no wash dates
    nowash = kimber(greensboro_rain)
    # test no washes
    assert np.allclose(nowash.values, expected_kimber_nowash['soiling'].values)


@pytest.fixture
def expected_kimber_manwash():
    return pd.read_csv(
        DATA_DIR / 'greensboro_kimber_soil_manwash.dat',
        parse_dates=True, index_col='timestamp')


def test_kimber_manwash(greensboro_rain, expected_kimber_manwash):
    """Test Kimber soiling model with a manual wash"""
    # a manual wash date
    manwash = [datetime.date(1990, 2, 15), ]
    # calculate soiling with manual wash
    manwash = kimber(greensboro_rain, manual_wash_dates=manwash)
    # test manual wash
    assert np.allclose(
        manwash.values,
        expected_kimber_manwash['soiling'].values)


@pytest.fixture
def expected_kimber_norain():
    # expected soiling reaches maximum
    soiling_loss_rate = 0.0015
    max_loss_rate = 0.3
    norain = np.ones(8760) * soiling_loss_rate/24
    norain[0] = 0.0
    norain = np.cumsum(norain)
    return np.where(norain > max_loss_rate, max_loss_rate, norain)


def test_kimber_norain(greensboro_rain, expected_kimber_norain):
    """Test Kimber soiling model with no rain"""
    # a year with no rain
    norain = pd.Series(0, index=greensboro_rain.index)
    # calculate soiling with no rain
    norain = kimber(norain)
    # test no rain, soiling reaches maximum
    assert np.allclose(norain.values, expected_kimber_norain)


@pytest.fixture
def expected_kimber_initial_soil():
    # expected soiling reaches maximum
    soiling_loss_rate = 0.0015
    max_loss_rate = 0.3
    norain = np.ones(8760) * soiling_loss_rate/24
    norain[0] = 0.1
    norain = np.cumsum(norain)
    return np.where(norain > max_loss_rate, max_loss_rate, norain)


def test_kimber_initial_soil(greensboro_rain, expected_kimber_initial_soil):
    """Test Kimber soiling model with initial soiling"""
    # a year with no rain
    norain = pd.Series(0, index=greensboro_rain.index)
    # calculate soiling with no rain
    norain = kimber(norain, initial_soiling=0.1)
    # test no rain, soiling reaches maximum
    assert np.allclose(norain.values, expected_kimber_initial_soil)
