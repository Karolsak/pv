"""
ASV benchmarks for solarposition.py
"""

import pandas as pd
import pvlib
from pvlib import solarposition

from pkg_resources import parse_version


if parse_version(pvlib.__version__) >= parse_version('0.6.1'):
    sun_rise_set_transit_spa = solarposition.sun_rise_set_transit_spa
else:
    sun_rise_set_transit_spa = solarposition.get_sun_rise_set_transit


class SolarPosition:

    def setup(self):
        self.times = pd.date_range(start='20180601', freq='1min',
                                   periods=14400)
        self.times_localized = self.times.tz_localize('Etc/GMT+7')
        self.lat = 35.1
        self.lon = -106.6

    # GH 512
    def time_ephemeris(self):
        solarposition.ephemeris(self.times, self.lat, self.lon)

    # GH 512
    def time_ephemeris_localized(self):
        solarposition.ephemeris(self.times_localized, self.lat, self.lon)

    def time_spa_python(self):
        solarposition.spa_python(self.times_localized[::5], self.lat, self.lon)

    def time_sun_rise_set_transit_spa(self):
        sun_rise_set_transit_spa(self.times_localized[::30],
                                 self.lat, self.lon)

    def time_nrel_earthsun_distance(self):
        solarposition.nrel_earthsun_distance(self.times_localized)
