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
sg = 'science_goal.uid___A001_X3833_X665b/'
gous = 'group.uid___A001_X3833_X6665/'
mous = 'member.uid___A001_X3833_X6666/'
EB = band + '_04_combined/'

# MS filenames for pipeline-processed datasets
msfile = ['uid___A002_X133b089_Xda88_targets.ms',
          'uid___A002_X133b089_Xdf7d_targets.ms',
          'uid___A002_X133b089_Xe356_targets.ms']

raw_path = pipe_dir + sg + gous + mous
#os.system('rm -rf ' + raw_path + 'combined.ms')
#vfiles = [raw_path + 'calibrated_final/measurement_sets/' + item for item in msfile]
#concat(vis=vfiles, concatvis=raw_path + 'combined.ms', 
#       freqtol='50Hz', dirtol='0.1arcsec', copypointing=False)

# get a list of the targets from the pipeline-processed MS file
msmd = msmetadata()
msmd.open(raw_path + 'combined.ms')
fieldnames = msmd.fieldnames()
msmd.close()

# parse into target names (for output) and field names (for access)
targ_fields = [item for item in fieldnames if item in td.keys()]

targ_fields = ['FY_FZTau', 'GI_GKTau', 'MHO1']
tfields = ['FY-FZTau', 'GI-GKTau', 'MHO1-2']

# check if the MS file has a corrected data column
has_corr = has_corrected_column(raw_path + 'combined.ms')
use_col = 'corrected' if has_corr else 'data'

# processed directory
if not os.path.exists(proc_dir + EB):
    os.system('mkdir ' + proc_dir + EB)

# Loop over each target field
for j in range(len(targ_fields)):
    print('\n Averaging and splitting data for '+targ_fields[j]+' ... ')

    # identify which SPWs have useful data for this target
    msmd = casatools.msmetadata()
    msmd.open(raw_path + 'combined.ms')
    #SPWID = msmd.spwsforfield(targ_fields[j])
    SPWID = msmd.spwsforfield(tfields[j])
    spws = ','.join(map(str, SPWID))
    msmd.close()
        
    # Spectral averaging 
    o_MS = proc_dir + EB + targ_fields[j] + '.' + band + '.reduced.ms'
    os.system('rm -rf ' + o_MS + '*')
    mstransform(vis=raw_path + 'combined.ms', outputvis=o_MS, 
                datacolumn=use_col, spw=spws, field=tfields[j], 
                chanaverage=True, chanbin=chbin)

    print('----------------------------------------------------------------')
