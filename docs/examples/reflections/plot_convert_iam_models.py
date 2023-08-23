
"""
IAM Model Conversion
====================

"""

# %%
# Introductory text blurb (TODO)

import numpy as np
from random import uniform
import matplotlib.pyplot as plt

from pvlib.tools import cosd
from pvlib.iam import (ashrae, martin_ruiz, physical, convert, fit)

# %%
# Converting from one model to another
# ------------------------------------
#
# Here we'll show how to convert from the Martin-Ruiz model to both the
# physical and ASHRAE models.

# compute martin_ruiz iam for given parameter
aoi = np.linspace(0, 90, 100)
martin_ruiz_params = {'a_r': 0.16}
martin_ruiz_iam = martin_ruiz(aoi, **martin_ruiz_params)

# get parameters for physical model, compute physical iam
physical_params = convert('martin_ruiz', martin_ruiz_params, 'physical')
physical_iam = physical(aoi, **physical_params)

# get parameters for ashrae model, compute ashrae iam
ashrae_params = convert('martin_ruiz', martin_ruiz_params, 'ashrae')
ashrae_iam = ashrae(aoi, **ashrae_params)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), sharey=True)

# plot aoi vs iam curves
ax1.plot(aoi, martin_ruiz_iam, label='Martin-Ruiz')
ax1.plot(aoi, physical_iam, label='physical')
ax1.set_xlabel('AOI (degrees)')
ax1.set_title('Martin-Ruiz to physical')
ax1.legend()

ax2.plot(aoi, martin_ruiz_iam, label='Martin-Ruiz')
ax2.plot(aoi, ashrae_iam, label='ASHRAE')
ax2.set_xlabel('AOI (degrees)')
ax2.set_title('Martin-Ruiz to ASHRAE')
ax2.legend()

ax1.set_ylabel('IAM')
plt.show()


# %%
# Fitting measured data to a model
# --------------------------------
#
# Here, we'll show how to fit measured data to a model. In this case,
# we'll use perturbed output from the Martin-Ruiz model to mimic
# measured data and then we'll fit this to the physical model.

# create perturbed iam data
aoi = np.linspace(0, 90, 100)
params = {'a_r': 0.16}
iam = martin_ruiz(aoi, **params)
data = iam * np.array([uniform(0.98, 1.02) for _ in range(len(iam))])

# get parameters for physical model that fits this data
physical_params = fit(aoi, data, 'physical')

# compute physical iam
physical_iam = physical(aoi, **physical_params)

# plot aoi vs iam curve
plt.scatter(aoi, data, c='darkorange', label='Perturbed data')
plt.plot(aoi, physical_iam, label='physical')
plt.xlabel('AOI (degrees)')
plt.ylabel('IAM')
plt.title('Fitting data to physical model')
plt.legend()
plt.show()


# %%
# The weight function
# -------------------
# Both :py:func:`pvlib.iam.convert` and :py:func:`pvlib.iam.fit` use
# a weight function when computing residuals between the original (source or
# measured) model and the target model. The default option for this weight
# function is $1 - \sin(x)$. The reasons for this choice of default are given
# in TODO.
#
# We can also choose to pass in a custom weight function, instead.
#
# ### Options for the weight function
#
# In some cases, the choice of weight function has a minimal effect on the
# behavior of the returned target model. This is especially true when there is
# a choice of parameters for the target model that matches the source model
# very well.

# However, in cases where this fit is not as strong, our choice of weight
# function can have a large impact on what parameters are returned for the
# target function. What weight function we choose in these cases will depend on
# how we intend to use the target model.
#
# Here we'll show examples of both of these cases, starting with an example
# where the choice of weight function does not have much impact. In doing
# so, we'll show how to pass in a custom weight function of our choice.

# compute martin_ruiz iam for given parameter
aoi = np.linspace(0, 90, 100)
martin_ruiz_params = {'a_r': 0.16}
martin_ruiz_iam = martin_ruiz(aoi, **martin_ruiz_params)

# get parameters for physical models ...

# ... using default weight function
physical_params_default = convert('martin_ruiz', martin_ruiz_params,
                                  'physical')
physical_iam_default = physical(aoi, **physical_params_default)

# ... using custom weight function
options = {'weight_function': lambda aoi: cosd(aoi)}

physical_params_custom = convert('martin_ruiz', martin_ruiz_params, 'physical',
                                 options=options)
physical_iam_custom = physical(aoi, **physical_params_custom)

# plot aoi vs iam curve
plt.plot(aoi, martin_ruiz_iam, label='Martin-Ruiz')
plt.plot(aoi, physical_iam_default, label='Default weight function')
plt.plot(aoi, physical_iam_custom, label='Custom weight function')
plt.xlabel('AOI (degrees)')
plt.ylabel('IAM')
plt.title('Martin-Ruiz to physical')
plt.legend()
plt.show()

# %%
# For this choice of source and target models, the weight function has little
# to no effect on the target model's outputted parameters. In this case, it
# is reasonable to use the default weight function with its default arguments.
#
# Now we'll look at an example where the weight function does affect the
# output.

# get parameters for ashrae models ...

# ... using default weight function
ashrae_params_default = convert('martin_ruiz', martin_ruiz_params, 'ashrae')
ashrae_iam_default = ashrae(aoi, **ashrae_params_default)

# ... using custom weight function
options = {'weight_function': lambda aoi: cosd(aoi)}

ashrae_params_custom = convert('martin_ruiz', martin_ruiz_params, 'ashrae',
                               options=options)
ashrae_iam_custom = ashrae(aoi, **ashrae_params_custom)

# plot aoi vs iam curve
plt.plot(aoi, martin_ruiz_iam, label='Martin-Ruiz')
plt.plot(aoi, ashrae_iam_default, label='Default weight function')
plt.plot(aoi, ashrae_iam_custom, label='Custom weight function')
plt.xlabel('AOI (degrees)')
plt.ylabel('IAM')
plt.title('Martin-Ruiz to ASHRAE')
plt.legend()
plt.show()

# %%
# In this case, each of these outputted target models looks quite different.
# Finding the right weight function and parameters in such cases will require
# knowing where you want the target model to be more accurate, and will likely
# require some experimentation.

