"""
test the pvgis IO tools
"""
import json
import numpy as np
import pandas as pd
import pytest
import requests
from pvlib.iotools import get_pvgis_tmy, read_pvgis_tmy
from pvlib.iotools import read_pvgis_hourly  # get_pvgis_hourly,
from ..conftest import DATA_DIR, RERUNS, RERUNS_DELAY, assert_frame_equal


testfile_radiation_csv = DATA_DIR / \
    'pvgis_hourly_Timeseries_45.000_8.000_SA_30deg_0deg_2016_2016.csv'
testfile_pv_json = DATA_DIR / \
    'pvgis_hourly_Timeseries_45.000_8.000_CM_10kWp_CIS_5_2a_2013_2014.json'

index_radiation_csv = \
    pd.date_range('20160101 00:10', freq='1h', periods=14, tz='UTC')
index_pv_json = \
    pd.date_range('2013-01-01 00:55', freq='1h', periods=10, tz='UTC')

columns_radiation_csv = [
    'Gb(i)', 'Gd(i)', 'Gr(i)', 'H_sun', 'T2m', 'WS10m', 'Int']
columns_radiation_csv_mapped = [
    'poa_direct', 'poa_diffuse', 'poa_ground_diffuse', 'solar_elevation',
    'temp_air', 'wind_speed', 'Int']
columns_pv_json = [
    'P', 'Gb(i)', 'Gd(i)', 'Gr(i)', 'H_sun', 'T2m', 'WS10m', 'Int']
columns_pv_json_mapped = [
    'P', 'poa_direct', 'poa_diffuse', 'poa_ground_diffuse', 'solar_elevation',
    'temp_air', 'wind_speed', 'Int']

data_radiation_csv = [
    [0.0, 0.0, 0.0, 0.0, 3.44, 1.43, 0.0],
    [0.0, 0.0, 0.0, 0.0, 2.94, 1.47, 0.0],
    [0.0, 0.0, 0.0, 0.0, 2.43, 1.51, 0.0],
    [0.0, 0.0, 0.0, 0.0, 1.93, 1.54, 0.0],
    [0.0, 0.0, 0.0, 0.0, 2.03, 1.62, 0.0],
    [0.0, 0.0, 0.0, 0.0, 2.14, 1.69, 0.0],
    [0.0, 0.0, 0.0, 0.0, 2.25, 1.77, 0.0],
    [0.0, 0.0, 0.0, 0.0, 3.06, 1.49, 0.0],
    [26.71, 8.28, 0.21, 8.06, 3.87, 1.22, 1.0],
    [14.69, 5.76, 0.16, 14.8, 4.67, 0.95, 1.0],
    [2.19, 0.94, 0.03, 19.54, 5.73, 0.77, 1.0],
    [2.11, 0.94, 0.03, 21.82, 6.79, 0.58, 1.0],
    [4.25, 1.88, 0.05, 21.41, 7.84, 0.4, 1.0],
    [0.0, 0.0, 0.0, 0.0, 7.43, 0.72, 0.0]]
data_pv_json = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 3.01, 1.23, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 2.22, 1.46, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 1.43, 1.7, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.64, 1.93, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.77, 1.8, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.91, 1.66, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 1.05, 1.53, 0.0],
    [3464.5, 270.35, 91.27, 6.09, 6.12, 1.92, 1.44, 0.0],
    [1586.9, 80.76, 83.95, 9.04, 13.28, 2.79, 1.36, 0.0],
    [713.3, 5.18, 70.57, 7.31, 18.56, 3.66, 1.27, 0.0]]

inputs_radiation_csv = {'latitude': 45.0, 'longitude': 8.0, 'elevation': 250.0,
                        'radiation_database': 'PVGIS-SARAH',
                        'Slope': '30 deg.', 'Azimuth': '0 deg.'}

metadata_radiation_csv = {
    'Gb(i)': 'Beam (direct) irradiance on the inclined plane (plane of the array) (W/m2)',  # noqa: F401
    'Gd(i)': 'Diffuse irradiance on the inclined plane (plane of the array) (W/m2)',  # noqa: F401
    'Gr(i)': 'Reflected irradiance on the inclined plane (plane of the array) (W/m2)',  # noqa: F401
    'H_sun': 'Sun height (degree)',
    'T2m': '2-m air temperature (degree Celsius)',
    'WS10m': '10-m total wind speed (m/s)',
    'Int': '1 means solar radiation values are reconstructed'}

