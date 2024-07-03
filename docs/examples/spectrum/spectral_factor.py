"""
Spectral Mismatch Estimation
============================
Comparison of spectral factor calculation methods used to estimate the spectral
mismatch factor, :math:`M`, from atmospheric variable inputs.
"""

# %%
# Introduction
# ------------
# This example demonstrates how to use different `spectrum.spectral_factor`
# models in pvlib to calculate the spectral mismatch factor, :math:`M`. While
# :math:`M` for a photovoltaic (PV) module can be calculated exactly using
# spectral irradiance and module spectral response data, these data are not
# always available. pvlib provides several functions to estimate the spectral
# mismatch factor, M, using proxies of the prevailing spectral
# irradiance conditions, such as air mass and clearsky index, which are easily
# derived from common ground-based measurements such as broadband irradiance.
# More information on a range of spectral factor models, as well as the
# variables upon which they are based, can be found in [1]_.
#
# Let's import some data. This example uses a Typical Meteorological Year 3
# (TMY3) file for the location of Greensboro, North Carolina, from the pvlib
# data directory. This TMY3 file is constructed using the median month from
# each year between 1980 and 2003, from which we extract the first week of
# August 2001 to analyse.

# %%
import pathlib
from matplotlib import pyplot as plt
import pandas as pd
import pvlib as pv
from pvlib import location
from pvlib.atmosphere import get_relative_airmass

DATA_DIR = pathlib.Path(pv.__file__).parent / 'data'
meteo, metadata = pv.iotools.read_tmy3(DATA_DIR / '723170TYA.CSV',
                                       coerce_year=2001, map_variables=True)
meteo = meteo.loc['2001-08-01':'2001-08-07']

# %%
# pvlib Spectral Factor Functions
# -----------------------------
# This example demonstrates the application of three pvlib spectral factor
# functions:
#
# - :py:func:`~pvlib.spectrum.spectral_factor_sapm`, which requires only
#   the absolute airmass :math:`AM_a`
# - :py:func:`~pvlib.spectrum.spectral_factor_pvspec`, which requires
#   :math:`AM_a` and the clearsky index :math:`k_c`
# - :py:func:`~pvlib.spectrum.spectral_factor_firstsolar`, which requires
#   :math:`AM_a` and the atmospheric precipitable water content :math:`W`

# %%
# Calculation of inputs
# ---------------------
# Let's calculate the absolute air mass, which is required for all three
# models. We use the Kasten and Young [2]_ model, which requires the apparent
# sun zenith. Note: TMY3 files timestamps indicate the end of the hour, so we
# shift the indices back 30-minutes to calculate solar position at the centre
# of the interval.

# Create a location object
lat, lon = metadata['latitude'], metadata['longitude']
alt = altitude = metadata['altitude']
tz = 'Etc/GMT+5'
loc = location.Location(lat, lon, tz=tz, name='Greensboro, NC')

# Calculate solar position parameters
solpos = loc.get_solarposition(
    meteo.index.shift(freq="-30min"),
    pressure=meteo.pressure*100,  # convert from millibar to Pa
    temperature=meteo.temp_air)
solpos.index = meteo.index  # reset index to end of the hour

amr = get_relative_airmass(solpos.apparent_zenith).dropna()  # relative airmass
ama = amr*(meteo.pressure/1013.25)  # absolute airmass

# Now we calculate the clearsky index, :math:`kc`, by comparing the TMY3 GHI to
# the modelled clearky GHI.

cs = loc.get_clearsky(meteo.index)
kc = pv.irradiance.clearsky_index(meteo.ghi, cs.ghi)

# :math:`W` is provided in the TMY3 file but in other cases can be calculated
# from temperature and relative humidity
# (see :py:func:`pvlib.atmosphere.gueymard94_pw`).

w = meteo.precipitable_water

# %%
# Calculation of Spectral Mismatch
# --------------------------------
# Let's calculate the spectral mismatch factor using the three pvlib functions.
# First, we need to import some model coefficients for the SAPM spectral factor
# function, which, unlike the other two functions, lacks built-in coefficients.

# Import some for a mc-Si module from the SAPM module database.
module = pv.pvsystem.retrieve_sam('SandiaMod')['LG_LG290N1C_G3__2013_']
# Calculate M using the three models for an mc-Si PV module.
m_sapm = pv.spectrum.spectral_factor_sapm(ama, module)
m_pvspec = pv.spectrum.spectral_factor_pvspec(ama, kc, 'multisi')
m_fs = pv.spectrum.spectral_factor_firstsolar(w, ama, 'multisi')
df_results = pd.concat([m_sapm, m_pvspec, m_fs], axis=1)
df_results.columns = ['SAPM', 'PVSPEC', 'FS']
# %%
# Comparison Plots
# ----------------
# We can plot the results to visualise variability between the models. Note
# that this is not an exact comparison since the exact same PV modules has
# not been modelled in each case, only the same module technology.

# Plot M
fig1, ax1 = plt.subplots()
df_results.plot(ax=ax1)

ax1.set_xlabel('Date (m-d H:M)')
ax1.set_ylabel('Mismatch (-)')
ax1.legend()
ax1.set_ylim(0.85, 1.15)
plt.show()

# We can also zoom in one one day, for example August 1st.
fig2, ax1 = plt.subplots()
df_results.loc['2001-08-01'].plot(ax=ax1)
ax1.set_ylim(0.85, 1.15)
plt.show()

# %%
# References
# ----------
# .. [1] Daxini, Rajiv, and Wu, Yupeng (2023). "Review of methods to account
#        for the solar spectral influence on photovoltaic device performance."
#        Energy 286
#        :doi:`10.1016/j.energy.2023.129461`
# .. [2] Kasten, F. and Young, A.T., 1989. Revised optical air mass tables
#        and approximation formula. Applied Optics, 28(22), pp.4735-4738.
#        :doi:`10.1364/AO.28.004735`
