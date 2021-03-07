"""
test iotools for CAMS
"""

import pandas as pd
import numpy as np
import pytest

from pvlib.iotools import cams
from conftest import DATA_DIR, assert_frame_equal


testfile_mcclear_verbose = DATA_DIR / 'cams_mcclear_1min_verbose.csv'
testfile_mcclear_monthly = DATA_DIR / 'cams_mcclear_monthly.csv'
testfile_radiation_verbose = DATA_DIR / 'cams_radiation_1min_verbose.csv'
testfile_radiation_monthly = DATA_DIR / 'cams_radiation_monthly.csv'


index_verbose = pd.date_range('2020-06-01 12', periods=4, freq='1T', tz='UTC')
index_monthly = pd.date_range('2020-01-01', periods=4, freq='1M')


dtypes_mcclear_verbose = [
    'object', 'float64', 'float64', 'float64', 'float64', 'float64', 'float64',
    'float64', 'float64', 'float64', 'float64', 'float64', 'float64',
    'float64', 'float64', 'float64', 'float64', 'float64', 'int64', 'float64',
    'float64', 'float64', 'float64']

dtypes_mcclear = [
    'object', 'float64', 'float64', 'float64', 'float64', 'float64']

dtypes_radiation_verbose = [
    'object', 'float64', 'float64', 'float64', 'float64', 'float64', 'float64',
    'float64', 'float64', 'float64', 'float64', 'float64', 'float64',
    'float64', 'float64', 'float64', 'float64', 'float64', 'float64',
    'float64', 'float64', 'float64', 'float64', 'int64', 'float64', 'float64',
    'float64', 'float64', 'float64', 'int64', 'int64', 'float64', 'float64',
    'float64', 'float64']

dtypes_radiation = [
    'object', 'float64', 'float64', 'float64', 'float64', 'float64', 'float64',
    'float64', 'float64', 'float64', 'float64']


columns_mcclear_verbose = [
    'Observation period', 'ghi_extra', 'ghi_clear', 'bhi_clear',
    'dhi_clear', 'dni_clear', 'solar_zenith', 'summer/winter split', 'tco3',
    'tcwv', 'AOD BC', 'AOD DU', 'AOD SS', 'AOD OR', 'AOD SU', 'AOD NI',
    'AOD AM', 'alpha', 'Aerosol type', 'fiso', 'fvol', 'fgeo', 'albedo']

columns_mcclear = [
    'Observation period', 'ghi_extra', 'ghi_clear', 'bhi_clear', 'dhi_clear',
    'dni_clear']

columns_radiation_verbose = [
    'Observation period', 'ghi_extra', 'ghi_clear', 'bhi_clear', 'dhi_clear',
    'dni_clear', 'ghi', 'bhi', 'dhi', 'dni', 'Reliability', 'solar_zenith',
    'summer/winter split', 'tco3', 'tcwv', 'AOD BC', 'AOD DU', 'AOD SS',
    'AOD OR', 'AOD SU', 'AOD NI', 'AOD AM', 'alpha', 'Aerosol type', 'fiso',
    'fvol', 'fgeo', 'albedo', 'Cloud optical depth', 'Cloud coverage',
    'Cloud type', 'GHI no corr', 'BHI no corr', 'DHI no corr', 'BNI no corr']

columns_radiation = [
    'Observation period', 'ghi_extra', 'ghi_clear', 'bhi_clear', 'dhi_clear',
    'dni_clear', 'ghi', 'bhi', 'dhi', 'dni', 'Reliability']


values_mcclear_verbose = np.array([
    ['2020-06-01T12:00:00.0/2020-06-01T12:01:00.0', 1084.194, 848.5020,
     753.564, 94.938, 920.28, 35.0308, 0.9723, 341.0221, 17.7962, 0.0065,
     0.0067, 0.0008, 0.0215, 0.0252, 0.0087, 0.0022, np.nan, -1, 0.1668,
     0.0912, 0.0267, 0.1359],
    ['2020-06-01T12:01:00.0/2020-06-01T12:02:00.0', 1083.504, 847.866, 752.904,
     94.962, 920.058, 35.0828, 0.9723, 341.0223, 17.802, 0.0065, 0.0067,
     0.0008, 0.0215, 0.0253, 0.0087, 0.0022, np.nan, -1, 0.1668, 0.0912,
     0.0267, 0.1359],
    ['2020-06-01T12:02:00.0/2020-06-01T12:03:00.0', 1082.802, 847.224, 752.232,
     94.986, 919.836, 35.1357, 0.9723, 341.0224, 17.8079, 0.0065, 0.0067,
     0.0008, 0.0216, 0.0253, 0.0087, 0.0022, np.nan, -1, 0.1668, 0.0912,
     0.0267, 0.1359],
    ['2020-06-01T12:03:00.0/2020-06-01T12:04:00.0', 1082.088, 846.564, 751.554,
     95.01, 919.614, 35.1896, 0.9723, 341.0226, 17.8137, 0.0065, 0.0067,
     0.0008, 0.0217, 0.0253, 0.0087, 0.0022, np.nan, -1, 0.1668, 0.0912,
     0.0267, 0.1359]])