inputs_pv_json = {
    'location': {'latitude': 45.0, 'longitude': 8.0, 'elevation': 250.0},
    'meteo_data': {'radiation_db': 'PVGIS-CMSAF', 'meteo_db': 'ERA-Interim',
                   'year_min': 2013, 'year_max': 2014, 'use_horizon': True,
                   'horizon_db': None, 'horizon_data': 'DEM-calculated'},
    'mounting_system': {'two_axis': {
        'slope': {'value': '-', 'optimal': '-'},
        'azimuth': {'value': '-', 'optimal': '-'}}},
    'pv_module': {'technology': 'CIS', 'peak_power': 10.0, 'system_loss': 5.0}}

metadata_pv_json = {'inputs': {'location': {'description': 'Selected location',
    'variables': {'latitude': {'description': 'Latitude',
                               'units': 'decimal degree'},
    'longitude': {'description': 'Longitude', 'units': 'decimal degree'},
    'elevation': {'description': 'Elevation', 'units': 'm'}}},
  'meteo_data': {'description': 'Sources of meteorological data',
   'variables': {'radiation_db': {'description': 'Solar radiation database'},
    'meteo_db': {'description': 'Database used for meteorological variables other than solar radiation'},
    'year_min': {'description': 'First year of the calculations'},
    'year_max': {'description': 'Last year of the calculations'},
    'use_horizon': {'description': 'Include horizon shadows'},
    'horizon_db': {'description': 'Source of horizon data'}}},
  'mounting_system': {'description': 'Mounting system',
   'choices': 'fixed, vertical_axis, inclined_axis, two_axis',
   'fields': {'slope': {'description': 'Inclination angle from the horizontal plane',
     'units': 'degree'},
    'azimuth': {'description': 'Orientation (azimuth) angle of the (fixed) PV system (0 = S, 90 = W, -90 = E)',
     'units': 'degree'}}},
  'pv_module': {'description': 'PV module parameters',
   'variables': {'technology': {'description': 'PV technology'},
    'peak_power': {'description': 'Nominal (peak) power of the PV module',
     'units': 'kW'},
    'system_loss': {'description': 'Sum of system losses', 'units': '%'}}}},
 'outputs': {'hourly': {'type': 'time series',
   'timestamp': 'hourly averages',
   'variables': {'P': {'description': 'PV system power', 'units': 'W'},
    'Gb(i)': {'description': 'Beam (direct) irradiance on the inclined plane (plane of the array)',
     'units': 'W/m2'},
    'Gd(i)': {'description': 'Diffuse irradiance on the inclined plane (plane of the array)',
     'units': 'W/m2'},
    'Gr(i)': {'description': 'Reflected irradiance on the inclined plane (plane of the array)',
     'units': 'W/m2'},
    'H_sun': {'description': 'Sun height', 'units': 'degree'},
    'T2m': {'description': '2-m air temperature', 'units': 'degree Celsius'},
    'WS10m': {'description': '10-m total wind speed', 'units': 'm/s'},
    'Int': {'description': '1 means solar radiation values are reconstructed'}}}}}


@pytest.mark.parametrize('testfile,index,columns,values,metadata_exp,'
                         'inputs_exp,map_variables,pvgis_format', [
    (testfile_radiation_csv, index_radiation_csv, columns_radiation_csv,
     data_radiation_csv, metadata_radiation_csv, inputs_radiation_csv, False, None),
    (testfile_radiation_csv, index_radiation_csv, columns_radiation_csv_mapped,
     data_radiation_csv, metadata_radiation_csv, inputs_radiation_csv, True, 'csv'),
    (testfile_pv_json, index_pv_json, columns_pv_json,
     data_pv_json, metadata_pv_json, inputs_pv_json, False, None),
    (testfile_pv_json, index_pv_json, columns_pv_json_mapped,
     data_pv_json, metadata_pv_json, inputs_pv_json, True, 'json')])
