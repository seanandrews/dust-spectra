import os
import sys
import numpy as np
from casatools import msmetadata
from scipy.interpolate import interp1d
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')
execfile('VLA_flagging.py')



# User specifies band and, optionally, specific EB
band = 'X'
s_EB = '08_1'



# -------------------------------------

# I/O paths
pipe_dir = '/data/sandrews/VLA_LP/data/VLA/'
proc_dir = '/d4/asha1/dust-spectra/DR/VLA/'


# retrieve full list of pipelined datafiles and identifiers for this band
EB, pipe_ms = np.loadtxt('files_VLA_' + band + '.txt', dtype=str).T


# if desired, select a specific EB to process
if s_EB is not None:
    pipe_ms = pipe_ms[EB == s_EB]
    EB = EB[EB == s_EB]
EB = [band + item + '/' for item in EB]


# get the list of VLA labels from the target dictionary
_ = [(k, td[k]['vlabel']) for k in td.keys()]
src, vlbls = map(list, zip(*_))



### loop over EBs
for i in range(len(EB)):

    print(f"----------------------------\nReducing data for execution {EB[i]}")


    # get a list of the fields in the pipelined datafile
    msmd = msmetadata()
    msmd.open(pipe_dir + pipe_ms[i] + '.ms')
    fieldnames = msmd.fieldnames()
    msmd.close()


    # extract fieldnames and associated with target dictionary keys
    tfields = [item for item in fieldnames if item in vlbls]
    ix = [item for item, x in enumerate(vlbls) if x in tfields]
    targs = [src[item] for item in ix]
    targ_fields = [vlbls[item] for item in ix]
    field_str = ', '.join(str(j) for j in targ_fields)
    print('\n    target fields:')
    for j in targ_fields: print('        -  ' + j)


    # check if the pipelined datafile has a 'corrected' column
    has_corr = has_corrected_column(pipe_dir + pipe_ms[i] + '.ms')
    use_col = 'corrected' if has_corr else 'data'


    # make a temporary copy of the pipelined datafile in a processing space
    prog = pipe_ms[i].split('.')[0] + '/'

    if not os.path.exists(proc_dir + prog + EB[i]):
        os.system('mkdir ' + proc_dir + prog + EB[i])

    init_ms = proc_dir + prog + EB[i] + 'pipeline.init'
#    os.system('rm -rf ' + init_ms + '*')
#    mstransform(vis=pipe_dir + pipe_ms[i] + '.ms', outputvis=init_ms + '.ms',
#                datacolumn=use_col, field=field_str)

    
    # bespoke additional flagging
    print('\n    bespoke flagging ....')
    _ = VLA_flags(init_ms + '.ms')



    ### bootstrap the amplitude scale
    # get median time of the EB and number of SPWs
    ms.open(init_ms + '.ms')
    med_time = np.median(ms.getdata('TIME')['time'])
    spw_info = ms.getspectralwindowinfo()
    ms.close()

    # get SPW string
    bspw = '0~' + str(len(spw_info) - 1)

    # load the bootstrapped 3C 138 fluxes in each SPW and define interpolator;
    # for times beyond bootstrap sample range, fix at the edge values
    print('\n    amplitude rescaling from bootstrap ....')
    _ = np.load('flux_bootstrap/3C138_' + band + '.npz')
    mjd, calfact = _['mjd'], _['calfact']
    cfint = interp1d(mjd, calfact, axis=1, kind='linear', bounds_error=False,
                     fill_value=(calfact[:,0], calfact[:,-1]))

    # interpolate to EB time
    cf = list(cfint(med_time))

    # produce the gain factor and apply the rescaling
    boot_cal = init_ms + '.gencal'
    os.system('rm -rf ' + boot_cal + '*')
    gencal(vis=init_ms + '.ms', caltable=boot_cal, spw=bspw, caltype='amp', 
           parameter=cf)
    applycal(vis=init_ms + '.ms', gaintable=boot_cal, calwt=True)

    # copy out the corrected data
    flag_rescale_ms = proc_dir + prog + EB[i] + 'pipeline.flag_rescale'
    os.system('rm -rf ' + flag_rescale_ms + '.ms*')
    mstransform(vis=init_ms + '.ms', outputvis=flag_rescale_ms + '.ms', 
                datacolumn='corrected', spw=bspw)


    # determine number of channels per SPW (assuming all SPWs are the same)
    msmd = msmetadata()
    msmd.open(flag_rescale_ms + '.ms')
    nchan = msmd.nchan(0)
    msmd.close()


    # loop over fields to frequency-average
    for j in range(len(targ_fields)):

        print('\n    spectral averaging data for ' + targs[j] + ' .... ')

        # spectral averaging
        out_ms = proc_dir + prog + EB[i] + targs[j] + '.' + band + '.reduced'
        os.system('rm -rf ' + out_ms + '.ms*')
        mstransform(vis=flag_rescale_ms + '.ms', outputvis=out_ms + '.ms', 
                    datacolumn='data', field=targ_fields[j], spw=bspw,
                    correlation='RR,LL', chanaverage=True, chanbin=nchan)


    # Remove pipeline MS copy to save space
    os.system('rm -rf ' + init_ms + '.ms*')
    print('----------------------------\n')
