"""
Numerical Precision
http://docs.sympy.org/latest/modules/evalf.html#accuracy-and-error-handling
"""

import logging
import os
import numpy as np
import pandas as pd
from pvlib import pvsystem

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
TEST_DATA = 'bishop88_numerical_precision.csv'
TEST_PATH = os.path.dirname(os.path.abspath(__file__))
PVLIB_PATH = os.path.dirname(TEST_PATH)
DATA_PATH = os.path.join(PVLIB_PATH, 'data', TEST_DATA)
POA = 888
TCELL = 55
CECMOD = pvsystem.retrieve_sam('cecmod')
# get module from cecmod and apply temp/irrad desoto corrections
SPR_E20_327 = CECMOD.SunPower_SPR_E20_327
ARGS = pvsystem.calcparams_desoto(
    poa_global=POA, temp_cell=TCELL,
    alpha_isc=SPR_E20_327.alpha_sc, module_parameters=SPR_E20_327,
    EgRef=1.121, dEgdT=-0.0002677
)
IL, I0, RS, RSH, NNSVTH = ARGS
IVCURVE_NPTS = 100

try:
    from sympy import symbols, exp as sy_exp
except ImportError as exc:
    LOGGER.exception(exc)
    symbols = NotImplemented
    sy_exp = NotImplemented


def generate_numerical_precicion():
    """
    Generate expected data with infinite numerical precision using SymPy.
    :return: dataframe of expected values
    """
    if symbols is NotImplemented:
        LOGGER.critical("SymPy is required to generate expected data.")
        raise ImportError("could not import sympy")
    il, io, rs, rsh, nnsvt, vd = symbols('il, io, rs, rsh, nnsvt, vd')
    a = sy_exp(vd / nnsvt)
    b = 1.0 / rsh
    i = il - io * (a - 1.0) - vd * b
    v = vd - i * rs
    c = io * a / nnsvt
    grad_i = - c - b  # di/dvd
    grad_v = 1.0 - grad_i * rs  # dv/dvd
    # dp/dv = d(iv)/dv = v * di/dv + i
    grad = grad_i / grad_v  # di/dv
    p = i * v
    grad_p = v * grad + i  # dp/dv
    grad2i = -c / nnsvt
    grad2v = -grad2i * rs
    grad2p = (
        grad_v * grad + v * (grad2i/grad_v - grad_i*grad2v/grad_v**2) + grad_i
    )
    # generate exact values
    data = dict(zip((il, io, rs, rsh, nnsvt), ARGS))
    vdtest = np.linspace(0, pvsystem.est_voc(IL, I0, NNSVTH), IVCURVE_NPTS)
    expected = []
    for test in vdtest:
        data[vd] = test
        test_data = {
            'i': np.float64(i.evalf(subs=data)),
            'v': np.float64(v.evalf(subs=data)),
            'p': np.float64(p.evalf(subs=data)),
            'grad_i': np.float64(grad_i.evalf(subs=data)),
            'grad_v': np.float64(grad_v.evalf(subs=data)),
            'grad': np.float64(grad.evalf(subs=data)),
            'grad_p': np.float64(grad_p.evalf(subs=data)),
            'grad2p': np.float64(grad2p.evalf(subs=data))
        }
        LOGGER.debug(test_data)
        expected.append(test_data)
    return pd.DataFrame(expected, index=vdtest)


def test_numerical_precicion():
    """
    Test that there are no numerical errors due to floating point arithmetic.
    """
    expected = pd.read_csv(DATA_PATH)
    vdtest = np.linspace(0, pvsystem.est_voc(IL, I0, NNSVTH), IVCURVE_NPTS)
    results = pvsystem.bishop88(vdtest, *ARGS, gradients=True)
    assert np.allclose(expected['i'], results[0])
    assert np.allclose(expected['v'], results[1])
    assert np.allclose(expected['p'], results[2])
    assert np.allclose(expected['grad_i'], results[3])
    assert np.allclose(expected['grad_v'], results[4])
    assert np.allclose(expected['grad'], results[5])
    assert np.allclose(expected['grad_p'], results[6])
    assert np.allclose(expected['grad2p'], results[7])


if __name__ == '__main__':
    expected = generate_numerical_precicion()
    expected.to_csv(DATA_PATH)
    test_numerical_precicion()
