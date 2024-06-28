import numpy as np
import pandas as pd


def power_mismatch_deline(
    rmad,
    coefficients=(0, 0.142, 0.032),
    fill_factor: float = None,
    fill_factor_reference: float = 0.79,
):
    r"""
    Estimate DC power loss due to irradiance non-uniformity.

    This model is described for bifacial modules in [1]_, where the backside
    irradiance is less uniform due to mounting and site conditions.

    The power loss is estimated by a polynomial model of the Relative Mean
    Absolute Difference (RMAD) of the cell-by-cell total irradiance.

    Use ``fill_factor`` to account for different fill factors between the
    trained model and the module of interest. Specify model's fill factor with
    ``fill_factor_reference``.

    .. versionadded:: 0.11.1

    Parameters
    ----------
    rmad : numeric
        The Relative Mean Absolute Difference of the cell-by-cell total
        irradiance. [Unitless]
        Check out the *Notes* section for the equation to calculate it from the
        bifaciality and the front and back irradiances.

    coefficients : float collection or numpy.polynomial.polynomial.Polynomial, default ``(0, 0.142, 0.032)``
        The polynomial coefficients to use.

        If a :external:class:`numpy.polynomial.polynomial.Polynomial`,
        it is evaluated as is. If not a ``Polynomial``, it must be the
        coefficients of a polynomial in ``rmad``, where the first element is
        the constant term and the last element is the highest order term. A
        :external:class:`~numpy.polynomial.polynomial.Polynomial`
        will be created internally.

    fill_factor : float, optional
        Fill factor at standard test condition (STC) of the module.
        Accounts for different fill factors between the trained model and the
        module under non-uniform irradiance.
        If not provided, the model is used as is.

    fill_factor_reference : float, default 0.79
        Fill factor at STC of the module used to train the model.
        If ``fill_factor`` is provided, this value is used to scale the output
        of the model.

    Returns
    -------
    loss : numeric
        The fractional power loss. [Unitless]
        Output will be a ``pandas.Series`` if ``rmad`` is a ``pandas.Series``.

    Notes
    -----
    The default model implemented is equation (11) [1]_:

    .. math::

       M = 0.142 \Delta + 0.032 \Delta^2 \qquad \text{(11)}

    where :math:`\Delta` is the Relative Mean Absolute Difference of the
    global irradiance, Eq. (4) of [1]_ and [2]_.

    The losses definition is Eq. (1) of [1]_, and it's defined as a loss of the
    output power:

    .. math::

       M = 1 - \frac{P_{Array}}{\sum P_{Cells}} \qquad \text{(1)}

    To account for a module with a fill factor distinct from the one used to
    train the model (``0.79`` by default), the output of the model can be
    modified with Eq. (7):

    .. math::

       M_{FF_1} = M_{FF_0} \frac{FF_1}{FF_0} \qquad \text{(7)}

    where parameter ``fill_factor`` is :math:`FF_1` and
    ``fill_factor_reference`` is :math:`FF_0`.
    In the section *See Also*, you will find two packages that can be used to
    calculate the irradiance at different points of the module.

    .. note::
       The global irradiance RMAD is different from the backside irradiance
       RMAD.

    In case the RMAD of the backside irradiance is known, the global RMAD can
    be calculated as follows, assuming the front irradiance RMAD is
    negligible [2]_:

    .. math::

       RMAD(k \cdot X + c) = RMAD(X) \cdot k \frac{k \bar{X}}{k \bar{X} + c}
       = RMAD(X) \cdot \frac{k}{1 + \frac{c}{k \bar{X}}}

    by similarity with equation (2) of [1]_:

    .. math::

       G_{total\,i} = G_{front\,i} + \phi_{Bifi} G_{rear\,i} \qquad \text{(2)}

    which yields:

    .. math::

       RMAD_{total} = RMAD_{rear} \frac{\phi_{Bifi}}
       {1 + \frac{G_{front}}{\phi_{Bifi} \bar{G}_{rear}}}

    See Also
    --------
    `solarfactors <https://github.com/pvlib/solarfactors/>`_
        Calculate the irradiance at different points of the module.
    `bifacial_radiance <https://github.com/NREL/bifacial_radiance>`_
        Calculate the irradiance at different points of the module.

    References
    ----------
    .. [1] C. Deline, S. Ayala Pelaez, S. MacAlpine, and C. Olalla, 'Estimating
       and parameterizing mismatch power loss in bifacial photovoltaic
       systems', Progress in Photovoltaics: Research and Applications, vol. 28,
       no. 7, pp. 691-703, 2020, :doi:`10.1002/pip.3259`.
    .. [2] “Mean absolute difference,” Wikipedia, Sep. 05, 2023.
       https://en.wikipedia.org/wiki/Mean_absolute_difference#Relative_mean_absolute_difference
       (accessed 2024-04-14).
    """  # noqa: E501
    if isinstance(coefficients, np.polynomial.Polynomial):
        model_polynom = coefficients
    else:  # expect an iterable
        model_polynom = np.polynomial.Polynomial(coef=coefficients)

    if fill_factor:  # Eq. (7), [1]
        # Modify output of a trained model with different fill factor
        model_polynom = model_polynom * fill_factor / fill_factor_reference

    mismatch = model_polynom(rmad)
    if isinstance(rmad, pd.Series):
        mismatch = pd.Series(mismatch, index=rmad.index)
    return mismatch
