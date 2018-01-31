"""
testing way faster single-diode methods using JW Bishop 1988
"""

from time import clock
import logging
import numpy as np
from pvlib import pvsystem
from pvlib.way_faster import faster_way, slower_way
from conftest import requires_scipy

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

POA = 888
TCELL = 55
CECMOD = pvsystem.retrieve_sam('cecmod')


@requires_scipy
def test_fast_spr_e20_327():
    spr_e20_327 = CECMOD.SunPower_SPR_E20_327
    x = pvsystem.calcparams_desoto(
        poa_global=POA, temp_cell=TCELL,
        alpha_isc=spr_e20_327.alpha_sc, module_parameters=spr_e20_327,
        EgRef=1.121, dEgdT=-0.0002677)
    il, io, rs, rsh, nnsvt = x
    tstart = clock()
    pvs = pvsystem.singlediode(*x)
    tstop = clock()
    dt_slow = tstop - tstart
    LOGGER.debug('single diode elapsed time = %g[s]', dt_slow)
    tstart = clock()
    out = faster_way(*x)
    tstop = clock()
    isc, voc, imp, vmp, pmp, ix, ixx = out.values()
    dt_fast = tstop - tstart
    LOGGER.debug('way faster elapsed time = %g[s]', dt_fast)
    LOGGER.debug('spr_e20_327 speedup = %g', dt_slow / dt_fast)
    assert np.isclose(pvs['i_sc'], isc)
    assert np.isclose(pvs['v_oc'], voc)
    # the singlediode method doesn't actually get the MPP correct
    pvs_imp = pvsystem.i_from_v(rsh, rs, nnsvt, vmp, io, il)
    pvs_vmp = pvsystem.v_from_i(rsh, rs, nnsvt, imp, io, il)
    assert np.isclose(pvs_imp, imp)
    assert np.isclose(pvs_vmp, vmp)
    assert np.isclose(pvs['p_mp'], pmp)
    assert np.isclose(pvs['i_x'], ix)
    pvs_ixx = pvsystem.i_from_v(rsh, rs, nnsvt, (voc + vmp)/2, io, il)
    assert np.isclose(pvs_ixx, ixx)
    return isc, voc, imp, vmp, pmp, pvs


@requires_scipy
def test_fast_fs_495():
    fs_495 = CECMOD.First_Solar_FS_495
    x = pvsystem.calcparams_desoto(
        poa_global=POA, temp_cell=TCELL,
        alpha_isc=fs_495.alpha_sc, module_parameters=fs_495,
        EgRef=1.475, dEgdT=-0.0003)
    il, io, rs, rsh, nnsvt = x
    x += (101, )
    tstart = clock()
    pvs = pvsystem.singlediode(*x)
    tstop = clock()
    dt_slow = tstop - tstart
    LOGGER.debug('single diode elapsed time = %g[s]', dt_slow)
    tstart = clock()
    out = faster_way(*x)
    tstop = clock()
    isc, voc, imp, vmp, pmp, ix, ixx, i, v, p = out.values()
    dt_fast = tstop - tstart
    LOGGER.debug('way faster elapsed time = %g[s]', dt_fast)
    LOGGER.debug('fs_495 speedup = %g', dt_slow / dt_fast)
    assert np.isclose(pvs['i_sc'], isc)
    assert np.isclose(pvs['v_oc'], voc)
    # the singlediode method doesn't actually get the MPP correct
    pvs_imp = pvsystem.i_from_v(rsh, rs, nnsvt, vmp, io, il)
    pvs_vmp = pvsystem.v_from_i(rsh, rs, nnsvt, imp, io, il)
    assert np.isclose(pvs_imp, imp)
    assert np.isclose(pvs_vmp, vmp)
    assert np.isclose(pvs['p_mp'], pmp)
    assert np.isclose(pvs['i_x'], ix)
    pvs_ixx = pvsystem.i_from_v(rsh, rs, nnsvt, (voc + vmp)/2, io, il)
    assert np.isclose(pvs_ixx, ixx)
    return isc, voc, imp, vmp, pmp, i, v, p, pvs


