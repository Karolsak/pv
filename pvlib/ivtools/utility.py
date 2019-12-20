"""
The ``pvlib.ivtools.utility.py`` module contains utility functions for fitting
equations to IV curve data.

"""

import numpy as np
import pandas as pd
from collections import OrderedDict


# A small number used to decide when a slope is equivalent to zero
EPS = np.finfo('float').eps**(1/3)


constants = OrderedDict()
constants['E0'] = 1000.0
constants['T0'] = 25.0
constants['k'] = 1.38066e-23
constants['q'] = 1.60218e-19


def numdiff(x, f):
    """
    NUMDIFF computes first and second order derivative using possibly unequally
    spaced data.

    Parameters
    ----------
    x : numeric
        a numpy array of values of x
    f : numeric
        a numpy array of values of the function f for which derivatives are to
        be computed. Must be the same length as x.

    Returns
    -------
    df : numeric
        a numpy array of len(x) containing the first derivative of f at each
        point x except at the first 2 and last 2 points
    df2 : numeric
        a numpy array of len(x) containing the second derivative of f at each
        point x except at the first 2 and last 2 points.

    Description
    -----------
    numdiff computes first and second order derivatives using a 5th order
    formula that accounts for possibly unequally spaced data. Because a 5th
    order centered difference formula is used, numdiff returns NaNs for the
    first 2 and last 2 points in the input vector for x.

    References
    ----------
    [1] PVLib MATLAB
    [2] M. K. Bowen, R. Smith, "Derivative formulae and errors for
        non-uniformly spaced points", Proceedings of the Royal Society A, vol.
        461 pp 1975 - 1997, July 2005. DOI: 10.1098/rpsa.2004.1430
    """

    n = len(f)

    df = np.zeros(n)
    df2 = np.zeros(n)

    # first two points are special
    df[:2] = float("Nan")
    df2[:2] = float("Nan")

    # Last two points are special
    df[-2:] = float("Nan")
    df2[-2:] = float("Nan")

    # Rest of points. Take reference point to be the middle of each group of 5
    # points. Calculate displacements
    ff = np.vstack((f[:-4], f[1:-3], f[2:-2], f[3:-1], f[4:])).T

    a0 = (np.vstack((x[:-4], x[1:-3], x[2:-2], x[3:-1], x[4:])).T
          - np.tile(x[2:-2], [5, 1]).T)

    u1 = np.zeros(a0.shape)
    left = np.zeros(a0.shape)
    u2 = np.zeros(a0.shape)

    u1[:, 0] = (
        a0[:, 1] * a0[:, 2] * a0[:, 3] + a0[:, 1] * a0[:, 2] * a0[:, 4]
        + a0[:, 1] * a0[:, 3] * a0[:, 4] + a0[:, 2] * a0[:, 3] * a0[:, 4])
    u1[:, 1] = (
        a0[:, 0] * a0[:, 2] * a0[:, 3] + a0[:, 0] * a0[:, 2] * a0[:, 4]
        + a0[:, 0] * a0[:, 3] * a0[:, 4] + a0[:, 2] * a0[:, 3] * a0[:, 4])
    u1[:, 2] = (
        a0[:, 0] * a0[:, 1] * a0[:, 3] + a0[:, 0] * a0[:, 1] * a0[:, 4]
        + a0[:, 0] * a0[:, 3] * a0[:, 4] + a0[:, 1] * a0[:, 3] * a0[:, 4])
    u1[:, 3] = (
        a0[:, 0] * a0[:, 1] * a0[:, 2] + a0[:, 0] * a0[:, 1] * a0[:, 4]
        + a0[:, 0] * a0[:, 2] * a0[:, 4] + a0[:, 1] * a0[:, 2] * a0[:, 4])
    u1[:, 4] = (
        a0[:, 0] * a0[:, 1] * a0[:, 2] + a0[:, 0] * a0[:, 1] * a0[:, 3]
        + a0[:, 0] * a0[:, 2] * a0[:, 3] + a0[:, 1] * a0[:, 2] * a0[:, 3])

    left[:, 0] = (a0[:, 0] - a0[:, 1]) * (a0[:, 0] - a0[:, 2]) * \
        (a0[:, 0] - a0[:, 3]) * (a0[:, 0] - a0[:, 4])
    left[:, 1] = (a0[:, 1] - a0[:, 0]) * (a0[:, 1] - a0[:, 2]) * \
        (a0[:, 1] - a0[:, 3]) * (a0[:, 1] - a0[:, 4])
    left[:, 2] = (a0[:, 2] - a0[:, 0]) * (a0[:, 2] - a0[:, 1]) * \
        (a0[:, 2] - a0[:, 3]) * (a0[:, 2] - a0[:, 4])
    left[:, 3] = (a0[:, 3] - a0[:, 0]) * (a0[:, 3] - a0[:, 1]) * \
        (a0[:, 3] - a0[:, 2]) * (a0[:, 3] - a0[:, 4])
    left[:, 4] = (a0[:, 4] - a0[:, 0]) * (a0[:, 4] - a0[:, 1]) * \
        (a0[:, 4] - a0[:, 2]) * (a0[:, 4] - a0[:, 3])

    df[2:-2] = np.sum(-(u1 / left) * ff, axis=1)

    # second derivative
    u2[:, 0] = (
        a0[:, 1] * a0[:, 2] + a0[:, 1] * a0[:, 3] + a0[:, 1] * a0[:, 4]
        + a0[:, 2] * a0[:, 3] + a0[:, 2] * a0[:, 4] + a0[:, 3] * a0[:, 4])
    u2[:, 1] = (
        a0[:, 0] * a0[:, 2] + a0[:, 0] * a0[:, 3] + a0[:, 0] * a0[:, 4]
        + a0[:, 2] * a0[:, 3] + a0[:, 2] * a0[:, 4] + a0[:, 3] * a0[:, 4])
    u2[:, 2] = (
        a0[:, 0] * a0[:, 1] + a0[:, 0] * a0[:, 3] + a0[:, 0] * a0[:, 4]
        + a0[:, 1] * a0[:, 3] + a0[:, 1] * a0[:, 3] + a0[:, 3] * a0[:, 4])
    u2[:, 3] = (
        a0[:, 0] * a0[:, 1] + a0[:, 0] * a0[:, 2] + a0[:, 0] * a0[:, 4]
        + a0[:, 1] * a0[:, 2] + a0[:, 1] * a0[:, 4] + a0[:, 2] * a0[:, 4])
    u2[:, 4] = (
        a0[:, 0] * a0[:, 1] + a0[:, 0] * a0[:, 2] + a0[:, 0] * a0[:, 3]
        + a0[:, 1] * a0[:, 2] + a0[:, 1] * a0[:, 4] + a0[:, 2] * a0[:, 3])

    df2[2:-2] = 2. * np.sum(u2 * ff, axis=1)
    return df, df2


