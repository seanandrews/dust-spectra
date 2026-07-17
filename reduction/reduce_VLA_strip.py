import os
import sys
from pathlib import Path
import glob
import numpy as np
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')


# user controls
targ = 'GOTau'
band = 'X'
eb = '12_1'
timebin = '30s'



### Basic definitions
# paths
proc_dir = '/d4/asha1/dust-spectra/DR/VLA/'
out_dir = '/d4/asha1/dust-spectra/fluxes/vis_data/'
exts = ['.image', '.mask', '.model', '.pb', '.psf', '.residual', '.sumwt', 
        '.*.tt0', '.*.tt1', '.*.tt2', '.alpha', '.alpha.error']

# define the subbands
if band == 'X':
    subs = ['0~7', '8~15', '16~23', '23~31']
if band == 'U':
    subs = ['36~47', '24~35', '12~23', '0~11']

# load a list of relevant EBs from the dictionary information
src = td[targ]

# make sure there's a strip subdirectory to work in
strip_dir = proc_dir + band + eb + '/strip/'
if not os.path.exists(strip_dir):
    os.system('mkdir ' + strip_dir)
if not os.path.exists(strip_dir + 'images/'):
    os.system('mkdir ' + strip_dir + 'images/')


print('\nStripping individual sub-bands for ' + targ + ', ' + band + eb + '\n')

### Transfer self-calibrated data products
# time-average the self-calibrated measurement set
print('Time-averaging the self-calibrated measurement set...')
os.system('rm -rf ' + strip_dir + targ + '.' + band + '.selfcal.tavg.ms')
mstransform(vis=proc_dir + band + eb + '/' + targ + '.' + band + '.selfcal.ms',
            outputvis=strip_dir + targ + '.' + band + '.selfcal.tavg.ms',
            datacolumn='data', timeaverage=True, timebin=timebin, spw='')


### Imaging to define strip subjects
# image the time-averged, self-calibrated measurement set
print('MTMFS imaging the full-band, time-averaged, dataset...')
vname = strip_dir + targ + '.' + band + '.selfcal.tavg'
cell, imsize, e_beam, nu_, pb = imparamcalc(vname + '.ms', D_ant=25.)

idict = src[band][band + eb]
nt, lnt, imscl = idict['nt'], idict['lnt'], idict['imscl']

iname = strip_dir + 'images/' + targ + '.' + band + '.selfcal.tavg'
for ext in exts: os.system('rm -rf ' + iname + ext)

tclean(vis=vname + '.ms', imagename=iname, selectdata=True, datacolumn='data', 
       specmode='mfs', gridder='standard', deconvolver='mtmfs', scales=[0], 
       pblimit=-0.1, nterms=2, weighting='briggs', robust=2.0, 
       imsize=int(imscl * imsize), cell=cell, interactive=False, niter=100000, 
       nsigma=1.0, usemask='auto-multithresh', cutthreshold=0.05,
       noisethreshold=nt, lownoisethreshold=lnt, smoothfactor=1.0, 
       sidelobethreshold=2.0, minbeamfrac=0.1, pbmask=0.0, savemodel='none')


### Generate a target-free mask of strip subjects
# get the epoch differential for this observation 
ms.open(vname + '.ms')
tstart_MS = ms.getdata(['time'])['time'][0]
ms.close()
dt_epoch = mjd_to_decimal_year(tstart_MS) - 2000.

# generate a target(s)-only region mask
mrr = str(np.max([round(e_beam * 4, 1), 3.5])) + 'arcsec'
if isinstance(src['RA'], list):
    targ_mask = []
    for ic in range(len(src['RA'])):
        mxx, myy = pm_corr(dt_epoch, src['RA'][ic], src['DEC'][ic],
                           src['mua'][ic], src['mud'][ic])
        targ_mask += ["circle[[" + mxx + ", " + myy + "], " + mrr + "]"]
else:
    mxx, myy = pm_corr(dt_epoch, src['RA'], src['DEC'], src['mua'], src['mud'])
    targ_mask = "circle[[" + mxx + ", " + myy + "], " + mrr + "]"

