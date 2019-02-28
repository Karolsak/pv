"""Functions to read data from the NOAA SOLRAD network.
"""

import pandas as pd
import numpy as np


HEADERS = (
    'WBANNO UTC_DATE UTC_TIME LST_DATE LST_TIME CRX_VN LONGITUDE LATITUDE '
    'AIR_TEMPERATURE PRECIPITATION SOLAR_RADIATION SR_FLAG '
    'SURFACE_TEMPERATURE ST_TYPE ST_FLAG RELATIVE_HUMIDITY RH_FLAG '
    'SOIL_MOISTURE_5 SOIL_TEMPERATURE_5 WETNESS WET_FLAG WIND_1_5 WIND_FLAG'
)

VARIABLE_MAP = {
    'LONGITUDE': 'longitude',
    'LATITUDE': 'latitude',
    'AIR_TEMPERATURE': 'temp_air',
    'SOLAR_RADIATION': 'ghi',
    'SR_FLAG': 'ghi_flag',
    'RELATIVE_HUMIDITY': 'relative_humidity',
    'RH_FLAG': 'relative_humidity_flag',
    'WIND_1_5': 'wind_speed',
    'WIND_FLAG': 'wind_speed_flag'
}

# as specified in CRN README.txt file. excludes 1 space between columns
WIDTHS = [5, 8, 4, 8, 4, 6, 7, 7, 7, 7, 6, 1, 7, 1, 1, 5, 1, 7, 7, 5, 1, 6, 1]
# add 1 to make fields contiguous (required by pandas.read_fwf)
WIDTHS = [w + 1 for w in WIDTHS]
# no space after last column
WIDTHS[-1] -= 1

# specify dtypes for potentially problematic values
DTYPES = [
    'int64', 'int64', 'int64', 'int64', 'int64', 'int64', 'float64', 'float64',
    'float64', 'float64', 'float64', 'int64', 'float64', 'O', 'int64',
    'float64', 'int64', 'float64', 'float64', 'int64', 'int64', 'float64',
    'int64'
]


def read_solrad(filename):
    """
    Read NOAA SOLRAD [1]_ [2]_ fixed-width file into pandas dataframe.

    Parameters
    ----------
    filename: str
        filepath or url to read for the fixed-width file.

    Returns
    -------
    data: Dataframe
        A dataframe with DatetimeIndex and all of the variables in the
        file.

    Notes
    -----
    CRN files contain 5 minute averages labeled by the interval ending
    time. Here, missing data is flagged as NaN, rather than the lowest
    possible integer for a field (e.g. -999 or -99). Air temperature in
    deg C. Wind speed in m/s at a height of 1.5 m above ground level.

    Variables corresponding to standard pvlib variables are renamed,
    e.g. `SOLAR_RADIATION` becomes `ghi`. See the
    `pvlib.iotools.crn.VARIABLE_MAP` dict for the complete mapping.

    References
    ----------
    .. [1] NOAA SOLRAD Network
       `https://www.esrl.noaa.gov/gmd/grad/solrad/solradsites.html
       <https://www.esrl.noaa.gov/gmd/grad/solrad/solradsites.html>`_

    .. [2] B. B. Hicks et. al., (1996), The NOAA Integrated Surface
       Irradiance Study (ISIS). A New Surface Radiation Monitoring
       Program. Bull. Amer. Meteor. Soc., 77, 2857-2864.
       :doi:`10.1175/1520-0477(1996)077<2857:TNISIS>2.0.CO;2`
    """

    # read in data
    data = pd.read_fwf(filename, header=None, names=HEADERS.split(' '),
                       widths=WIDTHS)
    # loop here because dtype kwarg not supported in read_fwf until 0.20
    for (col, _dtype) in zip(data.columns, DTYPES):
        data[col] = data[col].astype(_dtype)

    # set index
    # UTC_TIME does not have leading 0s, so must zfill(4) to comply
    # with %H%M format
    dts = data[['UTC_DATE', 'UTC_TIME']].astype(str)
    dtindex = pd.to_datetime(dts['UTC_DATE'] + dts['UTC_TIME'].str.zfill(4),
                             format='%Y%m%d%H%M', utc=True)
    data = data.set_index(dtindex)
    try:
        # to_datetime(utc=True) does not work in older versions of pandas
        data = data.tz_localize('UTC')
    except TypeError:
        pass

    # set nans
    for val in [-99, -999, -9999]:
        data = data.where(data != val, np.nan)

    data = data.rename(columns=VARIABLE_MAP)

    return data
