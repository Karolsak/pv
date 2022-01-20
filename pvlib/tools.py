"""
Collection of functions used in pvlib_python
"""

import datetime as dt
import numpy as np
import pandas as pd
import pytz


def cosd(angle):
    """
    Cosine with angle input in degrees

    Parameters
    ----------
    angle : float or array-like
        Angle in degrees

    Returns
    -------
    result : float or array-like
        Cosine of the angle
    """

    res = np.cos(np.radians(angle))
    return res


def sind(angle):
    """
    Sine with angle input in degrees

    Parameters
    ----------
    angle : float
        Angle in degrees

    Returns
    -------
    result : float
        Sin of the angle
    """

    res = np.sin(np.radians(angle))
    return res


def tand(angle):
    """
    Tan with angle input in degrees

    Parameters
    ----------
    angle : float
        Angle in degrees

    Returns
    -------
    result : float
        Tan of the angle
    """

    res = np.tan(np.radians(angle))
    return res


def asind(number):
    """
    Inverse Sine returning an angle in degrees

    Parameters
    ----------
    number : float
        Input number

    Returns
    -------
    result : float
        arcsin result
    """

    res = np.degrees(np.arcsin(number))
    return res


def localize_to_utc(time, location):
    """
    Converts or localizes a time series to UTC.

    Parameters
    ----------
    time : datetime.datetime, pandas.DatetimeIndex,
           or pandas.Series/DataFrame with a DatetimeIndex.
    location : pvlib.Location object

    Returns
    -------
    pandas object localized to UTC.
    """
    if isinstance(time, dt.datetime):
        if time.tzinfo is None:
            time = pytz.timezone(location.tz).localize(time)
        time_utc = time.astimezone(pytz.utc)
    else:
        try:
            time_utc = time.tz_convert('UTC')
        except TypeError:
            time_utc = time.tz_localize(location.tz).tz_convert('UTC')

    return time_utc


def datetime_to_djd(time):
    """
    Converts a datetime to the Dublin Julian Day

    Parameters
    ----------
    time : datetime.datetime
        time to convert

    Returns
    -------
    float
        fractional days since 12/31/1899+0000
    """

    if time.tzinfo is None:
        time_utc = pytz.utc.localize(time)
    else:
        time_utc = time.astimezone(pytz.utc)

    djd_start = pytz.utc.localize(dt.datetime(1899, 12, 31, 12))
    djd = (time_utc - djd_start).total_seconds() * 1.0/(60 * 60 * 24)

    return djd


def djd_to_datetime(djd, tz='UTC'):
    """
    Converts a Dublin Julian Day float to a datetime.datetime object

    Parameters
    ----------
    djd : float
        fractional days since 12/31/1899+0000
    tz : str, default 'UTC'
        timezone to localize the result to

    Returns
    -------
    datetime.datetime
       The resultant datetime localized to tz
    """

    djd_start = pytz.utc.localize(dt.datetime(1899, 12, 31, 12))

    utc_time = djd_start + dt.timedelta(days=djd)
    return utc_time.astimezone(pytz.timezone(tz))


def _pandas_to_doy(pd_object):
    """
    Finds the day of year for a pandas datetime-like object.

    Useful for delayed evaluation of the dayofyear attribute.

    Parameters
    ----------
    pd_object : DatetimeIndex or Timestamp

    Returns
    -------
    dayofyear
    """
    return pd_object.dayofyear


def _doy_to_datetimeindex(doy, epoch_year=2014):
    """
    Convert a day of year scalar or array to a pd.DatetimeIndex.

    Parameters
    ----------
    doy : numeric
        Contains days of the year

    Returns
    -------
    pd.DatetimeIndex
    """
    doy = np.atleast_1d(doy).astype('float')
    epoch = pd.Timestamp('{}-12-31'.format(epoch_year - 1))
    timestamps = [epoch + dt.timedelta(days=adoy) for adoy in doy]
    return pd.DatetimeIndex(timestamps)


