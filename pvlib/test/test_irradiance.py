import datetime
from collections import OrderedDict

import numpy as np
import pandas as pd

import pytest
from numpy.testing import assert_almost_equal, assert_allclose

from pandas.util.testing import assert_frame_equal, assert_series_equal

from pvlib import atmosphere, irradiance, solarposition
from pvlib._deprecation import pvlibDeprecationWarning
from pvlib.location import Location

from conftest import (fail_on_pvlib_version, needs_numpy_1_10, pandas_0_22,
                      requires_ephem, requires_numba)


# fixtures create realistic test input data
# test input data generated at Location(32.2, -111, 'US/Arizona', 700)
# test input data is hard coded to avoid dependencies on other parts of pvlib


@pytest.fixture
def times():
    # must include night values
    return pd.date_range(start='20140624', freq='6H', periods=4,
                         tz='US/Arizona')


@pytest.fixture
def irrad_data(times):
    return pd.DataFrame(np.array(
        [[   0.        ,    0.        ,    0.        ],
         [  79.73860422,  316.1949056 ,   40.46149818],
         [1042.48031487,  939.95469881,  118.45831879],
         [ 257.20751138,  646.22886049,   62.03376265]]),
        columns=['ghi', 'dni', 'dhi'], index=times)


@pytest.fixture
def ephem_data(times):
    return pd.DataFrame(np.array(
        [[124.0390863 , 124.0390863 , -34.0390863 , -34.0390863 ,
          352.69550699,  -2.36677158],
         [ 82.85457044,  82.97705621,   7.14542956,   7.02294379,
           66.71410338,  -2.42072165],
         [ 10.56413562,  10.56725766,  79.43586438,  79.43274234,
          144.76567754,  -2.47457321],
         [ 72.41687122,  72.46903556,  17.58312878,  17.53096444,
          287.04104128,  -2.52831909]]),
        columns=['apparent_zenith', 'zenith', 'apparent_elevation',
                 'elevation', 'azimuth', 'equation_of_time'],
        index=times)


@pytest.fixture
def dni_et(times):
    return np.array(
        [1321.1655834833093, 1321.1655834833093, 1321.1655834833093,
         1321.1655834833093])


@pytest.fixture
def relative_airmass(times):
    return pd.Series([np.nan, 7.58831596, 1.01688136, 3.27930443], times)


@fail_on_pvlib_version('0.7')
def test_deprecated_07():
    with pytest.warns(pvlibDeprecationWarning):
        irradiance.extraradiation(300)
    with pytest.warns(pvlibDeprecationWarning):
        irradiance.grounddiffuse(40, 900)
    with pytest.warns(pvlibDeprecationWarning):
        irradiance.total_irrad(32, 180, 10, 180, 0, 0, 0, 1400, 1)
    with pytest.warns(pvlibDeprecationWarning):
        irradiance.globalinplane(0, 1000, 100, 10)


# setup for et rad test. put it here for readability
timestamp = pd.Timestamp('20161026')
dt_index = pd.DatetimeIndex([timestamp])
doy = timestamp.dayofyear
dt_date = timestamp.date()
dt_datetime = datetime.datetime.combine(dt_date, datetime.time(0))
dt_np64 = np.datetime64(dt_datetime)
value = 1383.636203


@pytest.mark.parametrize('input, expected', [
    (doy, value),
    (np.float64(doy), value),
    (dt_date, value),
    (dt_datetime, value),
    (dt_np64, value),
    (np.array([doy]), np.array([value])),
    (pd.Series([doy]), np.array([value])),
    (dt_index, pd.Series([value], index=dt_index)),
    (timestamp, value)
])
@pytest.mark.parametrize('method', [
    'asce', 'spencer', 'nrel', requires_ephem('pyephem')])
def test_get_extra_radiation(input, expected, method):
    out = irradiance.get_extra_radiation(input)
    assert_allclose(out, expected, atol=1)


@requires_numba
def test_get_extra_radiation_nrel_numba(times):
    result = irradiance.get_extra_radiation(times, method='nrel', how='numba',
                                            numthreads=8)
    assert_allclose(result, [1322.332316, 1322.296282, 1322.261205, 1322.227091])


def test_get_extra_radiation_epoch_year():
    out = irradiance.get_extra_radiation(doy, method='nrel', epoch_year=2012)
    assert_allclose(out, 1382.4926804890767, atol=0.1)