def test_read_pvgis_hourly(testfile, index, columns, values, metadata_exp,
                           inputs_exp, map_variables, pvgis_format):
    expected = pd.DataFrame(index=index, data=values, columns=columns)
    expected['Int'] = expected['Int'].astype(int)
    expected.index.name = 'time'
    expected.index.freq = None
    out, inputs, metadata = read_pvgis_hourly(
        testfile, map_variables=map_variables, pvgis_format=pvgis_format)
    assert_frame_equal(out, expected)
    assert inputs == inputs_exp



# PVGIS TMY tests
@pytest.fixture
def expected():
    return pd.read_csv(DATA_DIR / 'pvgis_tmy_test.dat', index_col='time(UTC)')


@pytest.fixture
def userhorizon_expected():
    return pd.read_json(DATA_DIR / 'tmy_45.000_8.000_userhorizon.json')


@pytest.fixture
def month_year_expected():
    return [
        2009, 2012, 2014, 2010, 2011, 2013, 2011, 2011, 2013, 2013, 2013, 2011]


@pytest.fixture
def inputs_expected():
    return {
        'location': {'latitude': 45.0, 'longitude': 8.0, 'elevation': 250.0},
        'meteo_data': {
            'radiation_db': 'PVGIS-SARAH',
            'meteo_db': 'ERA-Interim',
            'year_min': 2005,
            'year_max': 2016,
            'use_horizon': True,
            'horizon_db': 'DEM-calculated'}}


@pytest.fixture
def epw_meta():
    return {
        'loc': 'LOCATION',
        'city': 'unknown',
        'state-prov': '-',
        'country': 'unknown',
        'data_type': 'ECMWF/ERA',
        'WMO_code': 'unknown',
        'latitude': 45.0,
        'longitude': 8.0,
        'TZ': 1.0,
        'altitude': 250.0}


@pytest.fixture
def meta_expected():
    with (DATA_DIR / 'pvgis_tmy_meta.json').open() as f:
        return json.load(f)


@pytest.fixture
def csv_meta(meta_expected):
    return [
        f"{k}: {v['description']} ({v['units']})" for k, v
        in meta_expected['outputs']['tmy_hourly']['variables'].items()]


@pytest.mark.remote_data
@pytest.mark.flaky(reruns=RERUNS, reruns_delay=RERUNS_DELAY)
def test_get_pvgis_tmy(expected, month_year_expected, inputs_expected,
                       meta_expected):
    pvgis_data = get_pvgis_tmy(45, 8)
    _compare_pvgis_tmy_json(expected, month_year_expected, inputs_expected,
                            meta_expected, pvgis_data)


def _compare_pvgis_tmy_json(expected, month_year_expected, inputs_expected,
                            meta_expected, pvgis_data):
    data, months_selected, inputs, meta = pvgis_data
    # check each column of output separately
    for outvar in meta_expected['outputs']['tmy_hourly']['variables'].keys():
        assert np.allclose(data[outvar], expected[outvar])
    assert np.allclose(
        [_['month'] for _ in months_selected], np.arange(1, 13, 1))
    assert np.allclose(
        [_['year'] for _ in months_selected], month_year_expected)
    inputs_loc = inputs['location']
    assert inputs_loc['latitude'] == inputs_expected['location']['latitude']
    assert inputs_loc['longitude'] == inputs_expected['location']['longitude']
    assert inputs_loc['elevation'] == inputs_expected['location']['elevation']
    inputs_met_data = inputs['meteo_data']
    expected_met_data = inputs_expected['meteo_data']
    assert (
        inputs_met_data['radiation_db'] == expected_met_data['radiation_db'])
    assert inputs_met_data['year_min'] == expected_met_data['year_min']
    assert inputs_met_data['year_max'] == expected_met_data['year_max']
    assert inputs_met_data['use_horizon'] == expected_met_data['use_horizon']
    assert inputs_met_data['horizon_db'] == expected_met_data['horizon_db']
    assert meta == meta_expected


