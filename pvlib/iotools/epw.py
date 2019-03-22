"""
Import functions for EPW data files.
"""

import datetime
import io
import re

try:
    # python 2 compatibility
    from urllib2 import urlopen, Request
except ImportError:
    from urllib.request import urlopen, Request

import dateutil
import pandas as pd


def read_epw(filename=None, coerce_year=None):
    '''
    Read an EPW file in to a pandas dataframe.
    
    Note that values contained in the metadata dictionary are unchanged
    from the EPW file.
    
    EPW files are commonly used by building simulation professionals 
    and are widely available on the web. For example via: 
    https://energyplus.net/weather , http://climate.onebuilding.org or 
    http://www.ladybug.tools/epwmap/
    
    
    Parameters
    ----------
    filename : String
        Can be a relative file path, absolute file path, or url.

    coerce_year : None or int, default None
        If supplied, the year of the data will be set to this value. This can
        be a useful feature because EPW data is composed of data from
        different years.
        Warning: EPW files always have 365*24 = 8760 data rows; 
        be careful with the use of leap years.
        
    
    Returns
    -------
    Tuple of the form (data, metadata).

    data : DataFrame
        A pandas dataframe with the columns described in the table
        below. For more detailed descriptions of each component, please
        consult the EnergyPlus Auxiliary Programs documentation 
        available at: https://energyplus.net/documentation.

    metadata : dict
        The site metadata available in the file.

    Notes
    -----

    The returned structures have the following fields.
        
    ===============   ======  ===================
    key               format  description
    ===============   ======  ===================
    loc               String  default identifier, not used
    city              String  site loccation
    state-prov        String  state, province or region (if available)
    country           String  site country code
    data_type         String  type of original data source
    WMO_code          String  WMO identifier
    latitude          Float   site latitude
    longitude         Float   site longitude
    TZ                Float   UTC offset
    altitude          Float   site elevation
    ===============   ======  ===================
    
    
    
    =============================       ======================================================================================================================================================
    EPWData field                       description
    =============================       ======================================================================================================================================================
    index                               A pandas datetime index. NOTE, the index is currently timezone unaware, and times are set to local standard time (daylight savings is not included)
    year
    month
    day
    hour
    minute
    data_source_unct                    Data source and uncertainty flags. See [1], chapter 2.13
    temp_air                            Dry bulb temperature at the time indicated, deg C
    temp_dew                            Dew-point temperature at the time indicated, deg C
    relative_humidity                   Relatitudeive humidity at the time indicated, percent
    atmospheric_pressure                Station pressure at the time indicated, Pa
    etr                                 Extraterrestrial horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    etrn                                Extraterrestrial normal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    ghi_infrared                        Horizontal infrared radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    ghi                                 Direct and diffuse horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    dni                                 Amount of direct normal radiation (modeled) recv'd during 60 mintues prior to timestamp, Wh/m^2
    dhi                                 Amount of diffuse horizontal radiation recv'd during 60 minutes prior to timestamp, Wh/m^2
    global_hor_illum                    Avg. total horizontal illuminance recv'd during the 60 minutes prior to timestamp, lx
    direct_normal_illum                 Avg. direct normal illuminance recv'd during the 60 minutes prior to timestamp, lx
    diffuse_horizontal_illum            Avg. horizontal diffuse illuminance recv'd during the 60 minutes prior to timestamp, lx
    zenith_luminance                    Avg. luminance at the sky's zenith during the 60 minutes prior to timestamp, cd/m^2
    wind_direction                      Wind direction at time indicated, degrees from north (360 = north; 0 = undefined,calm)
    wind_speed                          Wind speed at the time indicated, meter/second
    total_sky_cover                     Amount of sky dome covered by clouds or obscuring phenonema at time stamp, tenths of sky
    opaque_sky_cover                    Amount of sky dome covered by clouds or obscuring phenonema that prevent observing the sky at time stamp, tenths of sky
    visibility                          Horizontal visibility at the time indicated, km
    ceiling_height                      Height of cloud base above local terrain (7777=unlimited), meter
    present_weather_observation         Indicator for remaining fields: If 0, then the observed weather codes are taken from the following field. If 9, then missing weather is assumed. Since the primary use of these fields (Present Weather Observation and Present Weather Codes) is for rain/wet surfaces, a missing observation field or a missing weather code implies no rain.
    present_weather_codes               Present weather code, see [1], chapter 2.9.1.28
    precipitable_water                  Total precipitable water contained in a column of unit cross section from earth to top of atmosphere, cm
    aerosol_optical_depth               The broadband aerosol optical depth per unit of air mass due to extinction by aerosol component of atmosphere, unitless
    snow_depth                          Snow depth in centimeters on the day indicated, (999 = missing data)
    days_since_last_snowfall            Number of days since last snowfall (maximum value of 88, where 88 = 88 or greater days; 99 = missing data)
    albedo                              The ratio of reflected solar irradiance to global horizontal irradiance, unitless
    liquid_precipitation_depth          The amount of liquid precipitation observed at indicated time for the period indicated in the liquid precipitation quantity field, millimeter
    liquid_precipitation_quantity       The period of accumulation for the liquid precipitation depth field, hour
    =============================       ======================================================================================================================================================

    References
    ----------

    [1] EnergyPlus documentation, Auxiliary Programs
    https://energyplus.net/documentation.
    '''
    
    if filename.startswith('http'):
        # Attempts to download online EPW file
        # See comments above for possible online sources
        request = Request(filename, headers={'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 '
            'Safari/537.36')})
        response = urlopen(request)
        csvdata = io.StringIO(response.read().decode(errors='ignore'))
    else:
        # Assume it's accessible via the file system
        csvdata = open(filename, 'r')
    
    # Read line with metadata
    firstline = csvdata.readline()

    head = ['loc','city', 'state-prov', 'country', 'data_type','WMO_code', 
            'latitude', 'longitude', 'TZ','altitude']
    meta = dict(zip(head, firstline.rstrip('\n').split(",")))

    meta['altitude'] = float(meta['altitude'])
    meta['latitude'] = float(meta['latitude'])
    meta['longitude'] = float(meta['longitude'])
    meta['TZ'] = float(meta['TZ'])

    colnames = ['year', 'month', 'day', 'hour', 'minute', 'data_source_unct', 
                'temp_air', 'temp_dew', 'relative_humidity', 
                'atmospheric_pressure', 'etr', 'etrn', 'ghi_infrared', 'ghi', 
                'dni', 'dhi', 'global_hor_illum', 'direct_normal_illum', 
                'diffuse_horizontal_illum', 'zenith_luminance', 
                'wind_direction', 'wind_speed', 'total_sky_cover', 
                'opaque_sky_cover', 'visibility', 'ceiling_height', 
                'present_weather_observation', 'present_weather_codes',
                'precipitable_water', 'aerosol_optical_depth', 'snow_depth', 
                'days_since_last_snowfall', 'albedo', 
                'liquid_precipitation_depth', 'liquid_precipitation_quantity']
   
    # We only have to skip 6 rows instead of 7 because we have already used 
    # the realine call above.
    data = pd.read_csv(csvdata, skiprows=6, header=0, names=colnames)
    
    # Change to single year if requested
    if coerce_year is not None:
        data["year"] = coerce_year
        data['year'].iloc[-1] = coerce_year - 1

    # Update index with correct date information     
    data = data.set_index(pd.to_datetime(data[['year', 'month', 'day', 
                                               'hour']]))
     
    # Localize time series
    data = data.tz_localize(int(meta['TZ'] * 3600))

    return data, meta
