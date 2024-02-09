"""Functions to read data from the NOAA SOLRAD network."""

import pandas as pd
import requests
import io

# pvlib conventions
BASE_HEADERS = (
    'year', 'julian_day', 'month', 'day', 'hour', 'minute', 'decimal_time',
    'solar_zenith', 'ghi', 'ghi_flag', 'dni', 'dni_flag', 'dhi', 'dhi_flag',
    'uvb', 'uvb_flag', 'uvb_temp', 'uvb_temp_flag'
)

# following README_SOLRAD.txt variable names for remaining
STD_HEADERS = ('std_dw_psp', 'std_direct', 'std_diffuse', 'std_uvb')

HEADERS = BASE_HEADERS + STD_HEADERS

DPIR_HEADERS = ('dpir', 'dpir_flag', 'dpirc', 'dpirc_flag', 'dpird',
                'dpird_flag')

MADISON_HEADERS = BASE_HEADERS + DPIR_HEADERS + STD_HEADERS + (
    'std_dpir', 'std_dpirc', 'std_dpird')


# as specified in README_SOLRAD.txt file. excludes 1 space between columns
WIDTHS = [4, 3] + 4*[2] + [6, 6] + 5*[7, 1] + 4*[9]
MADISON_WIDTHS = [4, 3] + 4*[2] + [6, 6] + 8*[7, 1] + 7*[9]
# add 1 to make fields contiguous (required by pandas.read_fwf)
WIDTHS = [w + 1 for w in WIDTHS]
MADISON_WIDTHS = [w + 1 for w in MADISON_WIDTHS]
# no space after last column
WIDTHS[-1] -= 1
MADISON_WIDTHS[-1] -= 1

DTYPES = [
    'int64', 'int64', 'int64', 'int64', 'int64', 'int64', 'float64',
    'float64', 'float64', 'int64', 'float64', 'int64', 'float64', 'int64',
    'float64', 'int64', 'float64', 'int64', 'float64', 'float64',
    'float64', 'float64']

MADISON_DTYPES = [
    'int64', 'int64', 'int64', 'int64', 'int64', 'int64', 'float64', 'float64',
    'float64', 'int64', 'float64', 'int64', 'float64', 'int64', 'float64',
    'int64', 'float64', 'int64', 'float64', 'int64', 'float64', 'int64',
    'float64', 'int64', 'float64', 'float64', 'float64', 'float64', 'float64',
    'float64', 'float64']


def read_solrad(filename):
    """
    Read NOAA SOLRAD fixed-width file into pandas dataframe.

    The SOLRAD network is described in [1]_ and [2]_.

    .. versionchanged:: 0.10.4
       The function now returns a tuple where the first element is a dataframe
       and the second element is a dictionary containing metadata. Previous
       versions of this function only returned a dataframe.


    Parameters
    ----------
    filename: str
        filepath or url to read for the fixed-width file.

    Returns
    -------
    data: Dataframe
        A dataframe with DatetimeIndex and all of the variables in the
        file.
    metadata : dict
        Metadata.

    Notes
    -----
    SOLRAD data resolution is described by the README_SOLRAD.txt:
    "Before 1-jan. 2015 the data were reported as 3-min averages;
    on and after 1-Jan. 2015, SOLRAD data are reported as 1-min.
    averages of 1-sec. samples."
    Here, missing data is flagged as NaN, rather than -9999.9.

    References
    ----------
    .. [1] NOAA SOLRAD Network
       `https://www.esrl.noaa.gov/gmd/grad/solrad/index.html
       <https://www.esrl.noaa.gov/gmd/grad/solrad/index.html>`_

    .. [2] B. B. Hicks et. al., (1996), The NOAA Integrated Surface
       Irradiance Study (ISIS). A New Surface Radiation Monitoring
       Program. Bull. Amer. Meteor. Soc., 77, 2857-2864.
       :doi:`10.1175/1520-0477(1996)077<2857:TNISIS>2.0.CO;2`
    """
    if 'msn' in str(filename):
        names = MADISON_HEADERS
        widths = MADISON_WIDTHS
        dtypes = MADISON_DTYPES
    else:
        names = HEADERS
        widths = WIDTHS
        dtypes = DTYPES

    meta = {}

    if str(filename).startswith('ftp') or str(filename).startswith('http'):
        response = requests.get(filename)
        file_buffer = io.StringIO(response.content.decode())
    else:
        file_buffer = open(str(filename), 'r')

    # the first has the name of the  station, and the second gives the
    # station's latitude, longitude, elevation above mean sea level in meters,
    # and the displacement in hours from local standard time.
    meta['station_name'] = file_buffer.readline().strip()

    meta_line = file_buffer.readline().split()
    meta['latitude'] = float(meta_line[0])
    meta['longitude'] = float(meta_line[1])
    meta['elevation'] = float(meta_line[2])
    meta['TZ'] = int(meta_line[3])

    # read in data
    data = pd.read_fwf(file_buffer, header=None, names=names,
                       widths=widths, na_values=-9999.9, dtypes=dtypes)

    # set index
    # columns do not have leading 0s, so must zfill(2) to comply
    # with %m%d%H%M format
    dts = data[['month', 'day', 'hour', 'minute']].astype(str).apply(
        lambda x: x.str.zfill(2))
    dtindex = pd.to_datetime(
        data['year'].astype(str) + dts['month'] + dts['day'] + dts['hour'] +
        dts['minute'], format='%Y%m%d%H%M', utc=True)
    data = data.set_index(dtindex)

    return data, meta
