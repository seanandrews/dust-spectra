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
band = 'B3l'
chbin = 128         # bandwidth-smearing for ALMA B3 to B10 is negligible for
                    # the purposes of this program; this is full-SPW averaging


# execution identifiers
sg = ['science_goal.uid___A001_X3833_X665b/', 
      'science_goal.uid___A001_X3833_X665b/',
      'science_goal.uid___A001_X3833_X665b/',
      'science_goal.uid___A001_X3833_X665b/',
      'science_goal.uid___A001_X3833_X665b/',
      'science_goal.uid___A001_X3833_X665b/']
gous = ['group.uid___A001_X3833_X665f/',
        'group.uid___A001_X3833_X665c/',
        'group.uid___A001_X3833_X6662/',
        'group.uid___A001_X3833_X6665/',
        'group.uid___A001_X3833_X6665/', 
        'group.uid___A001_X3833_X6665/']
mous = ['member.uid___A001_X3833_X6660/',
        'member.uid___A001_X3833_X665d/',
        'member.uid___A001_X3833_X6663/',
        'member.uid___A001_X3833_X6666/',
        'member.uid___A001_X3833_X6666/',
        'member.uid___A001_X3833_X6666/']
EB = ['01_1', '02_1', '03_1', '04_1', '04_2', '04_3']
EB = [band + '_' + item + '/' for item in EB]


# MS filenames for pipeline-processed datasets
msfile = ['uid___A002_X131e84e_X188f1_targets.ms',
          'uid___A002_X13270a2_X20261_targets.ms',
          'uid___A002_X132e57d_X18d78_targets.ms',
          'uid___A002_X133b089_Xda88_targets.ms',
          'uid___A002_X133b089_Xdf7d_targets.ms',
          'uid___A002_X133b089_Xe356_targets.ms']


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

    print(fieldnames)

sys.exit()


for i in range(len(msfile)):

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
