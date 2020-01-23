import os
import numpy as np
import pandas as pd
from collections import OrderedDict

import pytest

from pvlib.ivtools import sdm
from pvlib import pvsystem

from pvlib.tests.conftest import requires_scipy, requires_pysam
from pvlib.tests.conftest import requires_statsmodels

BASEDIR = os.path.dirname(__file__)
TESTDIR = os.path.dirname(BASEDIR)
PROJDIR = os.path.dirname(TESTDIR)
DATADIR = os.path.join(PROJDIR, 'data')
TESTDATA = os.path.join(DATADIR, 'ivtools_numdiff.dat')


@pytest.fixture
def get_test_iv_params():
    return {'IL': 8.0, 'I0': 5e-10, 'Rsh': 1000, 'Rs': 0.2, 'nNsVth': 1.61864}


@pytest.fixture
def cec_params_cansol_cs5p_220p():
    return {'ivcurve': {'V_mp_ref': 46.6, 'I_mp_ref': 4.73, 'V_oc_ref': 58.3,
                        'I_sc_ref': 5.05},
            'specs': {'alpha_sc': 0.0025, 'beta_voc': -0.19659,
                      'gamma_pmp': -0.43, 'cells_in_series': 96},
            'params': {'a_ref': 2.3674, 'I_L_ref': 5.056, 'I_o_ref': 1.01e-10,
                       'R_sh_ref': 837.51, 'R_s': 1.004, 'Adjust': 2.3}}


@requires_pysam
def test_fit_cec_sam(cec_params_cansol_cs5p_220p):
    input_data = cec_params_cansol_cs5p_220p['ivcurve']
    specs = cec_params_cansol_cs5p_220p['specs']
    I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, Adjust = \
        sdm.fit_cec_sam(
            celltype='polySi', v_mp=input_data['V_mp_ref'],
            i_mp=input_data['I_mp_ref'], v_oc=input_data['V_oc_ref'],
            i_sc=input_data['I_sc_ref'], alpha_sc=specs['alpha_sc'],
            beta_voc=specs['beta_voc'],
            gamma_pmp=specs['gamma_pmp'],
            cells_in_series=specs['cells_in_series'])
    expected = pd.Series(cec_params_cansol_cs5p_220p['params'])
    modeled = pd.Series(index=expected.index, data=np.nan)
    modeled['a_ref'] = a_ref
    modeled['I_L_ref'] = I_L_ref
    modeled['I_o_ref'] = I_o_ref
    modeled['R_s'] = R_s
    modeled['R_sh_ref'] = R_sh_ref
    modeled['Adjust'] = Adjust
    assert np.allclose(modeled.values, expected.values, rtol=5e-2)
    # test for fitting failure
    with pytest.raises(RuntimeError):
        I_L_ref, I_o_ref, R_s, R_sh_ref, a_ref, Adjust = \
            sdm.fit_cec_sam(
                celltype='polySi', v_mp=0.45, i_mp=5.25, v_oc=0.55, i_sc=5.5,
                alpha_sc=0.00275, beta_voc=0.00275, gamma_pmp=0.0055,
                cells_in_series=1, temp_ref=25)


@requires_scipy
def test_fit_desoto():
    result, _ = sdm.fit_desoto(v_mp=31.0, i_mp=8.71, v_oc=38.3, i_sc=9.43,
                               alpha_sc=0.005658, beta_voc=-0.13788,
                               cells_in_series=60)
    result_expected = {'I_L_ref': 9.45232,
                       'I_o_ref': 3.22460e-10,
                       'R_s': 0.297814,
                       'R_sh_ref': 125.798,
                       'a_ref': 1.59128,
                       'alpha_sc': 0.005658,
                       'EgRef': 1.121,
                       'dEgdT': -0.0002677,
                       'irrad_ref': 1000,
                       'temp_ref': 25}
    assert np.allclose(pd.Series(result), pd.Series(result_expected),
                       rtol=1e-4)


@requires_scipy
def test_fit_desoto_failure():
    with pytest.raises(RuntimeError) as exc:
        sdm.fit_desoto(v_mp=31.0, i_mp=8.71, v_oc=38.3, i_sc=9.43,
                       alpha_sc=0.005658, beta_voc=-0.13788,
                       cells_in_series=10)
    assert ('Parameter estimation failed') in str(exc.value)


