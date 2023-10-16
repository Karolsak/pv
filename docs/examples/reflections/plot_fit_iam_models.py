
"""
IAM Model Conversion and Fitting
================================

Illustrates how to fit an IAM model to data using pvlib.iam.fit

"""

# %%
# An incidence angle modifier (IAM) model quantifies the fraction of direct
# irradiance is that is reflected away from a module's surface. Three popular
# IAM models are Martin-Ruiz :py:func:`~pvlib.iam.martin_ruiz`, physical
# :py:func:`~pvlib.iam.physical`, and ASHRAE `py:func:~pvlib.iam.ashrae`.
# Each model requires one or more parameters.
#
# Here, we show how to use
# :py:func:`~pvlib.iam.fit` to estimate a model's parameters from data.
#
# Model fitting require a weight function that assigns
# more influence to some AOI values than others. We illustrate how to provide
# a custom weight function to :py:func:`~pvlib.iam.fit`.

import numpy as np
from random import uniform
import matplotlib.pyplot as plt

from pvlib.tools import cosd
from pvlib.iam import (martin_ruiz, physical, fit)


# %%
# Fitting an IAM model to data
# ----------------------------
#
# Here, we'll show how to fit an IAM model to data.
# We'll generate some data by perturbing output from the Martin-Ruiz model to
# mimic measured data and then we'll fit the physical model to the perturbed
# data.

# Create and perturb IAM data.
aoi = np.linspace(0, 90, 100)
params = {'a_r': 0.16}
iam = martin_ruiz(aoi, **params)
data = iam * np.array([uniform(0.98, 1.02) for _ in range(len(iam))])

# Get parameters for the physical model by fitting to the perturbed data.
physical_params = fit(aoi, data, 'physical')

# Compute IAM with the fitted physical model parameters.
physical_iam = physical(aoi, **physical_params)

# Plot IAM vs. AOI
plt.scatter(aoi, data, c='darkorange', label='Data')
plt.plot(aoi, physical_iam, label='physical')
plt.xlabel('AOI (degrees)')
plt.ylabel('IAM')
plt.title('Fitting the physical model to data')
plt.legend()
plt.show()


# %%
# The weight function
# -------------------
# :py:func:`pvlib.iam.fit` uses a weight function when computing residuals
# between the model abd data. The default weight
# function is :math:`1 - \sin(aoi)`. We can instead pass a custom weight
# function to :py:func:`pvlib.iam.fit`.
#

# Define a custom weight function.
def weight_function(aoi):
    return cosd(aoi)


physical_params_custom = fit(aoi, data, 'physical', weight=weight_function)

physical_iam_custom = physical(aoi, **physical_params_custom)

# Plot IAM vs AOI.
plt.plot(aoi, data, label='Data (from Martin-Ruiz model)')
plt.plot(aoi, physical_iam, label='Default weight function')
plt.plot(aoi, physical_iam_custom, label='Custom weight function')
plt.xlabel('AOI (degrees)')
plt.ylabel('IAM')
plt.legend()
plt.show()