@pytest.mark.remote_data
@pytest.mark.flaky(reruns=RERUNS, reruns_delay=RERUNS_DELAY)
def test_get_pvgis_tmy_kwargs(userhorizon_expected):
    _, _, inputs, _ = get_pvgis_tmy(45, 8, usehorizon=False)
    assert inputs['meteo_data']['use_horizon'] is False
    data, _, _, _ = get_pvgis_tmy(
        45, 8, userhorizon=[0, 10, 20, 30, 40, 15, 25, 5])
    assert np.allclose(
        data['G(h)'], userhorizon_expected['G(h)'].values)
    assert np.allclose(
        data['Gb(n)'], userhorizon_expected['Gb(n)'].values)
    assert np.allclose(
        data['Gd(h)'], userhorizon_expected['Gd(h)'].values)
    _, _, inputs, _ = get_pvgis_tmy(45, 8, startyear=2005)
    assert inputs['meteo_data']['year_min'] == 2005
    _, _, inputs, _ = get_pvgis_tmy(45, 8, endyear=2016)
    assert inputs['meteo_data']['year_max'] == 2016


@pytest.mark.remote_data
@pytest.mark.flaky(reruns=RERUNS, reruns_delay=RERUNS_DELAY)
def test_get_pvgis_tmy_basic(expected, meta_expected):
    pvgis_data = get_pvgis_tmy(45, 8, outputformat='basic')
    _compare_pvgis_tmy_basic(expected, meta_expected, pvgis_data)


def _compare_pvgis_tmy_basic(expected, meta_expected, pvgis_data):
    data, _, _, _ = pvgis_data
    # check each column of output separately
    for outvar in meta_expected['outputs']['tmy_hourly']['variables'].keys():
        assert np.allclose(data[outvar], expected[outvar])


@pytest.mark.remote_data
@pytest.mark.flaky(reruns=RERUNS, reruns_delay=RERUNS_DELAY)
def test_get_pvgis_tmy_csv(expected, month_year_expected, inputs_expected,
                           meta_expected, csv_meta):
    pvgis_data = get_pvgis_tmy(45, 8, outputformat='csv')
    _compare_pvgis_tmy_csv(expected, month_year_expected, inputs_expected,
                           meta_expected, csv_meta, pvgis_data)


def _compare_pvgis_tmy_csv(expected, month_year_expected, inputs_expected,
                           meta_expected, csv_meta, pvgis_data):
    data, months_selected, inputs, meta = pvgis_data
    # check each column of output separately
    for outvar in meta_expected['outputs']['tmy_hourly']['variables'].keys():
        assert np.allclose(data[outvar], expected[outvar])
    assert np.allclose(
        [_['month'] for _ in months_selected], np.arange(1, 13, 1))
    assert np.allclose(
        [_['year'] for _ in months_selected], month_year_expected)
    assert inputs['latitude'] == inputs_expected['location']['latitude']
    assert inputs['longitude'] == inputs_expected['location']['longitude']
    assert inputs['elevation'] == inputs_expected['location']['elevation']
    for meta_value in meta:
        if not meta_value:
            continue
        # this copyright text tends to change (copyright year range increments
        # annually, e.g.), so just check the beginning of it:
        if meta_value.startswith('PVGIS (c) European'):
            continue
        assert meta_value in csv_meta


@pytest.mark.remote_data
@pytest.mark.flaky(reruns=RERUNS, reruns_delay=RERUNS_DELAY)
def test_get_pvgis_tmy_epw(expected, epw_meta):
    pvgis_data = get_pvgis_tmy(45, 8, outputformat='epw')
    _compare_pvgis_tmy_epw(expected, epw_meta, pvgis_data)


def _compare_pvgis_tmy_epw(expected, epw_meta, pvgis_data):
    data, _, _, meta = pvgis_data
    assert np.allclose(data.ghi, expected['G(h)'])
    assert np.allclose(data.dni, expected['Gb(n)'])
    assert np.allclose(data.dhi, expected['Gd(h)'])
    assert np.allclose(data.temp_air, expected['T2m'])
    assert meta == epw_meta


