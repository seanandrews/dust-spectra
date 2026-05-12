import os
import sys
import numpy as np
from casatools import msmetadata
from scipy.interpolate import interp1d
sys.path.append('.')
from targets_dict import targ as td
#execfile('reduction_tools.py')


# I/O paths
pipe_dir = '/data/sandrews/VLA_LP/data/VLA/'
proc_dir = '/d4/asha1/dust-spec/DR/VLA/'


# fixed quantities: observing band, SPWs, flux calibrator, channel binning
band = 'X'
bspw = '0~31'
calname = '3C138'
chbin = 64


# execution identifiers
EB = ['03_1', '11_1', '12_1', '01_1', '10_1', '01_2', '07_1', '08_1',
      '05_1', '14_1', '04_1', '06_1', '09_1', '13_1', '03_2', '02_1', 
      '14_2', '07_2', '12_2', '18_1', '15_1', '16_1', '16_2', '17_1']
EB = [band + item + '/' for item in EB]


# MS filenames for pipeline-processed datasets
msfile = ['sb48829784.eb48927155.60821.833398229166_targets_cont',
          'sb48833475.eb48936464.60826.821180555555_targets_cont',
          'sb48833859.eb48936892.60827.83169114584_targets_cont',
          'sb48829373.eb48940822.60829.83844501157_targets_cont_data_column',
          'sb48832414.eb48949534.60832.799824340276_targets_cont',
          'sb48828973.eb48949560.60833.81233049768_targets_cont_data_column',
          'sb48831257.eb48949582.60834.835955601855_targets_cont',
          'sb48831626.eb48952297.60836.767009675925_targets_cont',
          'sb48830471.eb48957189.60839.76233471065_targets_cont',
          'sb48834841.eb48957581.60839.86754622685_targets_cont',
          'sb48830226.eb48958259.60840.82695858796_targets_cont',
          'sb48830672.eb48958277.60841.62774427084_targets_cont',
          'sb48832014.eb48958281.60841.768722187495_targets_cont',
          'sb48834063.eb48964813.60845.536979282406_targets_cont',
          'sb48829784.eb48966133.60847.80787053241_targets_cont',
          'sb48829182.eb48967391.60848.585893877316_targets_cont',
          'sb48834539.eb48967593.60850.55250611111_targets_cont',
          'sb48831068.eb48970526.60853.52720679398_targets_cont',
          'sb48833655.eb49034255.60880.45885700232_targets_cont',
          'sb49058849.eb49071093.60890.694885150464_targets_cont',
          'sb49055824.eb49079253.60892.388710949075_targets_cont',
          'sb49056557.eb49083214.60892.678362280094_targets_cont',
          'sb49056557.eb49122442.60896.6622600463_targets_cont',
          'sb49057019.eb49123036.60897.59742288194_targets_cont']
msfile = ['25A-330.' + item + '.ms' for item in msfile]


# additional RFI flagging ranges (determined by direct inspection)
rfi_flags = '0:~8.010GHz,10:9.325~9.380GHz,11:9.457~9.481GHz,' + \
            '28:11.570~11.585GHz;11.606~11.626GHz'

#            '28:11.560~11.568GHz,' + \
#            '27:11.469~11.475GHz,' + \
#            '28:11.625~11.635GHz,' + \
#            '29:11.70~11.72GHz'


# get the list of VLA labels from the target dictionary
_ = [(k, td[k]['vlabel']) for k in td.keys()]
src, vlbls = map(list, zip(*_))



# Loop over batch of MS files
for i in [0]: #range(len(EB)):

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


    #fields = msmd.fieldsforintent('OBSERVE_TARGET#UNSPECIFIED')
    #field_names = msmd.namesforfields(fields)
#    field_str = ', '.join(str(j) for j in fields)
#    print('\nProcessing data for '+bloc[i]+' in \n      '+msfile[i]+' ...')
#    print('containing '+band+'-band observations of ')
#    for j in range(len(field_names)): print('      '+field_names[j])


    # Check if the MS file has a corrected data column
#    has_corr = has_corrected_column(data_dir+msfile[i])
#    if has_corr:
#        use_col = 'corrected'
#    else:
#        use_col = 'data'


    # Make a temporary copy of the pipeline-processed MS for the target fields
#    if not os.path.exists(bloc_dir+bloc[i]):
#        print('... making the directory '+bloc_dir+bloc[i])
#        os.system('mkdir '+bloc_dir+bloc[i])
#    i_MS = bloc_dir+bloc[i]+'pipeline.init.ms'
#    os.system('rm -rf '+i_MS+'*')
#    mstransform(vis=data_dir+msfile[i], outputvis=i_MS, datacolumn=use_col,
#                field=field_str)


    # Get the date for this execution (in MJD seconds)
#    ms.open(i_MS)
#    med_time = np.median(ms.getdata('TIME')['time'])
#    ms.close()


    # rescale the fluxes based on interpolation between bootstrap executions
#    _ = np.load('flux_bootstrap/'+calname+'_'+band+'.npz')
#    mjd, calfact = _['mjd'], _['calfact']
#    cfint = interp1d(mjd, calfact, axis=1, kind='linear', bounds_error=False,
#                     fill_value=(calfact[:,0], calfact[:,-1]))
#    cf = list(cfint(med_time))
#    caltbl = i_MS.replace('.ms', '.gencal')
#    os.system('rm -rf '+caltbl+'*')
#    gencal(vis=i_MS, caltable=caltbl, caltype='amp', spw=bspw, parameter=cf)
#    applycal(vis=i_MS, gaintable=caltbl, calwt=True, flagbackup=True)
#    f_MS = bloc_dir+bloc[i]+'flux_rescale.init.ms'
#    os.system('rm -rf '+f_MS+'*')
#    mstransform(vis=i_MS, outputvis=f_MS, datacolumn='corrected', spw=bspw)


    # Flag any additional RFI
#    if rfi_flags is not None:
#        flagdata(vis=f_MS, mode='manual', spw=rfi_flags, flagbackup=False)


    # Loop over each target field
#    for j in range(len(fields)):
#        print('\n Averaging and splitting data for '+field_names[j]+' ... ')
        
        # Spectral averaging (1 pseudo-channel per SPW)
#        o_MS = bloc_dir+bloc[i]+field_names[j]+'.'+band+'.post.spavg.ms'
#        os.system('rm -rf '+o_MS+'*')
#        mstransform(vis=f_MS, outputvis=o_MS, datacolumn='data', spw=bspw,
#                    field=field_names[j], chanaverage=True, chanbin=64)


    # Remove pipeline MS copy to save space
#    os.system('rm -rf '+i_MS+'*')
#    print('----------------------------------------------------------------')