@requires_scipy
def test_slow_spr_e20_327():
    spr_e20_327 = CECMOD.SunPower_SPR_E20_327
    x = pvsystem.calcparams_desoto(
        poa_global=POA, temp_cell=TCELL,
        alpha_isc=spr_e20_327.alpha_sc, module_parameters=spr_e20_327,
        EgRef=1.121, dEgdT=-0.0002677)
    il, io, rs, rsh, nnsvt = x
    tstart = clock()
    pvs = pvsystem.singlediode(*x)
    tstop = clock()
    dt_slow = tstop - tstart
    LOGGER.debug('single diode elapsed time = %g[s]', dt_slow)
    tstart = clock()
    out = slower_way(*x)
    tstop = clock()
    isc, voc, imp, vmp, pmp, ix, ixx = out.values()
    dt_fast = tstop - tstart
    LOGGER.debug('way faster elapsed time = %g[s]', dt_fast)
    LOGGER.debug('spr_e20_327 speedup = %g', dt_slow / dt_fast)
    assert np.isclose(pvs['i_sc'], isc)
    assert np.isclose(pvs['v_oc'], voc)
    # the singlediode method doesn't actually get the MPP correct
    pvs_imp = pvsystem.i_from_v(rsh, rs, nnsvt, vmp, io, il)
    pvs_vmp = pvsystem.v_from_i(rsh, rs, nnsvt, imp, io, il)
    assert np.isclose(pvs_imp, imp)
    assert np.isclose(pvs_vmp, vmp)
    assert np.isclose(pvs['p_mp'], pmp)
    assert np.isclose(pvs['i_x'], ix)
    pvs_ixx = pvsystem.i_from_v(rsh, rs, nnsvt, (voc + vmp)/2, io, il)
    assert np.isclose(pvs_ixx, ixx)
    return isc, voc, imp, vmp, pmp, pvs


@requires_scipy
def test_slow_fs_495():
    fs_495 = CECMOD.First_Solar_FS_495
    x = pvsystem.calcparams_desoto(
        poa_global=POA, temp_cell=TCELL,
        alpha_isc=fs_495.alpha_sc, module_parameters=fs_495,
        EgRef=1.475, dEgdT=-0.0003)
    il, io, rs, rsh, nnsvt = x
    x += (101, )
    tstart = clock()
    pvs = pvsystem.singlediode(*x)
    tstop = clock()
    dt_slow = tstop - tstart
    LOGGER.debug('single diode elapsed time = %g[s]', dt_slow)
    tstart = clock()
    out = slower_way(*x)
    tstop = clock()
    isc, voc, imp, vmp, pmp, ix, ixx, i, v, p = out.values()
    dt_fast = tstop - tstart
    LOGGER.debug('way faster elapsed time = %g[s]', dt_fast)
    LOGGER.debug('fs_495 speedup = %g', dt_slow / dt_fast)
    assert np.isclose(pvs['i_sc'], isc)
    assert np.isclose(pvs['v_oc'], voc)
    # the singlediode method doesn't actually get the MPP correct
    pvs_imp = pvsystem.i_from_v(rsh, rs, nnsvt, vmp, io, il)
    pvs_vmp = pvsystem.v_from_i(rsh, rs, nnsvt, imp, io, il)
    assert np.isclose(pvs_imp, imp)
    assert np.isclose(pvs_vmp, vmp)
    assert np.isclose(pvs['p_mp'], pmp)
    assert np.isclose(pvs['i_x'], ix)
    pvs_ixx = pvsystem.i_from_v(rsh, rs, nnsvt, (voc + vmp)/2, io, il)
    assert np.isclose(pvs_ixx, ixx)
    return isc, voc, imp, vmp, pmp, i, v, p, pvs


if __name__ == '__main__':
    r_fast_spr_e20_327 = test_fast_spr_e20_327()
    r_fast_fs_495 = test_fast_fs_495()
    r_slow_spr_e20_327 = test_slow_spr_e20_327()
    r_slow_fs_495 = test_slow_fs_495()
