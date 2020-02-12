"""
test iotools for PSM3
"""

import os
from pvlib.iotools import psm3
from conftest import DATA_DIR
import numpy as np
import pandas as pd
import pytest
from requests import HTTPError
from io import StringIO
import warnings

TMY_TEST_DATA = DATA_DIR / 'test_psm3_tmy-2017.csv'
YEAR_TEST_DATA = DATA_DIR / 'test_psm3_2017.csv'
MANUAL_TEST_DATA = DATA_DIR / 'test_read_psm3.csv'
LATITUDE, LONGITUDE = 40.5137, -108.5449
HEADER_FIELDS = [
    'Source', 'Location ID', 'City', 'State', 'Country', 'Latitude',
    'Longitude', 'Time Zone', 'Elevation', 'Local Time Zone',
    'Dew Point Units', 'DHI Units', 'DNI Units', 'GHI Units',
    'Temperature Units', 'Pressure Units', 'Wind Direction Units',
    'Wind Speed', 'Surface Albedo Units', 'Version']
PVLIB_EMAIL = 'pvlib-admin@googlegroups.com'


@pytest.fixture(scope="module")
def nrel_api_key():
    """Supplies pvlib-python's NREL Developer Network API key.

    Azure Pipelines CI utilizes a secret variable set to NREL_API_KEY
    to mitigate failures associated with using the default key of
    "DEMO_KEY". A user is capable of using their own key this way if
    desired however the default key should suffice for testing purposes.
    """
    try:
        demo_key = os.environ["NREL_API_KEY"]
    except KeyError:
        warnings.warn(
            "WARNING: NREL API KEY environment variable not set! "
            "Using DEMO_KEY instead. Unexpected failures may occur."
        )
        demo_key = 'DEMO_KEY'
    return demo_key


def assert_psm3_equal(header, data, expected):
    """check consistency of PSM3 data"""
    # check datevec columns
    assert np.allclose(data.Year, expected.Year)
    assert np.allclose(data.Month, expected.Month)
    assert np.allclose(data.Day, expected.Day)
    assert np.allclose(data.Hour, expected.Hour)
    assert np.allclose(data.Minute, expected.Minute)
    # check data columns
    assert np.allclose(data.GHI, expected.GHI)
    assert np.allclose(data.DNI, expected.DNI)
    assert np.allclose(data.DHI, expected.DHI)
    assert np.allclose(data.Temperature, expected.Temperature)
    assert np.allclose(data.Pressure, expected.Pressure)
    assert np.allclose(data['Dew Point'], expected['Dew Point'])
    assert np.allclose(data['Surface Albedo'], expected['Surface Albedo'])
    assert np.allclose(data['Wind Speed'], expected['Wind Speed'])
    assert np.allclose(data['Wind Direction'], expected['Wind Direction'])
    # check header
    for hf in HEADER_FIELDS:
        assert hf in header
    # check timezone
    assert (data.index.tzinfo.zone == 'Etc/GMT%+d' % -header['Time Zone'])


@pytest.mark.remote_data
@pytest.mark.flaky(reruns=5, reruns_delay=2)
def test_get_psm3_tmy(nrel_api_key):
    """test get_psm3 with a TMY"""
    header, data = psm3.get_psm3(LATITUDE, LONGITUDE, nrel_api_key,
                                 PVLIB_EMAIL, names='tmy-2017')
    expected = pd.read_csv(TMY_TEST_DATA)
    assert_psm3_equal(header, data, expected)


@pytest.mark.remote_data
@pytest.mark.flaky(reruns=5, reruns_delay=2)
def test_get_psm3_singleyear(nrel_api_key):
    """test get_psm3 with a single year"""
    header, data = psm3.get_psm3(LATITUDE, LONGITUDE, nrel_api_key,
                                 PVLIB_EMAIL, names='2017', interval=30)
    expected = pd.read_csv(YEAR_TEST_DATA)
    assert_psm3_equal(header, data, expected)


@pytest.mark.remote_data
@pytest.mark.flaky(reruns=5, reruns_delay=2)
def test_get_psm3_check_leap_day(nrel_api_key):
    _, data_2012 = psm3.get_psm3(LATITUDE, LONGITUDE, nrel_api_key,
                                 PVLIB_EMAIL, names="2012", interval=60,
                                 leap_day=True)
    assert len(data_2012) == (8760 + 24)


@pytest.mark.parametrize('latitude, longitude, api_key, names, interval',
                         [(LATITUDE, LONGITUDE, 'BAD', 'tmy-2017', 60),
                          (51, -5, nrel_api_key, 'tmy-2017', 60),
                          (LATITUDE, LONGITUDE, nrel_api_key, 'bad', 60),
                          (LATITUDE, LONGITUDE, nrel_api_key, '2017', 15),
                          ])
@pytest.mark.remote_data
@pytest.mark.flaky(reruns=5, reruns_delay=2)
def test_get_psm3_tmy_errors(
    latitude, longitude, api_key, names, interval
):
    """Test get_psm3() for multiple erroneous input scenarios.

    These scenarios include:
    * Bad API key -> HTTP 403 forbidden because api_key is rejected
    * Bad latitude/longitude -> Coordinates were not found in the NSRDB.
    * Bad name -> Name is not one of the available options.
    * Bad interval, single year -> Intervals can only be 30 or 60 minutes.
    """
    with pytest.raises(HTTPError) as excinfo:
        psm3.get_psm3(latitude, longitude, api_key, PVLIB_EMAIL,
                      names=names, interval=interval)
    # ensure the HTTPError caught isn't due to overuse of the API key
    assert "OVER_RATE_LIMIT" not in str(excinfo.value)


@pytest.fixture
def io_input(request):
    """file-like object for parse_psm3"""
    with MANUAL_TEST_DATA.open() as f:
        data = f.read()
    obj = StringIO(data)
    return obj


def test_parse_psm3(io_input):
    """test parse_psm3"""
    header, data = psm3.parse_psm3(io_input)
    expected = pd.read_csv(YEAR_TEST_DATA)
    assert_psm3_equal(header, data, expected)


def test_read_psm3():
    """test read_psm3"""
    header, data = psm3.read_psm3(MANUAL_TEST_DATA)
    expected = pd.read_csv(YEAR_TEST_DATA)
    assert_psm3_equal(header, data, expected)