@requires_scipy
@requires_statsmodels
def test_fit_desoto_sandia(cec_params_cansol_cs5p_220p):
    # this test computes a set of IV curves for the input fixture, fits
    # the De Soto model to the calculated IV curves, and compares the fitted
    # parameters to the starting values
    params = cec_params_cansol_cs5p_220p['params']
    params.pop('Adjust')
    specs = cec_params_cansol_cs5p_220p['specs']
    effective_irradiance = np.array([400., 500., 600., 700., 800., 900.,
                                     1000.])
    temp_cell = np.array([15., 25., 35., 45.])
    ee = np.tile(effective_irradiance, len(temp_cell))
    tc = np.repeat(temp_cell, len(effective_irradiance))
    iph, io, rs, rsh, nnsvth = pvsystem.calcparams_desoto(
        ee, tc, alpha_sc=specs['alpha_sc'], **params)
    sim_ivcurves = pvsystem.singlediode(iph, io, rs, rsh, nnsvth, 300)
    sim_ivcurves['ee'] = ee
    sim_ivcurves['tc'] = tc

    result = sdm.fit_desoto_sandia(sim_ivcurves, specs)
    modeled = pd.Series(index=params.keys(), data=np.nan)
    modeled['a_ref'] = result['a_ref']
    modeled['I_L_ref'] = result['I_L_ref']
    modeled['I_o_ref'] = result['I_o_ref']
    modeled['R_s'] = result['R_s']
    modeled['R_sh_ref'] = result['R_sh_ref']
    expected = pd.Series(params)
    assert np.allclose(modeled.values, expected.values, rtol=5e-2)


