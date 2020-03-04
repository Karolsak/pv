"""
The ``snow`` module contains functions that model the effect of snow on
solar modules.
"""

import numpy as np
import pandas as pd
from pvlib.tools import sind


def _time_delta_in_hours(times):
    delta = times.to_series().diff()
    return delta.dt.total_seconds().div(3600)


def snow_nrel_fully_covered(snowfall, threshold=1.):
    '''
    Calculates the timesteps when the row's slant height is fully covered
    by snow.

    Parameters
    ----------
    snowfall : Series
        Accumulated snowfall in each time period [cm]

    threshold : float, default 1.0
        Hourly snowfall above which snow coverage is set to the row's slant
        height. [cm/hr]

    Returns
    ----------
    boolean: Series
        True where the snowfall exceeds the defined threshold to fully cover
        the panel.

    Notes
    -----
    Implements the model described in [1]_ with minor improvements in [2]_.

    References
    ----------
    .. [1] Marion, B.; Schaefer, R.; Caine, H.; Sanchez, G. (2013).
       "Measured and modeled photovoltaic system energy losses from snow for
       Colorado and Wisconsin locations." Solar Energy 97; pp.112-121.
    .. [2] Ryberg, D; Freeman, J. "Integration, Validation, and Application
       of a PV Snow Coverage Model in SAM" (2017) NREL Technical Report
    '''
    timestep = _time_delta_in_hours(snowfall.index)
    hourly_snow_rate = snowfall / timestep
    # deal with first hour
    freq = pd.infer_freq(snowfall.index)
    if freq is not None:
        if len(freq)==1:  # only a unit abbreviation
            freq = "1" + freq
        timedelta = pd.Timedelta(freq).total_seconds() / 3600
        hourly_snow_rate.iloc[0] = snowfall[0] / timedelta
    else:  # can't infer frequency from index
        hourly_snow_rate[0] = 0  # replaces NaN
    return hourly_snow_rate > threshold


def snow_nrel(snowfall, poa_irradiance, temp_air, surface_tilt,
              initial_coverage=None, threshold_snowfall=1., m=-80.,
              sliding_coefficient=0.197):
    '''
    Calculates the fraction of the slant height of a row of modules covered by
    snow at every time step.

    Implements the model described in [1]_ with minor improvements in [2]_,
    with the change that the output is in fraction of the row's slant height
    rather than in tenths of the row slant height. As described in [1]_, model
    validation focused on fixed tilt systems.

    Parameters
    ----------
    snowfall : Series
        Accumulated snowfall within each time period. [cm]
    poa_irradiance : Series
        Total in-plane irradiance [W/m^2]
    temp_air : Series
        Ambient air temperature at the surface [C]
    surface_tilt : numeric
        Tilt of module's from horizontal, e.g. surface facing up = 0,
        surface facing horizon = 90. Must be between 0 and 180. [degrees]
    initial_coverage : float, default None
        Fraction of row's slant height that is covered with snow at the
        beginning of the simulation. If None (default) then the initial
        coverage is set to the snowfall in the first time period. [unitless]
    threshold_snowfall : float, default 1.0
        Hourly snowfall above which snow coverage is set to the row's slant
        height. [cm/hr]
    m : float, default 80.
        Coefficient used in [1]_ to determine if snow can slide given
        irradiance and air temperature. [W/(m^2 C)]
    sliding coefficient : float, default 0.197
        Empirical coefficient used in [1]_ to determine how much
        snow slides off in each time period. [unitless]

    Returns
    -------
    snow_coverage : Series
        The fraction of the slant height of a row of modules that is covered
        by snow at each time step.

    References
    ----------
    .. [1] Marion, B.; Schaefer, R.; Caine, H.; Sanchez, G. (2013).
       "Measured and modeled photovoltaic system energy losses from snow for
       Colorado and Wisconsin locations." Solar Energy 97; pp.112-121.
    .. [2] Ryberg, D; Freeman, J. (2017). "Integration, Validation, and
       Application of a PV Snow Coverage Model in SAM" NREL Technical Report
       NREL/TP-6A20-68705
    '''

    # set up output Series
    snow_coverage = pd.Series(index=poa_irradiance.index, data=np.nan)
    if initial_coverage is  None:
        initial_coverage = 0.

    # determine amount that snow can slide in each timestep
    can_slide = temp_air > poa_irradiance / m
    slide_amt = sliding_coefficient * sind(surface_tilt) * \
        _time_delta_in_hours(poa_irradiance.index)

    uncovered = pd.Series(0.0, index=poa_irradiance.index)
    uncovered[can_slide] = slide_amt[can_slide]

    # build list of intervals between snow fall events
    snow_events = snowfall[snow_nrel_fully_covered(snowfall,
                                                   threshold_snowfall)].index
    # define new snow coverage at each event
    new_snow = pd.Series(index=snow_events, data=1.)
    # include start and end times if they are not already snow events
    if snowfall.index[0] not in snow_events:
        new_snow[snowfall.index[0]] = initial_coverage
    if snowfall.index[-1] not in snow_events:
        new_snow[snowfall.index[-1]] = 0.

    windows = list(zip(new_snow.index[:-1], new_snow.index[1:]))
    for (ev, ne) in windows:
        filt = (snow_coverage.index > ev) & (snow_coverage.index <= ne)
        snow_coverage[ev] = new_snow[ev]
        snow_coverage[filt] = new_snow[ev] - uncovered[filt].cumsum()

    # clean up periods where row is completely uncovered
    snow_coverage[snow_coverage < 0] = 0
    snow_coverage = snow_coverage.fillna(value=0.)
    return snow_coverage


def snow_nrel_dc_loss(snow_coverage, num_strings):
    '''
    Calculates the DC loss due to snow coverage. Assumes that if a string is
    partially covered by snow, it produces 0W.

    Parameters
    ----------
    snow_coverage : numeric
        The fraction of row slant height covered by snow at each time step.

    num_strings: int
        The number of parallel-connected strings along a row slant height.

    Returns
    -------
    loss : numeric
        fraction of DC capacity loss due to snow coverage at each time step.
    '''
    return np.ceil(snow_coverage * num_strings) / num_strings