def rectify_iv_curve(voltage, current, voc, isc, decimals=None):
    """
    ``rectify_IV_curve`` ensures that Isc and Voc are included in a IV curve
    and removes duplicate voltage and current points.

    Parameters
    ----------
    voltage : numeric [V]
    current : numeric [A]
    voc : numeric
        open circuit voltage [V]
    isc : numeric
        short circuit current [A]
    decimals : int or None, default None
        number of decimal places to which voltage is rounded to remove
        duplicate values. If None, duplicates are not removed.

    Returns
    -------
    voltage : numeric [V]
    current : numeric [A]

    Raises
    ------
    ValueError if voltage and current are different length

    Description
    -----------
    ``rectify_IV_curve`` ensures that the IV curve lies in the first quadrant
    of the (voltage, current) plane. The returned IV curve:
    * contains no NaNs
    * increases in voltage
    * contains no negative current or voltage values
    * has the first data point as (0, Isc)
    * has the last data point as (Voc, 0)
    * contains no duplicate voltage values. Where voltage values are
      repeated, a single data point is substituted with current equal to
      the average of current at duplicated voltages.
    """

    if len(voltage) != len(current):
        raise ValueError('voltage and current must have the same length')

    # add isc and voc
    v_tmp = np.concatenate((voltage, np.array([0., voc])))
    i_tmp = np.concatenate((current, np.array([isc, 0.])))

    df = pd.DataFrame(data=np.vstack((v_tmp, i_tmp)).T, columns=['v', 'i'])
    # restrict to first quadrant
    df.dropna(inplace=True)
    df = df[(df['v']>=0) & (df['i']>=0) & (df['v']<=voc)]
    # sort pairs on voltage, then current
    df = df.sort_values(by=['v', 'i'], ascending=[True, False])

    # eliminate duplicate voltage points
    if decimals is not None:
        _, inv = np.unique(np.round(df['v'], decimals=decimals),
                           return_inverse=True)
        df.index = inv
        # average current at each common voltage
        df = df.groupby(by=inv).mean()

    tmp = np.array(df).T
    return tmp[0,], tmp[1,]