tmask = strip_dir + 'images/' + targ + '.' + band + '.targ.mask'
os.system('rm -rf ' + tmask + '*')
makemask(mode='copy', inpimage=iname + '.image.tt0', inpmask=targ_mask,
         output=tmask)

# remove the overlap with the target mask to generate the strip mask
smask = strip_dir + 'images/' + targ + '.' + band + '.no_targ.mask'
os.system('rm -rf ' + smask)
immath(imagename=[iname + '.mask', tmask], outfile=smask, 
       imagemd=iname + '.mask', mode='evalexpr', expr='iif(IM1>0.5, 0.0, IM0)')


### Estimate the RMS noise level outside the target + stripped mask
print('')
masked_im = iname + '.masked.image.tt0'
os.system('rm -rf ' + iname + '.masked.image.tt0')
immath(imagename=[iname + '.image.tt0', iname + '.mask'], 
       outfile=iname + '.masked.image.tt0', imagemd=iname + '.image.tt0', 
       mode='evalexpr', expr='iif(IM1<0.5, IM0, 0.0)')
RMS = imstat(imagename=iname + '.masked.image.tt0')['rms'][0]
print('')
print(f'Full-band RMS noise estimate = {RMS * 1e6:.1f} uJy')
RMS_str = f'{1.5 * RMS * 1e3:.3f}mJy'



### Cycle through subbands
os.system('rm -rf ' + strip_dir + targ + '.' + band + '-sub*')
for isub in range(len(subs)):
    # split out the subband SPWs
    sname = targ + '.' + band + '-sub' + str(isub).zfill(2)
    mstransform(vis=vname + '.ms', outputvis=strip_dir + sname + '.ms', 
                datacolumn='data', spw=subs[isub])

    # image the time-averaged, self-calibrated subband measurement set using 
    # the strip mask and fixed imaging parameters
    print('\nImaging with strip mask for subband ' + band + \
          '-sub' + str(isub).zfill(2) + '...')
    sname = strip_dir + targ + '.' + band + '-sub' + str(isub).zfill(2)
    s_cell, s_ims, s_beam, s_nu, s_pb = imparamcalc(sname + '.ms', D_ant=25.)
        
    iname = strip_dir + 'images/' + targ + '.' + band + '-sub' + \
            str(isub).zfill(2) + '.strip'
    for ext in exts: os.system('rm -rf ' + iname + ext)
    tclean(vis=sname + '.ms', imagename=iname, selectdata=True,
           datacolumn='data', specmode='mfs', gridder='standard',
           deconvolver='mtmfs', scales=[0], pblimit=-0.1, nterms=2,
           weighting='briggs', robust=2.0, imsize=int(imscl * imsize), 
           cell=cell, niter=100000, nsigma=1.0, interactive=False,
           usemask='user', mask=smask, threshold=RMS_str, 
           savemodel='modelcolumn')

    # subtract the clean model and split out 
    uvsub(vis=sname + '.ms')
    os.system('rm -rf ' + sname + '.targ_only.ms')
    mstransform(vis=sname + '.ms', 
                outputvis=sname + '.targ_only.ms', datacolumn='corrected')

    # image the stripped, target-only, subband measurement set
    print('Imaging with target mask for stripped subband ' + band + \
          '-sub' + str(isub).zfill(2) + '...')
    iname = strip_dir + 'images/' + targ + '.' + band + '-sub' + \
            str(isub).zfill(2) + '.targ_only'
    for ext in exts: os.system('rm -rf ' + iname + ext)
    tclean(vis=sname + '.targ_only.ms', imagename=iname, selectdata=True,
           datacolumn='data', specmode='mfs', gridder='standard',
           deconvolver='mtmfs', scales=[0], pblimit=-0.1, nterms=2,
           weighting='briggs', robust=2.0, imsize=int(imscl * imsize), 
           cell=cell, niter=100000, nsigma=1.0, interactive=False,
           usemask='user', mask=tmask, threshold=RMS_str,
           savemodel='modelcolumn')

    # export visibilities to preferred modeling format
    oname = out_dir + targ + '.' + band + eb + '.sub' + str(isub).zfill(2)
    os.system('rm -rf ' + oname + '.vis.npz')
    export_vis(sname + '.targ_only.ms', oname + '.vis.npz')