def test_get_extra_radiation_invalid():
    with pytest.raises(ValueError):
        irradiance.get_extra_radiation(300, method='invalid')


def test_grounddiffuse_simple_float():
    result = irradiance.get_ground_diffuse(40, 900)
    assert_allclose(result, 26.32000014911496)


def test_grounddiffuse_simple_series(irrad_data):
    ground_irrad = irradiance.get_ground_diffuse(40, irrad_data['ghi'])
    assert ground_irrad.name == 'diffuse_ground'


def test_grounddiffuse_albedo_0(irrad_data):
    ground_irrad = irradiance.get_ground_diffuse(40, irrad_data['ghi'], albedo=0)
    assert 0 == ground_irrad.all()


def test_grounddiffuse_albedo_invalid_surface(irrad_data):
    with pytest.raises(KeyError):
        irradiance.get_ground_diffuse(40, irrad_data['ghi'], surface_type='invalid')


def test_grounddiffuse_albedo_surface(irrad_data):
    result = irradiance.get_ground_diffuse(40, irrad_data['ghi'],
                                           surface_type='sand')
    assert_allclose(result, [0, 3.731058, 48.778813, 12.035025], atol=1e-4)


def test_isotropic_float():
    result = irradiance.isotropic(40, 100)
    assert_allclose(result, 88.30222215594891)


def test_isotropic_series(irrad_data):
    result = irradiance.isotropic(40, irrad_data['dhi'])
    assert_allclose(result, [0, 35.728402, 104.601328, 54.777191], atol=1e-4)


def test_klucher_series_float():
    # klucher inputs
    surface_tilt, surface_azimuth = 40.0, 180.0
    dhi, ghi = 100.0, 900.0
    solar_zenith, solar_azimuth = 20.0, 180.0
    # expect same result for floats and pd.Series
    expected = irradiance.klucher(
        surface_tilt, surface_azimuth,
        pd.Series(dhi), pd.Series(ghi),
        pd.Series(solar_zenith), pd.Series(solar_azimuth)
    )  # 94.99429931664851
    result = irradiance.klucher(
        surface_tilt, surface_azimuth, dhi, ghi, solar_zenith, solar_azimuth
    )
    assert_allclose(result, expected[0])


def test_klucher_series(irrad_data, ephem_data):
    result = irradiance.klucher(40, 180, irrad_data['dhi'], irrad_data['ghi'],
                                ephem_data['apparent_zenith'],
                                ephem_data['azimuth'])
    assert_allclose(result, [0, 37.446276, 109.209347, 56.965916], atol=1e-4)
    # expect same result for np.array and pd.Series
    expected = irradiance.klucher(
        40, 180, irrad_data['dhi'].values, irrad_data['ghi'].values,
        ephem_data['apparent_zenith'].values, ephem_data['azimuth'].values
    )
    assert_allclose(result, expected, atol=1e-4)


def test_haydavies(irrad_data, ephem_data, dni_et):
    result = irradiance.haydavies(40, 180, irrad_data['dhi'], irrad_data['dni'],
                         dni_et,
                         ephem_data['apparent_zenith'],
                         ephem_data['azimuth'])
    assert_allclose(result, [0, 14.967008, 102.994862, 33.190865], atol=1e-4)


def test_reindl(irrad_data, ephem_data, dni_et):
    result = irradiance.reindl(40, 180, irrad_data['dhi'], irrad_data['dni'],
                      irrad_data['ghi'], dni_et,
                      ephem_data['apparent_zenith'],
                      ephem_data['azimuth'])
    assert_allclose(result, [np.nan, 15.730664, 104.131724, 34.166258], atol=1e-4)


def test_king(irrad_data, ephem_data):
    result = irradiance.king(40, irrad_data['dhi'], irrad_data['ghi'],
                    ephem_data['apparent_zenith'])
    assert_allclose(result, [0, 44.629352, 115.182626, 79.719855], atol=1e-4)


def test_perez(irrad_data, ephem_data, dni_et, relative_airmass):
    dni = irrad_data['dni'].copy()
    dni.iloc[2] = np.nan
    out = irradiance.perez(40, 180, irrad_data['dhi'], dni,
                     dni_et, ephem_data['apparent_zenith'],
                     ephem_data['azimuth'], relative_airmass)
    expected = pd.Series(np.array(
        [   0.        ,   31.46046871,  np.nan,   45.45539877]),
        index=irrad_data.index)
    assert_series_equal(out, expected, check_less_precise=2)