@requires_scipy
@requires_statsmodels
def test_fit_pvsyst_sandia(disp=False, npts=3000):
    spec_list = ['cells_in_series', 'alpha_sc', 'beta_voc', 'descr']
    iv_specs = dict.fromkeys(spec_list)
    keylist = ['i_sc', 'i_mp', 'v_mp', 'v_oc', 'poa', 'tc', 'ee']
    ivcurves = dict.fromkeys(keylist)

    with open(os.path.join(BASEDIR, 'PVsyst_demo.txt'), 'r') as f:

        Ns, aIsc, bVoc, descr = f.readline().split(',')

        iv_specs.update(
            cells_in_series=int(Ns), aisc=float(aIsc), bvoc=float(bVoc),
            descr=descr)

        strN, strM = f.readline().split(',')
        N = int(strN)
        M = int(strM)

        isc = np.empty(N)
        imp = np.empty(N)
        vmp = np.empty(N)
        voc = np.empty(N)
        ee = np.empty(N)
        poa = np.empty(N)
        tc = np.empty(N)
        v = np.empty((N, M))
        i = np.empty((N, M))
        v[:] = np.nan  # fill with nan
        i[:] = np.nan

        for k in range(N):
            tmp = (float(x) for x in f.readline().split(','))
            isc[k], imp[k], vmp[k], voc[k], poa[k], tc[k], ee[k] = tmp
            # read voltage and current
            tmp = [float(x) for x in f.readline().split(',')]
            while len(tmp) < M:
                tmp.append(np.nan)
            v[k, :] = tmp
            tmp = [float(x) for x in f.readline().split(',')]
            while len(tmp) < M:
                tmp.append(np.nan)
            i[k, :] = tmp

    ivcurves['i_sc'] = isc[:npts]
    ivcurves['i_mp'] = imp[:npts]
    ivcurves['v_oc'] = voc[:npts]
    ivcurves['v_mp'] = vmp[:npts]
    ivcurves['ee'] = ee[:npts]
    ivcurves['tc'] = tc[:npts]
    ivcurves['v'] = v[:npts]
    ivcurves['i'] = i[:npts]

    pvsyst_specs = dict.fromkeys(spec_list)
    paramlist = [
        'I_L_ref', 'I_o_ref', 'EgRef', 'R_s', 'R_sh_ref', 'R_sh_0', 'R_sh_exp',
        'gamma_ref', 'mu_gamma']
    varlist = ['iph', 'io', 'rs', 'rsh', 'u']
    pvsyst = OrderedDict(key=(paramlist + varlist))

    with open(os.path.join(BASEDIR, 'PVsyst_demo_model.txt'), 'r') as f:

        Ns, aIsc, bVoc, descr = f.readline().split(',')

        pvsyst_specs.update(
            cells_in_series=int(Ns), alpha_sc=float(aIsc),
            beta_voc=float(bVoc), descr=descr)

        tmp = [float(x) for x in f.readline().split(',')]
        # I_L_ref, I_o_ref, EgRef, R_s, R_sh_ref, R_sh_0, R_sh_exp, gamma_ref,
        # mu_gamma
        pvsyst.update(zip(paramlist, tmp))

        strN = f.readline()
        N = int(strN)

        Iph = np.empty(N)
        Io = np.empty(N)
        Rsh = np.empty(N)
        Rs = np.empty(N)
        u = np.empty(N)

        for k in range(N):
            tmp = [float(x) for x in f.readline().split(',')]
            Iph[k], Io[k], Rsh[k], Rs[k], u[k] = tmp

    pvsyst.update(zip(varlist, [Iph, Io, Rs, Rsh, u]))

    expected = sdm.fit_pvsyst_sandia(ivcurves, iv_specs)
    param_res = pvsystem.calcparams_pvsyst(
        effective_irradiance=ivcurves['ee'], temp_cell=ivcurves['tc'],
        alpha_sc=iv_specs['aisc'], gamma_ref=expected['gamma_ref'],
        mu_gamma=expected['mu_gamma'], I_L_ref=expected['I_L_ref'],
        I_o_ref=expected['I_o_ref'], R_sh_ref=expected['R_sh_ref'],
        R_sh_0=expected['R_sh_0'], R_s=expected['R_s'],
        cells_in_series=iv_specs['cells_in_series'], EgRef=expected['EgRef'])
    iv_res = pvsystem.singlediode(*param_res)

    ivcurves['p_mp'] = ivcurves['v_mp'] * ivcurves['i_mp']  # power
    if disp:
        return expected, pvsyst, ivcurves, iv_specs, param_res, iv_res

    # assertions
    assert np.allclose(
        ivcurves['p_mp'], iv_res['p_mp'], equal_nan=True, rtol=0.038)
    assert np.allclose(
        ivcurves['v_mp'], iv_res['v_mp'], equal_nan=True, rtol=0.029)
    assert np.allclose(
        ivcurves['i_mp'], iv_res['i_mp'], equal_nan=True, rtol=0.021)
    assert np.allclose(
        ivcurves['i_sc'], iv_res['i_sc'], equal_nan=True, rtol=0.003)
    assert np.allclose(
        ivcurves['v_oc'], iv_res['v_oc'], equal_nan=True, rtol=0.019)
    # cells_in_series, aisc, bvoc, descr
    assert all((iv_specs[spec] == pvsyst_specs[spec]) for spec in spec_list)
    # I_L_ref, I_o_ref, EgRef, R_sh_ref, R_sh_0, R_sh_exp, R_s, gamma_ref,
    # mu_gamma
    assert np.isclose(expected['I_L_ref'], pvsyst['I_L_ref'], rtol=6.5e-5)
    assert np.isclose(expected['I_o_ref'], pvsyst['I_o_ref'], rtol=0.15)
    assert np.isclose(expected['R_s'], pvsyst['R_s'], rtol=0.0035)
    assert np.isclose(expected['R_sh_ref'], pvsyst['R_sh_ref'], rtol=0.091)
    assert np.isclose(expected['R_sh_0'], pvsyst['R_sh_0'], rtol=0.013)
    assert np.isclose(expected['EgRef'], pvsyst['EgRef'], rtol=0.037)
    assert np.isclose(expected['gamma_ref'], pvsyst['gamma_ref'], rtol=0.0045)
    assert np.isclose(expected['mu_gamma'], pvsyst['mu_gamma'], rtol=0.064)

    # Iph, Io, Rsh, Rs, u
    mask = np.ones(expected['u'].shape, dtype=bool)
    # exclude one curve with different convergence
    umask = mask.copy()
    umask[2540] = False
    assert all(expected['u'][umask] == pvsyst['u'][:npts][umask])
    assert np.allclose(
        expected['iph'][expected['u']], pvsyst['iph'][:npts][expected['u']],
        equal_nan=True, rtol=0.0009)
    assert np.allclose(
        expected['io'][expected['u']], pvsyst['io'][:npts][expected['u']],
        equal_nan=True, rtol=0.096)
    assert np.allclose(
        expected['rs'][expected['u']], pvsyst['rs'][:npts][expected['u']],
        equal_nan=True, rtol=0.035)
    # exclude one curve with Rsh outside 63% tolerance
    rshmask = expected['u'].copy()
    rshmask[2545] = False
    assert np.allclose(
        expected['rsh'][rshmask], pvsyst['rsh'][:npts][rshmask],
        equal_nan=True, rtol=0.63)


@requires_scipy
@pytest.mark.parametrize('vmp, imp, iph, io, rs, rsh, nnsvth, expected', [
    (2., 2., 2., 2., 2., 2., 2., np.nan),
    (2., 2., 0., 2., 2., 2., 2., np.nan),
    (2., 2., 2., 0., 2., 2., 2., np.nan),
    (2., 2., 2., 2., 0., 2., 2., np.nan),
    (2., 2., 2., 2., 2., 0., 2., np.nan),
    (2., 2., 2., 2., 2., 2., 0., np.nan)])
def test__update_rsh_fixed_pt_nans(vmp, imp, iph, io, rs, rsh, nnsvth,
                                   expected):
    outrsh = sdm._update_rsh_fixed_pt(vmp, imp, iph, io, rs, rsh, nnsvth)
    assert np.all(np.isnan(outrsh))