def _datetimelike_scalar_to_doy(time):
    return pd.DatetimeIndex([pd.Timestamp(time)]).dayofyear


def _datetimelike_scalar_to_datetimeindex(time):
    return pd.DatetimeIndex([pd.Timestamp(time)])


def _scalar_out(arg):
    if np.isscalar(arg):
        output = arg
    else:  #
        # works if it's a 1 length array and
        # will throw a ValueError otherwise
        output = np.asarray(arg).item()

    return output


def _array_out(arg):
    if isinstance(arg, pd.Series):
        output = arg.values
    else:
        output = arg

    return output


def _build_kwargs(keys, input_dict):
    """
    Parameters
    ----------
    keys : iterable
        Typically a list of strings.
    input_dict : dict-like
        A dictionary from which to attempt to pull each key.

    Returns
    -------
    kwargs : dict
        A dictionary with only the keys that were in input_dict
    """

    kwargs = {}
    for key in keys:
        try:
            kwargs[key] = input_dict[key]
        except KeyError:
            pass

    return kwargs


def _build_args(keys, input_dict, dict_name):
    """
    Parameters
    ----------
    keys : iterable
        Typically a list of strings.
    input_dict : dict-like
        A dictionary from which to pull each key.
    dict_name : str
        A variable name to include in an error message for missing keys

    Returns
    -------
    kwargs : list
        A list with values corresponding to keys
    """
    try:
        args = [input_dict[key] for key in keys]
    except KeyError as e:
        missing_key = e.args[0]
        msg = (f"Missing required parameter '{missing_key}'. Found "
               f"{input_dict} in {dict_name}.")
        raise KeyError(msg)
    return args


# Created April,2014
# Author: Rob Andrews, Calama Consulting
# Modified: November, 2020 by C. W. Hansen, to add atol and change exit
# criteria
def _golden_sect_DataFrame(params, VL, VH, func, atol=1e-8):
    """
    Vectorized golden section search for finding MPP from a dataframe
    timeseries.

    Parameters
    ----------
    params : dict or Dataframe
        Parameters for the IV curve(s) where MPP will be found. Must contain
        keys: 'r_sh', 'r_s', 'nNsVth', 'i_0', 'i_l'
        of inputs to the function to be optimized.
        Each row should represent an independent optimization.

    VL: float
        Lower bound on voltage for the optimization

    VH: array-like
        Upper bound on voltage for the optimization

    func: function
        Function to be optimized must be in the form f(dict or Dataframe, str)
        where str is the key corresponding to voltage

    Returns
    -------
    func(params, 'V1') : dict or DataFrame
        function evaluated at the optimal point

    df['V1']: array-like or Series
        Dataframe of optimal points

    Notes
    -----
    This function will find the MAXIMUM of a function
    """

    phim1 = (np.sqrt(5) - 1) / 2

    df = params
    df['VH'] = VH
    df['VL'] = VL

    converged = False
    iterations = 0
    iterlimit = np.max(np.trunc(np.log(atol / (VH - VL)) / np.log(phim1))) + 1

    while not converged and (iterations < iterlimit):

        phi = phim1 * (df['VH'] - df['VL'])
        df['V1'] = df['VL'] + phi
        df['V2'] = df['VH'] - phi

        df['f1'] = func(df, 'V1')
        df['f2'] = func(df, 'V2')
        df['SW_Flag'] = df['f1'] > df['f2']

        df['VL'] = df['V2']*df['SW_Flag'] + df['VL']*(~df['SW_Flag'])
        df['VH'] = df['V1']*~df['SW_Flag'] + df['VH']*(df['SW_Flag'])

        err = abs(df['V2'] - df['V1'])

        # works with single value because err is np.float64
        converged = (err < atol).all()
        # err will be less than atol before iterations hit the limit
        # but just to be safe
        iterations += 1

    return func(df, 'V1'), df['V1']