def test_perez_components(irrad_data, ephem_data, dni_et, relative_airmass):
    dni = irrad_data['dni'].copy()
    dni.iloc[2] = np.nan
    out, df_components = irradiance.perez(40, 180, irrad_data['dhi'], dni,
                     dni_et, ephem_data['apparent_zenith'],
                     ephem_data['azimuth'], relative_airmass,
                     return_components=True)
    expected = pd.Series(np.array(
        [   0.        ,   31.46046871,  np.nan,   45.45539877]),
        index=irrad_data.index)
    expected_components = pd.DataFrame(
        np.array([[  0.        ,  26.84138589,          np.nan,  31.72696071],
                 [ 0.        ,  0.        ,         np.nan,  4.47966439],
                 [ 0.        ,  4.62212181,         np.nan,  9.25316454]]).T,
        columns=['isotropic', 'circumsolar', 'horizon'],
        index=irrad_data.index
    )
    if pandas_0_22():
        expected_for_sum = expected.copy()
        expected_for_sum.iloc[2] = 0
    else:
        expected_for_sum = expected
    sum_components = df_components.sum(axis=1)

    assert_series_equal(out, expected, check_less_precise=2)
    assert_frame_equal(df_components, expected_components)
    assert_series_equal(sum_components, expected_for_sum, check_less_precise=2)


@needs_numpy_1_10
def test_perez_arrays(irrad_data, ephem_data, dni_et, relative_airmass):
    dni = irrad_data['dni'].copy()
    dni.iloc[2] = np.nan
    out = irradiance.perez(40, 180, irrad_data['dhi'].values, dni.values,
                     dni_et, ephem_data['apparent_zenith'].values,
                     ephem_data['azimuth'].values, relative_airmass.values)
    expected = np.array(
        [   0.        ,   31.46046871,  np.nan,   45.45539877])
    assert_allclose(out, expected, atol=1e-2)


def test_liujordan():
    expected = pd.DataFrame(np.
        array([[863.859736967, 653.123094076, 220.65905025]]),
        columns=['ghi', 'dni', 'dhi'],
        index=[0])
    out = irradiance.liujordan(
        pd.Series([10]), pd.Series([0.5]), pd.Series([1.1]), dni_extra=1400)
    assert_frame_equal(out, expected)


def test_get_total_irradiance(irrad_data, ephem_data, dni_et, relative_airmass):
    models = ['isotropic', 'klucher',
              'haydavies', 'reindl', 'king', 'perez']

    for model in models:
        total = irradiance.get_total_irradiance(
            32, 180,
            ephem_data['apparent_zenith'], ephem_data['azimuth'],
            dni=irrad_data['dni'], ghi=irrad_data['ghi'],
            dhi=irrad_data['dhi'],
            dni_extra=dni_et, airmass=relative_airmass,
            model=model,
            surface_type='urban')

        assert total.columns.tolist() == ['poa_global', 'poa_direct',
                                          'poa_diffuse', 'poa_sky_diffuse',
                                          'poa_ground_diffuse']


@pytest.mark.parametrize('model', ['isotropic', 'klucher',
                                   'haydavies', 'reindl', 'king', 'perez'])
def test_get_total_irradiance_scalars(model):
    total = irradiance.get_total_irradiance(
        32, 180,
        10, 180,
        dni=1000, ghi=1100,
        dhi=100,
        dni_extra=1400, airmass=1,
        model=model,
        surface_type='urban')

    assert list(total.keys()) == ['poa_global', 'poa_direct',
                                  'poa_diffuse', 'poa_sky_diffuse',
                                  'poa_ground_diffuse']
    # test that none of the values are nan
    assert np.isnan(np.array(list(total.values()))).sum() == 0