values_mcclear_monthly = np.array([
    ['2020-01-01T00:00:00.0/2020-02-01T00:00:00.0', 67.4314, 39.5494,
     26.1998, 13.3496, 142.1562],
    ['2020-02-01T00:00:00.0/2020-03-01T00:00:00.0', 131.2335, 84.7849,
     58.3855, 26.3994, 202.4865],
    ['2020-03-01T00:00:00.0/2020-04-01T00:00:00.0', 232.3323, 163.176,
     125.1675, 38.0085, 307.5254],
    ['2020-04-01T00:00:00.0/2020-05-01T00:00:00.0', 344.7431, 250.7585,
     197.8757, 52.8829, 387.6707]])

values_radiation_verbose = np.array([
    ['2020-06-01T12:00:00.0/2020-06-01T12:01:00.0', 1084.194, 848.502, 753.564,
     94.938, 920.28, 815.358, 702.342, 113.022, 857.724, 1.0, 35.0308, 0.9723,
     341.0221, 17.7962, 0.0065, 0.0067, 0.0008, 0.0215, 0.0252, 0.0087, 0.0022,
     np.nan, -1, 0.1668, 0.0912, 0.0267, 0.1359, 0.0, 0, 5, 848.502, 753.564,
     94.938, 920.28],
    ['2020-06-01T12:01:00.0/2020-06-01T12:02:00.0', 1083.504, 847.866, 752.904,
     94.962, 920.058, 814.806, 701.73, 113.076, 857.52, 1.0, 35.0828, 0.9723,
     341.0223, 17.802, 0.0065, 0.0067, 0.0008, 0.0215, 0.0253, 0.0087, 0.0022,
     np.nan, -1, 0.1668, 0.0912, 0.0267, 0.1359, 0.0, 0, 5, 847.866, 752.904,
     94.962, 920.058],
    ['2020-06-01T12:02:00.0/2020-06-01T12:03:00.0', 1082.802, 847.224, 752.232,
     94.986, 919.836, 814.182, 701.094, 113.088, 857.298, 1.0, 35.1357, 0.9723,
     341.0224, 17.8079, 0.0065, 0.0067, 0.0008, 0.0216, 0.0253, 0.0087, 0.0022,
     np.nan, -1, 0.1668, 0.0912, 0.0267, 0.1359, 0.0, 0, 5, 847.224, 752.232,
     94.986, 919.836],
    ['2020-06-01T12:03:00.0/2020-06-01T12:04:00.0', 1082.088, 846.564, 751.554,
     95.01, 919.614, 813.612, 700.464, 113.148, 857.094, 1.0, 35.1896, 0.9723,
     341.0226, 17.8137, 0.0065, 0.0067, 0.0008, 0.0217, 0.0253, 0.0087, 0.0022,
     np.nan, -1, 0.1668, 0.0912, 0.0267, 0.1359, 0.0, 0, 5, 846.564, 751.554,
     95.01, 919.614]])

values_radiation_monthly = np.array([
    ['2020-01-01T00:00:00.0/2020-02-01T00:00:00.0', 67.4317, 39.5496,
     26.2, 13.3496, 142.1567, 20.8763, 3.4526, 17.4357, 16.7595, 0.997],
    ['2020-02-01T00:00:00.0/2020-03-01T00:00:00.0', 131.2338, 84.7852,
     58.3858, 26.3994, 202.4871, 47.5197, 13.984, 33.5512, 47.8541, 0.9956],
    ['2020-03-01T00:00:00.0/2020-04-01T00:00:00.0', 232.3325, 163.1762,
     125.1677, 38.0085, 307.5256, 120.1659, 69.6217, 50.5653, 159.576, 0.9949],
    ['2020-04-01T00:00:00.0/2020-05-01T00:00:00.0', 344.7433, 250.7587,
     197.8758, 52.8829, 387.6709, 196.7015, 123.2593, 73.5152, 233.9675,
     0.9897]])


@pytest.mark.parametrize('testfile,index,columns,values,dtypes', [
    (testfile_mcclear_verbose, index_verbose, columns_mcclear_verbose,
     values_mcclear_verbose, dtypes_mcclear_verbose),
    (testfile_mcclear_monthly, index_monthly, columns_mcclear,
     values_mcclear_monthly, dtypes_mcclear),
    (testfile_radiation_verbose, index_verbose, columns_radiation_verbose,
     values_radiation_verbose, dtypes_radiation_verbose),
    (testfile_radiation_monthly, index_monthly, columns_radiation,
     values_radiation_monthly, dtypes_radiation)])
def test_read_cams(testfile, index, columns, values, dtypes):
    expected = pd.DataFrame(values, columns=columns, index=index)
    expected.index.name = 'time'
    expected.index.freq = None
    for (col, _dtype) in zip(expected.columns, dtypes):
        expected[col] = expected[col].astype(_dtype)
    out = cams.read_cams_radiation(testfile, integrated=False,
                                   map_variables=True)
    assert_frame_equal(out, expected)