@requires_scipy
def test__update_rsh_fixed_pt_vmp0():
    outrsh = sdm._update_rsh_fixed_pt(vmp=0., imp=2., iph=2., io=2., rs=2.,
                                      rsh=2., nnsvth=2.)
    np.testing.assert_allclose(outrsh, np.array([502.]), atol=.0001)


@requires_scipy
def test__update_rsh_fixed_pt_vector():
    outrsh = sdm._update_rsh_fixed_pt(rsh=np.array([-1., 3, .5, 2.]),
                                      rs=np.array([1., -.5, 2., 2.]),
                                      io=np.array([.2, .3, -.4, 2.]),
                                      iph=np.array([-.1, 1, 3., 2.]),
                                      nnsvth=np.array([4., -.2, .1, 2.]),
                                      imp=np.array([.2, .2, -1., 2.]),
                                      vmp=np.array([0., -1, 0., 0.]))
    assert np.all(np.isnan(outrsh[0:3]))
    np.testing.assert_allclose(outrsh[3], np.array([502.]), atol=.0001)


@requires_scipy
@pytest.mark.parametrize('voc, iph, io, rs, rsh, nnsvth, expected', [
    (2., 2., 2., 2., 2., 2., 0.5911),
    (2., 2., 2., 0., 2., 2., 0.5911),
    (2., 2., 0., 2., 2., 2., 0.),
    (2., 0., 2., 2., 2., 2., 1.0161e-4),
    (0., 2., 2., 2., 2., 2., 17.9436)])
def test__update_io(voc, iph, io, rs, rsh, nnsvth, expected):
    outio = sdm._update_io(voc, iph, io, rs, rsh, nnsvth)
    np.testing.assert_allclose(outio, expected, atol=.0001)


@requires_scipy
@pytest.mark.parametrize('voc, iph, io, rs, rsh, nnsvth', [
    (2., 2., 2., 2., 2., 0.),
    (-1., -1., -1., -1., -1., -1.)])
def test__update_io_nan(voc, iph, io, rs, rsh, nnsvth):
    outio = sdm._update_io(voc, iph, io, rs, rsh, nnsvth)
    assert np.isnan(outio)


@requires_scipy
@pytest.mark.parametrize('vmp, imp, iph, io, rs, rsh, nnsvth, expected', [
    (2., 2., 2., 2., 2., 2., 2., (1.8726, 2.)),
    (2., 0., 2., 2., 2., 2., 2., (1.8726, 3.4537)),
    (2., 2., 0., 2., 2., 2., 2., (1.2650, 0.8526)),
    (0., 2., 2., 2., 2., 2., 2., (1.5571, 2.))])
def test__calc_theta_phi_exact(vmp, imp, iph, io, rs, rsh, nnsvth, expected):
    theta, phi = sdm._calc_theta_phi_exact(vmp, imp, iph, io, rs, rsh, nnsvth)
    np.testing.assert_allclose(theta, expected[0], atol=.0001)
    np.testing.assert_allclose(phi, expected[1], atol=.0001)


@requires_scipy
@pytest.mark.parametrize('vmp, imp, iph, io, rs, rsh, nnsvth', [
    (2., 2., 2., 0., 2., 2., 2.),
    (2., 2., 2., 2., 2., 2., 0.),
    (2., 0., 2., 2., 2., 0., 2.)])
def test__calc_theta_phi_exact_both_nan(vmp, imp, iph, io, rs, rsh, nnsvth):
    theta, phi = sdm._calc_theta_phi_exact(vmp, imp, iph, io, rs, rsh, nnsvth)
    assert np.isnan(theta)
    assert np.isnan(phi)


@requires_scipy
def test__calc_theta_phi_exact_one_nan():
    theta, phi = sdm._calc_theta_phi_exact(imp=2., iph=2., vmp=2., io=2.,
                                           nnsvth=2., rs=0., rsh=2.)
    assert np.isnan(theta)
    np.testing.assert_allclose(phi, 2., atol=.0001)


@requires_scipy
def test__calc_theta_phi_exact_vector():
    theta, phi = sdm._calc_theta_phi_exact(imp=np.array([1., -1.]),
                                           iph=np.array([-1., 1.]),
                                           vmp=np.array([1., -1.]),
                                           io=np.array([-1., 1.]),
                                           nnsvth=np.array([1., -1.]),
                                           rs=np.array([-1., 1.]),
                                           rsh=np.array([1., -1.]))
    assert np.isnan(theta[0])
    assert np.isnan(theta[1])
    assert np.isnan(phi[0])
    np.testing.assert_allclose(phi[1], 2.2079, atol=.0001)