@pytest.mark.remote_data
@pytest.mark.flaky(reruns=RERUNS, reruns_delay=RERUNS_DELAY)
def test_get_pvgis_tmy_error():
    err_msg = 'outputformat: Incorrect value.'
    with pytest.raises(requests.HTTPError, match=err_msg):
        get_pvgis_tmy(45, 8, outputformat='bad')
    with pytest.raises(requests.HTTPError, match='404 Client Error'):
        get_pvgis_tmy(45, 8, url='https://re.jrc.ec.europa.eu/')


def test_read_pvgis_tmy_json(expected, month_year_expected, inputs_expected,
                             meta_expected):
    fn = DATA_DIR / 'tmy_45.000_8.000_2005_2016.json'
    # infer outputformat from file extensions
    pvgis_data = read_pvgis_tmy(fn)
    _compare_pvgis_tmy_json(expected, month_year_expected, inputs_expected,
                            meta_expected, pvgis_data)
    # explicit pvgis outputformat
    pvgis_data = read_pvgis_tmy(fn, pvgis_format='json')
    _compare_pvgis_tmy_json(expected, month_year_expected, inputs_expected,
                            meta_expected, pvgis_data)
    with fn.open('r') as fbuf:
        pvgis_data = read_pvgis_tmy(fbuf, pvgis_format='json')
        _compare_pvgis_tmy_json(expected, month_year_expected, inputs_expected,
                                meta_expected, pvgis_data)


def test_read_pvgis_tmy_epw(expected, epw_meta):
    fn = DATA_DIR / 'tmy_45.000_8.000_2005_2016.epw'
    # infer outputformat from file extensions
    pvgis_data = read_pvgis_tmy(fn)
    _compare_pvgis_tmy_epw(expected, epw_meta, pvgis_data)
    # explicit pvgis outputformat
    pvgis_data = read_pvgis_tmy(fn, pvgis_format='epw')
    _compare_pvgis_tmy_epw(expected, epw_meta, pvgis_data)
    with fn.open('r') as fbuf:
        pvgis_data = read_pvgis_tmy(fbuf, pvgis_format='epw')
        _compare_pvgis_tmy_epw(expected, epw_meta, pvgis_data)


def test_read_pvgis_tmy_csv(expected, month_year_expected, inputs_expected,
                            meta_expected, csv_meta):
    fn = DATA_DIR / 'tmy_45.000_8.000_2005_2016.csv'
    # infer outputformat from file extensions
    pvgis_data = read_pvgis_tmy(fn)
    _compare_pvgis_tmy_csv(expected, month_year_expected, inputs_expected,
                           meta_expected, csv_meta, pvgis_data)
    # explicit pvgis outputformat
    pvgis_data = read_pvgis_tmy(fn, pvgis_format='csv')
    _compare_pvgis_tmy_csv(expected, month_year_expected, inputs_expected,
                           meta_expected, csv_meta, pvgis_data)
    with fn.open('rb') as fbuf:
        pvgis_data = read_pvgis_tmy(fbuf, pvgis_format='csv')
        _compare_pvgis_tmy_csv(expected, month_year_expected, inputs_expected,
                               meta_expected, csv_meta, pvgis_data)


def test_read_pvgis_tmy_basic(expected, meta_expected):
    fn = DATA_DIR / 'tmy_45.000_8.000_2005_2016.txt'
    # XXX: can't infer outputformat from file extensions for basic
    with pytest.raises(ValueError, match="pvgis format 'txt' was unknown"):
        read_pvgis_tmy(fn)
    # explicit pvgis outputformat
    pvgis_data = read_pvgis_tmy(fn, pvgis_format='basic')
    _compare_pvgis_tmy_basic(expected, meta_expected, pvgis_data)
    with fn.open('rb') as fbuf:
        pvgis_data = read_pvgis_tmy(fbuf, pvgis_format='basic')
        _compare_pvgis_tmy_basic(expected, meta_expected, pvgis_data)
        # file buffer raises TypeError if passed to pathlib.Path()
        with pytest.raises(TypeError):
            read_pvgis_tmy(fbuf)


def test_read_pvgis_tmy_exception():
    bad_outputformat = 'bad'
    err_msg = f"pvgis format '{bad_outputformat:s}' was unknown"
    with pytest.raises(ValueError, match=err_msg):
        read_pvgis_tmy('filename', pvgis_format=bad_outputformat)