def test_poa_components(irrad_data, ephem_data, dni_et, relative_airmass):
    aoi = irradiance.aoi(40, 180, ephem_data['apparent_zenith'],
                         ephem_data['azimuth'])
    gr_sand = irradiance.get_ground_diffuse(40, irrad_data['ghi'],
                                            surface_type='sand')
    diff_perez = irradiance.perez(
        40, 180, irrad_data['dhi'], irrad_data['dni'], dni_et,
        ephem_data['apparent_zenith'], ephem_data['azimuth'], relative_airmass)
    out = irradiance.poa_components(
        aoi, irrad_data['dni'], diff_perez, gr_sand)
    expected = pd.DataFrame(np.array(
        [[  0.        ,  -0.        ,   0.        ,   0.        ,
            0.        ],
         [ 35.19456561,   0.        ,  35.19456561,  31.4635077 ,
            3.73105791],
         [956.18253696, 798.31939281, 157.86314414, 109.08433162,
           48.77881252],
         [ 90.99624896,  33.50143401,  57.49481495,  45.45978964,
           12.03502531]]),
        columns=['poa_global', 'poa_direct', 'poa_diffuse', 'poa_sky_diffuse',
                 'poa_ground_diffuse'],
        index=irrad_data.index)
    assert_frame_equal(out, expected)


def test_disc_keys(irrad_data, ephem_data):
    disc_data = irradiance.disc(irrad_data['ghi'], ephem_data['zenith'],
                                ephem_data.index)
    assert 'dni' in disc_data.columns
    assert 'kt' in disc_data.columns
    assert 'airmass' in disc_data.columns


def test_disc_value():
    times = pd.DatetimeIndex(['2014-06-24T12-0700','2014-06-24T18-0700'])
    ghi = pd.Series([1038.62, 254.53], index=times)
    zenith = pd.Series([10.567, 72.469], index=times)
    pressure = 93193.
    disc_data = irradiance.disc(ghi, zenith, times, pressure=pressure)
    assert_almost_equal(disc_data['dni'].values,
                        np.array([830.46, 676.09]), 1)


def test_dirint_value():
    times = pd.DatetimeIndex(['2014-06-24T12-0700','2014-06-24T18-0700'])
    ghi = pd.Series([1038.62, 254.53], index=times)
    zenith = pd.Series([10.567, 72.469], index=times)
    pressure = 93193.
    dirint_data = irradiance.dirint(ghi, zenith, times, pressure=pressure)
    assert_almost_equal(dirint_data.values,
                        np.array([ 888. ,  683.7]), 1)


def test_dirint_nans():
    times = pd.DatetimeIndex(start='2014-06-24T12-0700', periods=5, freq='6H')
    ghi = pd.Series([np.nan, 1038.62, 1038.62, 1038.62, 1038.62], index=times)
    zenith = pd.Series([10.567, np.nan, 10.567, 10.567, 10.567,], index=times)
    pressure = pd.Series([93193., 93193., np.nan, 93193., 93193.], index=times)
    temp_dew = pd.Series([10, 10, 10, np.nan, 10], index=times)
    dirint_data = irradiance.dirint(ghi, zenith, times, pressure=pressure,
                                    temp_dew=temp_dew)
    assert_almost_equal(dirint_data.values,
                        np.array([np.nan, np.nan, np.nan, np.nan, 893.1]), 1)


def test_dirint_tdew():
    times = pd.DatetimeIndex(['2014-06-24T12-0700','2014-06-24T18-0700'])
    ghi = pd.Series([1038.62, 254.53], index=times)
    zenith = pd.Series([10.567, 72.469], index=times)
    pressure = 93193.
    dirint_data = irradiance.dirint(ghi, zenith, times, pressure=pressure,
                                    temp_dew=10)
    assert_almost_equal(dirint_data.values,
                        np.array([892.9,  636.5]), 1)


def test_dirint_no_delta_kt():
    times = pd.DatetimeIndex(['2014-06-24T12-0700','2014-06-24T18-0700'])
    ghi = pd.Series([1038.62, 254.53], index=times)
    zenith = pd.Series([10.567, 72.469], index=times)
    pressure = 93193.
    dirint_data = irradiance.dirint(ghi, zenith, times, pressure=pressure,
                                    use_delta_kt_prime=False)
    assert_almost_equal(dirint_data.values,
                        np.array([861.9,  670.4]), 1)


def test_dirint_coeffs():
    coeffs = irradiance._get_dirint_coeffs()
    assert coeffs[0,0,0,0] == 0.385230
    assert coeffs[0,1,2,1] == 0.229970
    assert coeffs[3,2,6,3] == 1.032260


