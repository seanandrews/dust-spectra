import os
import sys
import numpy as np
from casatools import msmetadata
from scipy.interpolate import interp1d
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')


# I/O paths
pipe_dir = '/data/sandrews/VLA_LP/data/ALMA/2025.1.00321.S/'
proc_dir = '/d4/asha1/dust-spectra/DR/ALMA/'


# fixed quantities: observing band, channel binning
band = 'B1'
chbin = 128         # closely matches VLA Q-band binning (1 chan / SPW there,
                    # corresponds to 15 channels / SPW here)


# execution identifiers
sg = ['science_goal.uid___A001_X3839_X295/', 
      'science_goal.uid___A001_X3839_X295/',
      'science_goal.uid___A001_X3839_X28e/',
      'science_goal.uid___A001_X3839_X28e/',
      'science_goal.uid___A001_X3839_X28e/',
      'science_goal.uid___A001_X3839_X28e/',
      'science_goal.uid___A001_X3839_X29f/',
      'science_goal.uid___A001_X3839_X295/',
      'science_goal.uid___A001_X3839_X29f/',
      'science_goal.uid___A001_X3839_X2ac/',
      'science_goal.uid___A001_X3839_X2ac/',
      'science_goal.uid___A001_X3839_X29f/',
      'science_goal.uid___A001_X3839_X295/',
      'science_goal.uid___A001_X3839_X28e/',
      'science_goal.uid___A001_X3839_X29f/']
gous = ['group.uid___A001_X3839_X29c/', 
        'group.uid___A001_X3839_X29c/',
        'group.uid___A001_X3839_X292/',
        'group.uid___A001_X3839_X292/',
        'group.uid___A001_X3839_X292/',
        'group.uid___A001_X3839_X292/',
        'group.uid___A001_X3839_X2a0/',
        'group.uid___A001_X3839_X296/',
        'group.uid___A001_X3839_X2a6/',
        'group.uid___A001_X3839_X2ad/',
        'group.uid___A001_X3839_X2b0/',
        'group.uid___A001_X3839_X2a3/',
        'group.uid___A001_X3839_X299/',
        'group.uid___A001_X3839_X28f/',
        'group.uid___A001_X3839_X2a9/']
mous = ['member.uid___A001_X3839_X29d/', 
        'member.uid___A001_X3839_X29d/',
        'member.uid___A001_X3839_X293/',
        'member.uid___A001_X3839_X293/',
        'member.uid___A001_X3839_X293/',
        'member.uid___A001_X3839_X293/',
        'member.uid___A001_X3839_X2a1/',
        'member.uid___A001_X3839_X297/',
        'member.uid___A001_X3839_X2a7/',
        'member.uid___A001_X3839_X2ae/',
        'member.uid___A001_X3839_X2b1/',
        'member.uid___A001_X3839_X2a4/',
        'member.uid___A001_X3839_X29a/',
        'member.uid___A001_X3839_X290/',
        'member.uid___A001_X3839_X2aa/']
EB = ['01_1', '01_2', '02_1', '02_2', '02_3', '02_4', '03_1', '04_1', '05_1',
      '06_1', '07_1', '08_1', '09_1', '10_1', '11_1'] 
EB = [band + '_' + item + '/' for item in EB]


# MS filenames for pipeline-processed datasets
msfile = ['uid___A002_X13270a2_X16eba_targets.ms',
          'uid___A002_X133b089_X165ee_targets.ms',
          'uid___A002_X13270a2_X172a1_targets.ms',
          'uid___A002_X133dde2_X27318_targets.ms',
          'uid___A002_X133dde2_X27575_targets.ms',
          'uid___A002_X133dde2_X279f7_targets.ms',
          'uid___A002_X13270a2_X1ffa9_targets.ms',
          'uid___A002_X132e57d_Xe6fc_targets.ms',
          'uid___A002_X132e57d_Xea0d_targets.ms',
          'uid___A002_X132e57d_Xebeb_targets.ms',
          'uid___A002_X133b089_X1715b_targets.ms',
          'uid___A002_X133b089_X17728_targets.ms',
          'uid___A002_X133b089_X17872_targets.ms',
          'uid___A002_X133b089_X179ea_targets.ms',
          'uid___A002_X133dde2_X27019_targets.ms']




# Loop over batch of MS files
for i in range(len(msfile)):
    # tracking
    print(f"\nReducing dataset {i:02d} for execution {EB[i]}...")

    # get a list of the targets from the pipeline-processed MS file
    pipe_path = pipe_dir + sg[i] + gous[i] + mous[i] + 'calibrated_final/' + \
                'measurement_sets/'
    msmd = msmetadata()
    msmd.open(pipe_path + msfile[i])
    fieldnames = msmd.fieldnames()
    msmd.close()

    # parse into target names (for output) and field names (for access)
    targ_fields = [item for item in fieldnames if item in td.keys()]

    # check if the MS file has a corrected data column
    has_corr = has_corrected_column(pipe_path + msfile[i])
    use_col = 'corrected' if has_corr else 'data'

    # processed directory
    if not os.path.exists(proc_dir + EB[i]):
        os.system('mkdir ' + proc_dir + EB[i])

    # Loop over each target field
    for j in range(len(targ_fields)):
        print('\n Averaging and splitting data for '+targ_fields[j]+' ... ')

        # identify which SPWs have useful data for this target
        msmd = casatools.msmetadata()
        msmd.open(pipe_path + msfile[i])
        SPWID = msmd.spwsforfield(targ_fields[j])
        spws = ','.join(map(str, SPWID))
        msmd.close()
        
        # Spectral averaging 
        o_MS = proc_dir + EB[i] + targ_fields[j] + '.' + band + '.reduced.ms'
        os.system('rm -rf ' + o_MS + '*')
        mstransform(vis=pipe_path + msfile[i], outputvis=o_MS, 
                    datacolumn=use_col, spw=spws, field=targ_fields[j], 
                    chanaverage=True, chanbin=chbin)

    print('----------------------------------------------------------------')
