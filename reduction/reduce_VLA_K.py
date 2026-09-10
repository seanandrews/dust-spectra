import os
import sys
import numpy as np
from casatools import msmetadata
from scipy.interpolate import interp1d
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')


# I/O paths
pipe_dir = '/data/sandrews/VLA_LP/data/VLA/'
proc_dir = '/d4/asha1/dust-spec/DR/VLA/'


# fixed quantities: observing band, SPWs, flux calibrator, channel binning
band = 'K'
bspw = '0~63'
calname = '3C138'
chbin = 64


# execution identifiers
EB = ['06_1', '07_1', '07_2', '11_1', '04_1', '01_1', '05_1', '07_3',
      '08_1']
EB = [band + item + '/' for item in EB]


# MS filenames for pipeline-processed datasets
msfile = ['sb48810508.eb48958255.60840.666593518516_targets_cont',
          'sb48810731.eb48997054.60863.586843599536_targets_cont_data_column',
          'sb48810731.eb49026595.60871.56697115741_targets_cont_data_column',
          'sb48812515.eb49041185.60883.513033958334_targets_cont_data_column',
          'sb48809530.eb49041219.60884.43355821759_targets_cont',
          'sb48808152.eb49074659.60891.39462178241_targets_cont_data_column',
          'sb48810056.eb49079865.60892.498031724535_targets_cont_data_column',
          'sb48810731.eb49108423.60895.4173605324_targets_cont_data_column',
          'sb48811165.eb49119294.60896.383778125004_targets_cont_data_column']
msfile = ['25A-330.' + item + '.ms' for item in msfile]


# additional RFI flagging ranges (determined by direct inspection)
rfi_flags = '0:0~8.010GHz,10:9.325~12GHz,11:9.457~9.481GHz,' + \
            '28:11.570~11.585GHz;11.606~11.626GHz,' + \
            '29:11.68~11.73GHz,31:11.96~15GHz'

time_flags = [None, None, None, None, None, None, None, None, None]


# get the list of VLA labels from the target dictionary
_ = [(k, td[k]['vlabel']) for k in td.keys()]
src, vlbls = map(list, zip(*_))



# Loop over batch of MS files
for i in [3,4,5,6,7,8]:  #range(len(EB)):
    # tracking
    print(f"\nReducing dataset {i:02d} for execution {EB[i]}...")

    # get a list of the targets
    msmd = msmetadata()
    msmd.open(pipe_dir + msfile[i])
    fieldnames = msmd.fieldnames()
    msmd.close()

    # parse into target names (for output) and field names (for access)
    tfields = [item for item in fieldnames if item in vlbls]
    ix = [item for item, x in enumerate(vlbls) if x in tfields]
    targ_names = [src[item] for item in ix]
    targ_fields = [vlbls[item] for item in ix]
    field_str = ', '.join(str(j) for j in targ_fields)
    print('\n' + field_str)

    # check if the MS file has a corrected data column
    has_corr = has_corrected_column(pipe_dir + msfile[i])
    use_col = 'corrected' if has_corr else 'data'

    # temporary copy of the pipeline-processed MS for the target fields
    if not os.path.exists(proc_dir + EB[i]):
        os.system('mkdir ' + proc_dir + EB[i])
    init_MS = proc_dir + EB[i] + 'pipeline.init.ms'
    os.system('rm -rf ' + init_MS + '*')
    mstransform(vis=pipe_dir + msfile[i], outputvis=init_MS, 
                datacolumn=use_col, field=field_str)

    # standard RFI flag set
    flagdata(vis=init_MS, mode='manual', spw=rfi_flags, flagbackup=False)

    # execution-specific time flagging
    if time_flags[i] is not None:
        flagdata(vis=init_MS, mode='manual', spw='', timerange=time_flags[i],
                 flagbackup=False)



    # rescale the fluxes based on interpolation between bootstrap executions
    ms.open(init_MS)
    med_time = np.median(ms.getdata('TIME')['time'])
    ms.close()
    _ = np.load('flux_bootstrap/' + calname + '_' + band + '.npz')
    mjd, calfact = _['mjd'], _['calfact']
    cfint = interp1d(mjd, calfact, axis=1, kind='linear', bounds_error=False,
                     fill_value=(calfact[:,0], calfact[:,-1]))
    cf = list(cfint(med_time))
    caltbl = init_MS.replace('.ms', '.gencal')
    os.system('rm -rf ' + caltbl + '*')
    gencal(vis=init_MS, caltable=caltbl, caltype='amp', spw=bspw, parameter=cf)
    applycal(vis=init_MS, gaintable=caltbl, calwt=True, flagbackup=True)
    fr_MS = proc_dir + EB[i] + 'pipeline.flag_rescale.ms'
    os.system('rm -rf ' + fr_MS + '*')
    os.system('cp -rf ' + init_MS + ' ' + fr_MS)
    mstransform(vis=init_MS, outputvis=fr_MS, datacolumn='corrected', spw=bspw)



    # Loop over each target field
    for j in range(len(targ_fields)):
        print('\n Averaging and splitting data for '+targ_fields[j]+' ... ')
        
        # Spectral averaging (1 pseudo-channel per SPW)
        o_MS = proc_dir + EB[i] + targ_names[j] + '.' + band + '.reduced.ms'
        os.system('rm -rf ' + o_MS + '*')
        mstransform(vis=fr_MS, outputvis=o_MS, datacolumn='data', spw=bspw,
                    field=targ_fields[j], chanaverage=True, chanbin=chbin,
                    correlation='RR,LL')


    # Remove pipeline MS copy to save space
    os.system('rm -rf ' + init_MS + '*')
    print('----------------------------------------------------------------')