def test_erbs():
    ghi = pd.Series([0, 50, 1000, 1000])
    zenith = pd.Series([120, 85, 10, 10])
    doy = pd.Series([1, 1, 1, 180])
    expected = pd.DataFrame(np.
        array([[ -0.00000000e+00,   0.00000000e+00,  -0.00000000e+00],
               [  9.67127061e+01,   4.15709323e+01,   4.05715990e-01],
               [  7.94187742e+02,   2.17877755e+02,   7.18119416e-01],
               [  8.42358014e+02,   1.70439297e+02,   7.68919470e-01]]),
        columns=['dni', 'dhi', 'kt'])

    out = irradiance.erbs(ghi, zenith, doy)

    assert_frame_equal(np.round(out, 0), np.round(expected, 0))


def test_erbs_all_scalar():
    ghi = 1000
    zenith = 10
    doy = 180

    expected = OrderedDict()
    expected['dni'] = 8.42358014e+02
    expected['dhi'] = 1.70439297e+02
    expected['kt'] = 7.68919470e-01

    out = irradiance.erbs(ghi, zenith, doy)

    for k, v in out.items():
        assert_allclose(v, expected[k], 5)


@needs_numpy_1_10
def test_dirindex(times):
    ghi = pd.Series([0, 0, 1038.62, 254.53], index=times)
    ghi_clearsky = pd.Series(
        np.array([0., 79.73860422, 1042.48031487, 257.20751138]),
        index=times
    )
    dni_clearsky = pd.Series(
        np.array([0., 316.1949056, 939.95469881, 646.22886049]),
        index=times
    )
    zenith = pd.Series(
        np.array([124.0390863, 82.85457044, 10.56413562, 72.41687122]),
        index=times
    )
    pressure = 93193.
    tdew = 10.
    out = irradiance.dirindex(ghi, ghi_clearsky, dni_clearsky,
                              zenith, times, pressure=pressure,
                              temp_dew=tdew)
    dirint_close_values = irradiance.dirint(ghi, zenith, times,
                                            pressure=pressure,
                                            use_delta_kt_prime=True,
                                            temp_dew=tdew).values
    expected_out = np.array([np.nan, 0., 748.31562753, 630.72592644])

    tolerance = 1e-8
    assert np.allclose(out, expected_out, rtol=tolerance, atol=0,
                       equal_nan=True)
    tol_dirint = 0.2
    assert np.allclose(out.values, dirint_close_values, rtol=tol_dirint, atol=0,
                       equal_nan=True)


def test_dni():
    ghi = pd.Series([90, 100, 100, 100, 100])
    dhi = pd.Series([100, 90, 50, 50, 50])
    zenith = pd.Series([80, 100, 85, 70, 85])
    clearsky_dni = pd.Series([50, 50, 200, 50, 300])

    dni = irradiance.dni(ghi, dhi, zenith,
                         clearsky_dni=clearsky_dni, clearsky_tolerance=2)
    assert_series_equal(dni,
                        pd.Series([float('nan'), float('nan'), 400,
                                   146.190220008, 573.685662283]))

    dni = irradiance.dni(ghi, dhi, zenith)
    assert_series_equal(dni,
                        pd.Series([float('nan'), float('nan'), 573.685662283,
                                   146.190220008, 573.685662283]))


@pytest.mark.parametrize(
    'surface_tilt,surface_azimuth,solar_zenith,' +
    'solar_azimuth,aoi_expected,aoi_proj_expected',
    [(0, 0, 0, 0, 0, 1),
     (30, 180, 30, 180, 0, 1),
     (30, 180, 150, 0, 180, -1),
     (90, 0, 30, 60, 75.5224878, 0.25),
     (90, 0, 30, 170, 119.4987042, -0.4924038)])
def test_aoi_and_aoi_projection(surface_tilt, surface_azimuth, solar_zenith,
                                solar_azimuth, aoi_expected,
                                aoi_proj_expected):
    aoi = irradiance.aoi(surface_tilt, surface_azimuth, solar_zenith,
                         solar_azimuth)
    assert_allclose(aoi, aoi_expected, atol=1e-6)

    aoi_projection = irradiance.aoi_projection(
        surface_tilt, surface_azimuth, solar_zenith, solar_azimuth)
    assert_allclose(aoi_projection, aoi_proj_expected, atol=1e-6)
