import os
import sys
from pathlib import Path
import glob
import numpy as np
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')


# user controls
band = 'B1'
EB = ['01_1', '01_2', '02_1', '02_2', '02_3', '02_4', '03_1', '04_1', '05_1',
      '06_1', '07_1', '08_1', '09_1', '10_1', '11_1']
timebin = '30s'



### Basic definitions
# paths
proc_dir = '/d4/asha1/dust-spectra/DR/ALMA/'
out_dir = '/d4/asha1/dust-spectra/fluxes/vis_data/'
exts = ['.image', '.mask', '.model', '.pb', '.psf', '.residual', '.sumwt', 
        '.*.tt0', '.*.tt1', '.*.tt2', '.alpha', '.alpha.error']

# define the subbands
if band == 'X':
    subs = ['0~7', '8~15', '16~23', '23~31']
if band == 'U':
    subs = ['36~47', '24~35', '12~23', '0~11']
if band == 'B1':
    subs = ['0~1', '2~3']


for i in range(len(EB)):

    # identify the available targets and reduced MS filenames
    EB_dir = proc_dir + band + '_' + EB[i]
    ms = [f.name for f in Path(EB_dir).glob('*.' + band + '.selfcal.ms')]
    targs = [f.split('.' + band + '.selfcal.ms', 1)[0] for f in ms]
    msfiles = [proc_dir + band + '_' + EB[i] + f for f in ms]
    print(targs)

    # make sure there's a peel subdirectory to work in
    peel_dir = proc_dir + band + '_' + EB[i] + '/peel/'
    if not os.path.exists(peel_dir):
        os.system('mkdir ' + peel_dir)
    if not os.path.exists(peel_dir + 'images/'):
        os.system('mkdir ' + peel_dir + 'images/')


    for it in range(len(targs)):

        # load a list of relevant EBs from the dictionary information
        src = td[targs[it]]
        print('\nPeeling individual sub-bands for ' + targs[it] + \
              ', ' + band + '_' + EB[i] + '\n')

        ### Transfer self-calibrated data products
        # time-average the self-calibrated measurement set
        print('Time-averaging the self-calibrated measurement set...')
        os.system('rm -rf ' + peel_dir + targs[it] + \
                  '.' + band + '.selfcal.tavg.ms')
        visname = proc_dir + band + '_' + EB[i] + '/' + targs[it] + '.' + \
                  band + '.selfcal'
        vname = peel_dir + targs[it] + '.' + band + '.selfcal.tavg.ms'
        os.system('rm -rf ' + vname)
        mstransform(vis=visname + '.ms', outputvis=vname, datacolumn='data', 
                    timeaverage=True, timebin=timebin, spw='')


        ### Imaging to define peel subjects
        # image the time-averged, self-calibrated measurement set
        print('MTMFS imaging the full-band, time-averaged, dataset...')
        cell, imsize, e_beam, nu_, pb = imparamcalc(vname, D_ant=12.)

        idict = src[band][band + '_' + EB[i]]
        nt, lnt, imscl = idict['nt'], idict['lnt'], idict['imscl']

        # make a clean mask (can add background sources with automask)
        ms = casatools.ms()
        ms.open(vname)
        tstart_MS = ms.getdata(['time'])['time'][0]
        ms.close()
        dt_epoch = mjd_to_decimal_year(tstart_MS) - 2000.

        mrr = str(np.max([round(e_beam * 3, 1), 3.0])) + 'arcsec'
        if isinstance(src['RA'], list):
            imask = []
            for ic in range(len(src['RA'])):
                mxx, myy = pm_corr(dt_epoch, src['RA'][ic], src['DEC'][ic],
                                   src['mua'][ic], src['mud'][ic])
                imask += ["circle[[" + mxx + ", " + myy + "], " + mrr + "]"]
        else:
            mxx, myy = pm_corr(dt_epoch, src['RA'], src['DEC'],
                               src['mua'], src['mud'])
            imask = "circle[[" + mxx + ", " + myy + "], " + mrr + "]"

        iname = peel_dir + 'images/' + targs[it] + '.' + band + '.selfcal.tavg'
        for ext in exts: os.system('rm -rf ' + iname + ext)

        # shallow clean around target (to ensure it is masked)
        tclean(vis=vname, imagename=iname, selectdata=True, datacolumn='data', 
               specmode='mfs', gridder='standard', deconvolver='mtmfs', 
               scales=[0], pblimit=-0.1, nterms=2, weighting='briggs',
               robust=2.0, imsize=int(imscl * imsize), cell=cell, niter=100, 
               nsigma=1.0, interactive=False, usemask='user', mask=imask, 
               pbmask=0., savemodel='modelcolumn')

        # deeper clean + add automask for background sources
        tclean(vis=vname, imagename=iname, selectdata=True, datacolumn='data', 
               specmode='mfs', gridder='standard', deconvolver='mtmfs', 
               scales=[0], pblimit=-0.1, nterms=2, weighting='briggs',
               robust=2.0, imsize=int(imscl * imsize), cell=cell, niter=100000, 
               nsigma=1.0, interactive=False, usemask='auto-multithresh', 
               cutthreshold=0.05, noisethreshold=nt, lownoisethreshold=lnt,
               smoothfactor=1.0, sidelobethreshold=2.0, minbeamfrac=0.1, 
               pbmask=0., restart=True, savemodel='modelcolumn')

        smask = iname + '.mask'


        if 'skip_strip' in idict:
            skip_strip = idict['skip_strip']
        else: skip_strip = False

        if skip_strip:
            oname = out_dir + targs[it] + '.' + band + '_' + EB[i] + '.full'
            os.system('rm -rf ' + oname + '.vis.npz')
            export_vis(vname + '.ms', oname + '.vis.npz')
        else:
            tmask = peel_dir + 'images/' + targs[it] + '.' + band + \
                    '.targ.mask'
            os.system('rm -rf ' + tmask + '*')
            makemask(mode='copy', inpimage=iname + '.image.tt0', 
                     inpmask=imask, output=tmask)

            ### Estimate the RMS noise level outside the full-band mask
            print('')
            masked_im = iname + '.masked.image.tt0'
            os.system('rm -rf ' + iname + '.masked.image.tt0')
            immath(imagename=[iname + '.image.tt0', iname + '.mask'], 
                   outfile=iname + '.masked.image.tt0', 
                   imagemd=iname + '.image.tt0', 
                   mode='evalexpr', expr='iif(IM1<0.5, IM0, 0.0)')
            RMS = imstat(imagename=iname + '.masked.image.tt0')['rms'][0]
            print('')
            print(f'Full-band RMS noise estimate = {RMS * 1e6:.1f} uJy')
            RMS_str = f'{1.5 * RMS * 1e3:.3f}mJy'


            ### Cycle through subbands
            os.system('rm -rf ' + peel_dir + targs[it] + '.' + band + '-sub*')
            for isub in range(len(subs)):
                # split out the subband SPWs
                sname = targs[it] + '.' + band + '-sub' + str(isub).zfill(2)
                mstransform(vis=vname, outputvis=peel_dir + sname + '.ms', 
                            datacolumn='data', spw=subs[isub])

                # image time-averaged, self-calibrated subband measurement set 
                # using the peel mask and fixed imaging parameters
                print('\nImaging with peel mask for subband ' + band + \
                      '-sub' + str(isub).zfill(2) + '...')
                sname = peel_dir + targs[it] + '.' + band + \
                        '-sub' + str(isub).zfill(2)
                s_cell, s_ims, s_bm, s_nu, s_pb = imparamcalc(sname + '.ms', 
                                                              D_ant=12.)
        
                iname = peel_dir + 'images/' + targs[it] + '.' + band + \
                        '-sub' + str(isub).zfill(2) + '.peel'
                for ext in exts: os.system('rm -rf ' + iname + ext)
                tclean(vis=sname + '.ms', imagename=iname, selectdata=True,
                       datacolumn='data', specmode='mfs', gridder='standard',
                       deconvolver='mtmfs', scales=[0], pblimit=-0.1, nterms=2,
                       weighting='briggs', robust=2.0, 
                       imsize=int(imscl * imsize), cell=cell, niter=100000, 
                       nsigma=1.0, interactive=False, usemask='user', 
                       mask=smask, threshold=RMS_str, savemodel='modelcolumn')

                # remove contributions from the target(s) in the clean model
                os.system('rm -rf ' + iname + '.model.tt0.target-masked')
                immath(imagename=[iname + '.model.tt0', tmask],
                       outfile=iname + '.model.tt0.target-masked',
                       imagemd=iname + '.model.tt0',
                       mode='evalexpr', expr='IM0 * (1 - IM1)')

                os.system('rm -rf ' + iname + '.model.tt1.target-masked')
                immath(imagename=[iname + '.model.tt1', tmask],
                       outfile=iname + '.model.tt1.target-masked',
                       imagemd=iname + '.model.tt1',
                       mode='evalexpr', expr='IM0 * (1 - IM1)')

                # insert the modified model into the MS
                os.system('rm -rf ' + iname + '.model.tt*.save')
                os.system('mv ' + iname + '.model.tt0 ' + \
                          iname + '.model.tt0.save')
                os.system('mv ' + iname + '.model.tt1 ' + \
                          iname + '.model.tt1.save')
                tclean(vis=sname + '.ms', imagename=iname, selectdata=True,
                       datacolumn='data', specmode='mfs', gridder='standard',
                       deconvolver='mtmfs', scales=[0], pblimit=-0.1, nterms=2,
                       weighting='briggs', robust=2.0, cell=cell, niter=0,
                       imsize=int(imscl * imsize), interactive=False, 
                       startmodel=[iname + '.model.tt0.target-masked',
                                   iname + '.model.tt1.target-masked'], 
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
                iname = peel_dir + 'images/' + targs[it] + '.' + band + \
                        '-sub' + str(isub).zfill(2) + '.targ_only'
                for ext in exts: os.system('rm -rf ' + iname + ext)
                tclean(vis=sname + '.targ_only.ms', imagename=iname, 
                       selectdata=True, datacolumn='data', specmode='mfs', 
                       gridder='standard', deconvolver='mtmfs', scales=[0], 
                       pblimit=-0.1, nterms=2, weighting='briggs', robust=2.0, 
                       imsize=int(imscl * imsize), cell=cell, niter=100000, 
                       nsigma=1.0, interactive=False, usemask='user', 
                       mask=tmask, threshold=RMS_str, savemodel='modelcolumn')



            ### Post-peel, full-band imaging 
            # concatenate peeled MSs and export the data to preferred format
            pref = peel_dir + targs[it] + '.' + band + '-sub'
            suff = '.targ_only.ms'
            snms = [pref + str(j).zfill(2) + suff for j in range(len(subs))]
            fname = peel_dir + targs[it] + '.' + band + '-full.targ_only'
            os.system('rm -rf ' + fname + '.ms')
            concat(vis=snms, concatvis=fname + '.ms', 
                   dirtol='0.1arcsec', freqtol='50Hz', copypointing=False)
            oname = out_dir + targs[it] + '.' + band + '_' + EB[i] + '.full'
            os.system('rm -rf ' + oname + '.vis.npz')
            export_vis(fname + '.ms', oname + '.vis.npz')

            # image the concatenated peeled MS
            print('Imaging the concatenated, peeled (target-only) dataset...')
            iname = peel_dir + 'images/' + targs[it] + '.' + band + \
                    '-full.targ_only'
            for ext in exts: os.system('rm -rf ' + iname + ext)
            tclean(vis=fname + '.ms', imagename=iname, selectdata=True, 
                   datacolumn='data', specmode='mfs', gridder='standard', 
                   deconvolver='mtmfs', scales=[0], pblimit=-0.1, nterms=2, 
                   weighting='briggs', robust=2.0, imsize=int(imscl * imsize), 
                   cell=cell, interactive=False, niter=100000, nsigma=1.0, 
                   usemask='user', mask=tmask, threshold=RMS_str, pbmask=0.0, 
                   savemodel='none')
