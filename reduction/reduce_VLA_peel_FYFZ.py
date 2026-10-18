import os
import sys
from pathlib import Path
import glob
import numpy as np
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')


# user controls
targ = ['FY_FZTau']
eb = '13_1'


band = 'U'
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
    subs = [str(i) for i in range(48)]



for it in range(len(targ)):

    # load a list of relevant EBs from the dictionary information
    src = td[targ[it]]

    # make sure there's a peel subdirectory to work in
    peel_dir = proc_dir + band + eb + '/peel/'
    if not os.path.exists(peel_dir):
        os.system('mkdir ' + peel_dir)
    if not os.path.exists(peel_dir + 'images/'):
        os.system('mkdir ' + peel_dir + 'images/')


    print('\nPeeling individual sub-bands for ' + targ[it] + \
          ', ' + band + eb + '\n')

    ### Transfer self-calibrated data products
    # time-average the self-calibrated measurement set
    print('Time-averaging the self-calibrated measurement set...')
    os.system('rm -rf ' + peel_dir + targ[it] + \
              '.' + band + '.selfcal.tavg.ms')
    visname = proc_dir + band + eb + '/' + targ[it] + '.' + band + '.selfcal'
    mstransform(vis=visname + '.ms',
                outputvis=peel_dir + targ[it] + '.' + band + '.selfcal.tavg.ms',
                datacolumn='data', timeaverage=True, timebin=timebin, spw='')
    os.system('cp -r ' + visname + '.ms ' + \
              peel_dir + targ[it] + '.' + band + '.selfcal.tavg.ms')


    ### Imaging to define peel subjects
    # image the time-averged, self-calibrated measurement set
    print('MTMFS imaging the full-band, time-averaged, dataset...')
    vname = peel_dir + targ[it] + '.' + band + '.selfcal.tavg'
    cell, imsize, e_beam, nu_, pb = imparamcalc(vname + '.ms', D_ant=25.)

    idict = src[band][band + eb]
    nt, lnt, imscl = idict['nt'], idict['lnt'], idict['imscl']

    iname = peel_dir + 'images/' + targ[it] + '.' + band + '.selfcal.tavg'
    for ext in exts: os.system('rm -rf ' + iname + ext)

    smask = peel_dir + 'images/FYFZ_special_2.mask'


    if 'skip_strip' in idict:
        skip_strip = idict['skip_strip']
    else: skip_strip = False

    if skip_strip:
        oname = out_dir + targ[it] + '.' + band + eb + '.full'
        os.system('rm -rf ' + oname + '.vis.npz')
        export_vis(vname + '.ms', oname + '.vis.npz')
    else:
        ### Generate a target mask (accounting for source proper motion)
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
            mxx, myy = pm_corr(dt_epoch, src['RA'], src['DEC'], 
                               src['mua'], src['mud'])
            targ_mask = "circle[[" + mxx + ", " + myy + "], " + mrr + "]"

        tmask = peel_dir + 'images/' + targ[it] + '.' + band + '.targ.mask'
        os.system('rm -rf ' + tmask + '*')
        makemask(mode='copy', 
                 inpimage=smask,
                 inpmask=targ_mask,
                 output=tmask)


        ### Cycle through subbands
        os.system('rm -rf ' + peel_dir + targ[it] + '.' + band + '-sub*')
        for isub in range(len(subs)):
            # split out the subband SPWs
            sname = targ[it] + '.' + band + '-sub' + str(isub).zfill(2)
            mstransform(vis=vname + '.ms', outputvis=peel_dir + sname + '.ms', 
                        datacolumn='data', spw=subs[isub])

            # image time-averaged, self-calibrated subband measurement set 
            # using the peel mask and fixed imaging parameters
            print('\nImaging with peel mask for subband ' + band + \
                  '-sub' + str(isub).zfill(2) + '...')
            sname = peel_dir + targ[it] + '.' + band + \
                    '-sub' + str(isub).zfill(2)
            s_cell, s_ims, s_bm, s_nu, s_pb = imparamcalc(vname + '.ms', 
                                                          D_ant=25.)
        
            iname = peel_dir + 'images/' + targ[it] + '.' + band + '-sub' + \
                    str(isub).zfill(2) + '.peel'
            for ext in exts: os.system('rm -rf ' + iname + ext)
            tclean(vis=sname + '.ms', imagename=iname, selectdata=True,
                   datacolumn='data', specmode='mfs', gridder='standard',
                   deconvolver='mtmfs', scales=[0], pblimit=-0.1, nterms=1,
                   weighting='briggs', robust=2.0, imsize=int(imscl * imsize), 
                   cell=cell, niter=100000, nsigma=1.0, interactive=False,
                   usemask='user', mask=peel_dir+'images/FYFZ_special_2.mask', 
                   savemodel='modelcolumn')


            # subtract the masked model and split out the peeled dataset
            uvsub(vis=sname + '.ms')
            os.system('rm -rf ' + sname + '.targ_only.ms')
            mstransform(vis=sname + '.ms', 
                        outputvis=sname + '.targ_only.ms', 
                        datacolumn='corrected')

            # image the peeled, target-only, subband measurement set
            print('Imaging with target mask for peeled subband ' + band + \
                  '-sub' + str(isub).zfill(2) + '...')
            iname = peel_dir + 'images/' + targ[it] + '.' + band + '-sub' + \
                    str(isub).zfill(2) + '.targ_only'
            for ext in exts: os.system('rm -rf ' + iname + ext)
            tclean(vis=sname + '.targ_only.ms', imagename=iname, 
                   selectdata=True, datacolumn='data', specmode='mfs', 
                   gridder='standard', deconvolver='mtmfs', scales=[0], 
                   pblimit=-0.1, nterms=1, weighting='briggs', robust=2.0, 
                   imsize=int(imscl * imsize), cell=cell, niter=100000, 
                   nsigma=1.0, interactive=False, usemask='user', mask=tmask, 
                   savemodel='modelcolumn')


        ### Post-peel, full-band imaging 
        # concatenate the peeled MSs and export the data to preferred format
        pref = peel_dir + targ[it] + '.' + band + '-sub'
        suff = '.targ_only.ms'
        snms = [pref + str(i).zfill(2) + suff for i in range(len(subs))]
        fname = peel_dir + targ[it] + '.' + band + '-full.targ_only'
        os.system('rm -rf ' + fname + '.ms')
        concat(vis=snms, concatvis=fname + '.ms', 
               dirtol='0.1arcsec', freqtol='50Hz', copypointing=False)
        oname = out_dir + targ[it] + '.' + band + eb + '.full'
        os.system('rm -rf ' + oname + '.vis.npz')
        export_vis(fname + '.ms', oname + '.vis.npz')

        # image the concatenated peeled MS
        print('Imaging the concatenated, peeled (target-only) dataset...')
        iname = peel_dir + 'images/' + targ[it] + '.' + band + '-full.targ_only'
        for ext in exts: os.system('rm -rf ' + iname + ext)
        tclean(vis=fname + '.ms', imagename=iname, selectdata=True, 
               datacolumn='data', specmode='mfs', gridder='standard', 
               deconvolver='mtmfs', scales=[0], pblimit=-0.1, nterms=2, 
               weighting='briggs', robust=2.0, imsize=int(imscl * imsize), 
               cell=cell, interactive=False, niter=100000, nsigma=1.0, 
               usemask='user', mask=tmask, threshold='0.01mJy', pbmask=0.0, 
               savemodel='none')
