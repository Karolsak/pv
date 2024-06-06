"""
The ``albedo`` module contains functions for modeling albedo.
"""

from pvlib.tools import sind

WATER_COLOR_COEFFS = {
    'clear_water_no_waves': 0.13,
    'clear_water_ripples_up_to_2.5cm': 0.16,
    'clear_water_ripples_larger_than_2.5cm_occasional_whitecaps': 0.23,
    'clear_water_frequent_whitecaps': 0.3,
    'green_water_ripples_up_to_2.5cm': 0.22,
    'muddy_water_no_waves': 0.19
}

WATER_ROUGHNESS_COEFFS = {
    'clear_water_no_waves': 0.29,
    'clear_water_ripples_up_to_2.5cm': 0.7,
    'clear_water_ripples_larger_than_2.5cm_occasional_whitecaps': 1.23,
    'clear_water_frequent_whitecaps': 2,
    'green_water_ripples_up_to_2.5cm': 0.7,
    'muddy_water_no_waves': 0.29
}


def albedo_water(solar_elevation, color_coeff=None, wave_roughness_coeff=None,
                 surface_condition=None):
    r"""
    Estimation of albedo values for inland water bodies.

    The available surface conditions are for inland water bodies, e.g., lakes
    and ponds. For ocean/open sea, an albedo value of 0.06 is recommended.
    See :py:constant:`pvlib.temperature.ALBEDO`.

    Parameters
    ----------
    solar_elevation : numeric
        Sun elevation angle. [degrees]

    color_coeff : numeric, optional
        Water color coefficient. [-]

    wave_roughness_coeff : numeric, optional
        Water wave roughness coefficient. [-]

    surface_condition : string, optional
        If supplied, overrides ``color_coeff`` and ``wave_roughness_coeff``.
        ``surface_condition`` can be one of the following:
        * 'clear_water_no_waves'
        * 'clear_water_ripples_up_to_2.5cm'
        * 'clear_water_ripples_larger_than_2.5cm_occasional_whitecaps'
        * 'clear_water_frequent_whitecaps'
        * 'green_water_ripples_up_to_2.5cm'
        * 'muddy_water_no_waves'.

    Returns
    -------
    numeric
    Albedo for inland water bodies.

    Notes
    -----
    The equation for calculating the albedo :math:`\rho` is given by

    .. math::
       :label: albedo

        \rho = c^{(r sin(\alpha) + 1)}

    Inputs to the model are the water color coefficient :math:`c` [-], the
    water wave roughness coefficient :math:`r` [-] and the solar elevation
    :math:`\alpha` [degrees]. Parameters are provided in [1]_ , and are coded
    for convenience in :data:`~pvlib.albedo.WATER_COLOR_COEFFS` and
    :data:`~pvlib.albedo.WATER_ROUGHNESS_COEFFS`. The values of these
    coefficients are experimentally determined.

    +---------------------------------------------------------------+-----------------------------+--------------------------------------+
    | Surface and condition                                         | Color coefficient :math:`c` | Wave roughness coefficient :math:`r` |
    +===============================================================+=============================+======================================+
    | Clear water no waves                                          | 0.13                        | 0.29                                 |
    +---------------------------------------------------------------+-----------------------------+--------------------------------------+
    | Clear water ripples up to 2.5 cm                              | 0.16                        | 0.70                                 |
    +---------------------------------------------------------------+-----------------------------+--------------------------------------+
    | Clear water ripples larger than 2.5 cm (occasional whitecaps) | 0.23                        | 1.23                                 |
    +---------------------------------------------------------------+-----------------------------+--------------------------------------+
    | Clear water frequent whitecaps                                | 0.30                        | 2.00                                 |
    +---------------------------------------------------------------+-----------------------------+--------------------------------------+
    | Green water ripples up to 2.5cm                               | 0.22                        | 0.70                                 |
    +---------------------------------------------------------------+-----------------------------+--------------------------------------+
    | Muddy water no waves                                          | 0.19                        | 0.29                                 |
    +---------------------------------------------------------------+-----------------------------+--------------------------------------+

    References
    ----------
    .. [1] Dvoracek M.J., Hannabas B. (1990). "Prediction of albedo for use in
       evapotranspiration and irrigation scheduling." IN: Visions of the Future
       American Society of Agricultural Engineers 04-90: 692-699.
    """  # noqa: E501

    if surface_condition is not None:
        color_coeff = WATER_COLOR_COEFFS[surface_condition]
        wave_roughness_coeff = WATER_ROUGHNESS_COEFFS[surface_condition]

    albedo = color_coeff ** (wave_roughness_coeff * sind(solar_elevation) + 1)
    return albedo