def schumaker_qspline(x, y):
    """
    schumaker_qspline fits a quadratic spline which preserves monotonicity and
    convexity in the data.

    Parameters
    ----------
    x : numeric
        independent points between which the spline will interpolate.
    y : numeric
        dependent points between which the spline will interpolate.

    Returns
    -------
    t : numpy.ndarray
        an ordered vector of knots, i.e., X values where the spline
        changes coefficients. All values in ``x`` are used as knots.
        The algorithm may insert additional knots between data points in ``x``
        where changes in convexity are indicated by the (numerical)
        derivative. Consequently len(t) >= len(x).
    c : numpy.ndarray
        a Nx3 matrix of coefficients where the kth row defines the quadratic
        interpolant between t_k and t_(k+1), i.e., y = c[i, 0] *
        (x - t_k)^2 + c[i, 1] * (x - t_k) + c[i, 2]
    yhat : numpy.ndarray
        y values corresponding to the knots in t. Contains the original
        data points, y, and also y-values estimated from the spline at the
        inserted knots.
    kflag : numpy.ndarray
        a vector of len(t) of logicals, which are set to true for
        elements of t that are knots inserted by the algorithm.

    Notes
    -----
    Ported from PVLib Matlab [1]_. Algorithm is taken from [2]_, which relies
    on prior work described in [3]_.

    References
    ----------
    [1] PVLib MATLAB
    [2] L. L. Schumaker, "On Shape Preserving Quadratic Spline Interpolation",
        SIAM Journal on Numerical Analysis 20(4), August 1983, pp 854 - 864
    [3] M. H. Lam, "Monotone and Convex Quadratic Spline Interpolation",
        Virginia Journal of Science 41(1), Spring 1990
    """
    # Make sure vectors are 1D arrays
    x = x.flatten()
    y = y.flatten()

    n = x.size
    assert n == y.size

    # compute various values used by the algorithm: differences, length of line
    # segments between data points, and ratios of differences.
    delx = np.diff(x)  # delx[i] = x[i + 1] - x[i]
    dely = np.diff(y)

    delta = dely / delx

    # Calculate first derivative at each x value per [3]

    s = np.zeros_like(x)

    left = np.append(0.0, delta)
    right = np.append(delta, 0.0)

    pdelta = left * right

    u = pdelta > 0

    # [3], Eq. 9 for interior points
    # fix tuning parameters in [2], Eq 9 at chi = .5 and eta = .5
    s[u] = pdelta[u] / (0.5*left[u] + 0.5*right[u])

    # [3], Eq. 7 for left endpoint
    left_end = 2.0 * delta[0] - s[1]
    if delta[0] * left_end > 0:
        s[0] = left_end

    # [3], Eq. 8 for right endpoint
    right_end = 2.0 * delta[-1] - s[-2]
    if delta[-1] * right_end > 0:
        s[-1] = right_end

    # determine knots. Start with initial points x
    # [2], Algorithm 4.1 first 'if' condition of step 5 defines intervals
    # which won't get internal knots
    tests = s[:-1] + s[1:]
    u = np.isclose(tests, 2.0 * delta, atol=EPS)
    # u = true for an interval which will not get an internal knot

    k = n + sum(~u)  # total number of knots = original data + inserted knots

    # set up output arrays
    # knot locations, first n - 1 and very last (n + k) are original data
    xk = np.zeros(k)
    yk = np.zeros(k)  # function values at knot locations
    # logicals that will indicate where additional knots are inserted
    flag = np.zeros(k, dtype=bool)
    a = np.zeros((k, 3))

    # structures needed to compute coefficients, have to be maintained in
    # association with each knot

    tmpx = x[:-1]
    tmpy = y[:-1]
    tmpx2 = x[1:]
    tmps = s[:-1]
    tmps2 = s[1:]
    diffs = np.diff(s)

    # structure to contain information associated with each knot, used to
    # calculate coefficients
    uu = np.zeros((k, 6))

    uu[:(n - 1), :] = np.array([tmpx, tmpx2, tmpy, tmps, tmps2, delta]).T

    # [2], Algorithm 4.1 subpart 1 of Step 5
    # original x values that are left points of intervals without internal
    # knots

    # MATLAB differs from NumPy, boolean indices must be same size as
    # array
    xk[:(n-1)][u] = tmpx[u]
    yk[:(n-1)][u] = tmpy[u]
    # constant term for each polynomial for intervals without knots
    a[:(n-1), 2][u] = tmpy[u]
    a[:(n-1), 1][u] = s[:-1][u]
    a[:(n-1), 0][u] = 0.5 * diffs[u] / delx[u]  # leading coefficients

    # [2], Algorithm 4.1 subpart 2 of Step 5
    # original x values that are left points of intervals with internal knots
    xk[:(n-1)][~u] = tmpx[~u]
    yk[:(n-1)][~u] = tmpy[~u]

    aa = s[:-1] - delta
    b = s[1:] - delta

    sbar = np.zeros(k)
    eta = np.zeros(k)
    # will contain mapping from the left points of intervals containing an
    # added knot to each inverval's internal knot value
    xi = np.zeros(k)

    t0 = aa * b >= 0
    # first 'else' in Algorithm 4.1 Step 5
    v = np.logical_and(~u, t0)  # len(u) == (n - 1) always
    q = np.sum(v)  # number of this type of knot to add

    if q > 0.:
        xk[(n - 1):(n + q - 1)] = .5 * (tmpx[v] + tmpx2[v])  # knot location
        uu[(n - 1):(n + q - 1), :] = np.array([tmpx[v], tmpx2[v], tmpy[v],
                                               tmps[v], tmps2[v], delta[v]]).T
        xi[:(n-1)][v] = xk[(n - 1):(n + q - 1)]

    t1 = np.abs(aa) > np.abs(b)
    w = np.logical_and(~u, ~v)  # second 'else' in Algorithm 4.1 Step 5
    w = np.logical_and(w, t1)
    r = np.sum(w)

    if r > 0.:
        xk[(n + q - 1):(n + q + r - 1)] = tmpx2[w] + aa[w] * delx[w] / diffs[w]
        uu[(n + q - 1):(n + q + r - 1), :] = np.array([tmpx[w], tmpx2[w],
                                                       tmpy[w], tmps[w],
                                                       tmps2[w], delta[w]]).T
        xi[:(n-1)][w] = xk[(n + q - 1):(n + q + r - 1)]

    z = np.logical_and(~u, ~v)  # last 'else' in Algorithm 4.1 Step 5
    z = np.logical_and(z, ~w)
    ss = np.sum(z)

    if ss > 0.:
        xk[(n + q + r - 1):(n + q + r + ss - 1)] = \
            tmpx[z] + b[z] * delx[z] / diffs[z]
        uu[(n + q + r - 1):(n + q + r + ss - 1), :] = \
            np.array([tmpx[z], tmpx2[z], tmpy[z], tmps[z], tmps2[z],
                      delta[z]]).T
        xi[:(n-1)][z] = xk[(n + q + r - 1):(n + q + r + ss - 1)]

    # define polynomial coefficients for intervals with added knots
    ff = ~u
    sbar[:(n-1)][ff] = (
        (2 * uu[:(n-1), 5][ff] - uu[:(n-1), 4][ff])
        + (uu[:(n-1), 4][ff] - uu[:(n-1), 3][ff])
        * (xi[:(n-1)][ff] - uu[:(n-1), 0][ff])
        / (uu[:(n-1), 1][ff] - uu[:(n-1), 0][ff]))
    eta[:(n-1)][ff] = (
        (sbar[:(n-1)][ff] - uu[:(n-1), 3][ff])
        / (xi[:(n-1)][ff] - uu[:(n-1), 0][ff]))

    sbar[(n - 1):(n + q + r + ss - 1)] = \
        (2 * uu[(n - 1):(n + q + r + ss - 1), 5] -
         uu[(n - 1):(n + q + r + ss - 1), 4]) + \
        (uu[(n - 1):(n + q + r + ss - 1), 4] -
         uu[(n - 1):(n + q + r + ss - 1), 3]) * \
        (xk[(n - 1):(n + q + r + ss - 1)] -
         uu[(n - 1):(n + q + r + ss - 1), 0]) / \
        (uu[(n - 1):(n + q + r + ss - 1), 1] -
         uu[(n - 1):(n + q + r + ss - 1), 0])
    eta[(n - 1):(n + q + r + ss - 1)] = \
        (sbar[(n - 1):(n + q + r + ss - 1)] -
         uu[(n - 1):(n + q + r + ss - 1), 3]) / \
        (xk[(n - 1):(n + q + r + ss - 1)] -
         uu[(n - 1):(n + q + r + ss - 1), 0])

    # constant term for polynomial for intervals with internal knots
    a[:(n-1), 2][~u] = uu[:(n-1), 2][~u]
    a[:(n-1), 1][~u] = uu[:(n-1), 3][~u]
    a[:(n-1), 0][~u] = 0.5 * eta[:(n-1)][~u]  # leading coefficient

    a[(n - 1):(n + q + r + ss - 1), 2] = \
        uu[(n - 1):(n + q + r + ss - 1), 2] + \
        uu[(n - 1):(n + q + r + ss - 1), 3] * \
        (xk[(n - 1):(n + q + r + ss - 1)] -
         uu[(n - 1):(n + q + r + ss - 1), 0]) + \
        .5 * eta[(n - 1):(n + q + r + ss - 1)] * \
        (xk[(n - 1):(n + q + r + ss - 1)] -
         uu[(n - 1):(n + q + r + ss - 1), 0]) ** 2.
    a[(n - 1):(n + q + r + ss - 1), 1] = sbar[(n - 1):(n + q + r + ss - 1)]
    a[(n - 1):(n + q + r + ss - 1), 0] = \
        .5 * (uu[(n - 1):(n + q + r + ss - 1), 4] -
              sbar[(n - 1):(n + q + r + ss - 1)]) / \
        (uu[(n - 1):(n + q + r + ss - 1), 1] -
         uu[(n - 1):(n + q + r + ss - 1), 0])

    yk[(n - 1):(n + q + r + ss - 1)] = a[(n - 1):(n + q + r + ss - 1), 2]

    xk[n + q + r + ss - 1] = x[n - 1]
    yk[n + q + r + ss - 1] = y[n - 1]
    flag[(n - 1):(n + q + r + ss - 1)] = True  # these are all inserted knots

    tmp = np.vstack((xk, a.T, yk, flag)).T
    # sort output in terms of increasing x (original plus added knots)
    tmp2 = tmp[tmp[:, 0].argsort(kind='mergesort')]

    t = tmp2[:, 0]
    outn = len(t)
    c = tmp2[0:(outn - 1), 1:4]
    yhat = tmp2[:, 4]
    kflag = tmp2[:, 5]
    return t, c, yhat, kflag
