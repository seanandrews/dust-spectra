import os
import sys
import numpy as np
from casatools import msmetadata
from pathlib import Path
import glob
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')



# User specifies band, time-averging bin, sub-bands, and, optionally, 
# specific EB and specific target
band = 'X'
timebin = '30s'
subbands = ['0~7', '8~15', '16~23', '24~31']
s_EB = '01_1'
s_targ = 'CWTau'



# -------------------------------------

# I/O paths
proc_dir = '/d4/asha1/dust-spectra/DR/VLA/'
msout_dir = '/data/sandrews/VLA_LP/final_data/'
visout_dir = '/data/sandrews/VLA_LP/fluxes/vis_data/'


# list of image extensions (useful for cleanup)
exts = ['.image', '.mask', '.model', '.pb', '.psf', '.residual',
        '.sumwt', '.*.tt*', '.alpha', '.alpha.error', '.beta', '.beta.error']


# retrieve full list of pipelined datafiles and identifiers for this band
EB, pipe_ms = np.loadtxt('files_VLA_' + band + '.txt', dtype=str).T


# if desired, select a specific EB to process; grab the program identifiers
if s_EB is not None:
    pipe_ms = pipe_ms[EB == s_EB]
    EB = EB[EB == s_EB]
EB = [band + item + '/' for item in EB]
prog = [item.split('.')[0] + '/' for item in pipe_ms]



### loop over EBs
for i in range(len(EB)):

    print(f"----------------------------\nPeel processing execution {EB[i]}")


    # identify the available targets and reduced ms filenames
    EB_dir = proc_dir + prog[i] + EB[i]
    ms = [f.name for f in Path(EB_dir).glob('*.reduced.ms')]
    targs = [f.split('.' + band + '.reduced.ms', 1)[0] for f in ms]
    msfiles = [proc_dir + EB[i] + f for f in ms]


    # select an individual target if specified
    if s_targ is not None:
        if s_targ in targs:
            tix = targs.index(s_targ)
            msfiles = [msfiles[tix]]
            targs = [targs[tix]]
        else:
            print('\n    s_targ not in the target list for this EB.  exiting.')
            sys.exit()


    # check for the peel / imaging paths for this execution block
    peel_dir = EB_dir + 'peel/'
    pimg_dir = peel_dir + 'images/'
    if not os.path.exists(peel_dir):
        os.system('mkdir ' + peel_dir)
    if not os.path.exists(pimg_dir):
        os.system('mkdir ' + pimg_dir)



    ### loop over targets
    for it in range(len(targs)):

        print(f"\n    Processing data for {targs[it]} from {EB[i]} ....")


        # a handy filename prefix
        pref = targs[it] + '.' + band


        # time-averaging the self-calibrated dataset
        print('\n        time-averaging to reduce dataset volume ....')
        visa = peel_dir + pref + '.selfcal.tavg'
        os.system('rm -rf ' + visa + '.ms*')
        mstransform(vis=EB_dir + pref + '.selfcal.ms', outputvis=visa + '.ms',
                    datacolumn='data', timeaverage=True, timebin=timebin)


        # store this time-averaged dataset in secure location
        os.system('cp -r ' + visa + '.ms ' + \
                  msout_dir + targs[it] + '.' + EB[i][:-1] + '.selfcal.ms')


        # get imaging / self-cal information from the target dictionary
        src = td[targs[it]]
        idict = src[band][EB[i][:-1]]


        # set some defaults for non-specified parameters
        nt = 5 if 'nt' not in idict else idict['nt']
        lnt = 2 if 'lnt' not in idict else idict['lnt']
        imscl = 1 if 'imscl' not in idict else idict['imscl']
        nterms = 2 if 'nterms' not in idict else idict['nterms']
        if 'mask' in idict:
            usemask = 'user'
            mask = idict['mask']
        else:
            usemask = 'auto-multithresh'
            mask = ''
        pblim = -0.1


        # get some useful imaging parameters from the datafile
        cell, imsize, est_beam, nu_, pb = imparamcalc(msfiles[it], D_ant=25.)
        imsize = int(imscl * imsize)


        # full-band imaging: identify peel targets (direct user, or automask)
        print('\n        preliminary full-band imaging to ' + \
              'identify peel targets ....')
        iname = pimg_dir + pref + '.selfcal.tavg'
        for ext in exts: os.system('rm -rf ' + iname + ext)
        tclean(vis=visa + '.ms', imagename=iname, datacolumn='data',
               deconvolver='mtmfs', scales=[0], pblimit=pblim,
               nterms=nterms, weighting='briggs', robust=2.0,
               imsize=imsize, cell=cell, niter=100000, nsigma=1.0,
               pbmask=0, interactive=False, usemask=usemask, mask=mask,
               noisethreshold=nt, lownoisethreshold=lnt, cutthreshold=0.05, 
               sidelobethreshold=2.0, minbeamfrac=0.1, savemodel='none')
        pmask = iname + '.mask'


        # generate a target mask (accounting for source proper motion)
        ms = casatools.ms()
        ms.open(visa + '.ms')
        tstart = ms.getdata(['time'])['time'][0]
        ms.close()
        dt_epoch = mjd_to_decimal_year(tstart) - 2000.

        mrr = str(round(est_beam * 4, 1)) + 'arcsec'
        if isinstance(src['RA'], list):
            t_mask = []
            for ic in range(len(src['RA'])):
                mxx, myy = pm_corr(dt_epoch, src['RA'][ic], src['DEC'][ic],
                                   src['mua'][ic], src['mud'][ic])
                t_mask += ["circle[[" + mxx + ", " + myy + "], " + mrr + "]"]
        else:
            mxx, myy = pm_corr(dt_epoch, src['RA'], src['DEC'],
                               src['mua'], src['mud'])
            t_mask = "circle[[" + mxx + ", " + myy + "], " + mrr + "]"

        targ_mask = pimg_dir + pref + '.targ.mask'
        os.system('rm -rf ' + targ_mask + '*')
        makemask(mode='copy', inpimage=iname + '.image.tt0', inpmask=t_mask,
                 output=targ_mask)


        # loop over sub-bands
        os.system('rm -rf ' + peel_dir + pref + '-sub*')
        for isub in range(len(subbands)):

            # split out the sub-band SPWs
            sname = peel_dir + pref + '-sub' + str(isub).zfill(2)
            mstransform(vis=visa + '.ms', outputvis=sname + '.ms',
                        datacolumn='data', spw=subbands[isub])

           
            # image the sub-band to generate a clean model in the peel mask
            print('\n            imaging with peel mask for sub-band ' + \
                  band + '-sub' + str(isub).zfill(2) + ' ....')
            iname = pimg_dir + pref + '-sub' + str(isub).zfill(2) + '.peel'
            for ext in exts: os.system('rm -rf ' + iname + ext)
            tclean(vis=sname + '.ms', imagename=iname, datacolumn='data',
                   deconvolver='mtmfs', scales=[0], pblimit=pblim, nterms=2, 
                   weighting='briggs', robust=2.0, imsize=imsize, cell=cell, 
                   niter=100000, nsigma=1.0, pbmask=0, interactive=False, 
                   usemask='user', mask=pmask, savemodel='modelcolumn')


            # remove contributions from the target(s) in the clean model
            os.system('rm -rf ' + iname + '.model.tt0.target-masked')
            immath(imagename=[iname + '.model.tt0', targ_mask],
                   outfile=iname + '.model.tt0.target-masked',
                   imagemd=iname + '.model.tt0',
                   mode='evalexpr', expr='IM0 * (1 - IM1)')

            os.system('rm -rf ' + iname + '.model.tt1.target-masked')
            immath(imagename=[iname + '.model.tt1', targ_mask],
                   outfile=iname + '.model.tt1.target-masked',
                   imagemd=iname + '.model.tt1',
                   mode='evalexpr', expr='IM0 * (1 - IM1)')


            # insert the modified model into the MS
            os.system('rm -rf ' + iname + '.model.tt*.save')
            os.system('mv ' + iname + '.model.tt0 ' + \
                      iname + '.model.tt0.save')
            os.system('mv ' + iname + '.model.tt1 ' + \
                      iname + '.model.tt1.save')
            tclean(vis=sname + '.ms', imagename=iname, datacolumn='data', 
                   deconvolver='mtmfs', scales=[0], pblimit=pblim, nterms=2,
                   weighting='briggs', robust=2.0, imsize=imsize, cell=cell, 
                   niter=0, interactive=False,
                   startmodel=[iname + '.model.tt0.target-masked',
                               iname + '.model.tt1.target-masked'],
                   savemodel='modelcolumn')


            # subtract the masked model and split out the peeled dataset
            uvsub(vis=sname + '.ms')
            os.system('rm -rf ' + sname + '.targ_only.ms')
            mstransform(vis=sname + '.ms', outputvis=sname + '.targ_only.ms',
                        datacolumn='corrected')


            # image the peeled, target-only, sub-band measurement set
            print('\n            imaging with target mask for peeled ' + \
                  'sub-band ' + band + '-sub' + str(isub).zfill(2) + ' ....')
            iname = pimg_dir + pref + '-sub' + str(isub).zfill(2) + \
                    '.targ_only'
            for ext in exts: os.system('rm -rf ' + iname + ext)
            tclean(vis=sname + '.targ_only.ms', imagename=iname,
                   datacolumn='data', deconvolver='mtmfs', scales=[0],
                   pblimit=pblim, nterms=2, weighting='briggs', robust=2.0,
                   imsize=imsize, cell=cell, niter=100000, nsigma=1.0, 
                   interactive=False, usemask='user', mask=targ_mask,
                   pbmask=0, savemodel='modelcolumn')



        ### post-peel, full-band imaging 

        # concatenate peeled sub-band data into composite file
        print('\n        combining peeled datasets ....')
        pre, suff = peel_dir + pref + '-sub', '.targ_only.ms'
        snms = [pre + str(j).zfill(2) + suff for j in range(len(subbands))]
        fname = peel_dir + pref + '-full.targ_only'
        os.system('rm -rf ' + fname + '.ms')
        concat(vis=snms, concatvis=fname + '.ms',
               dirtol='0.1arcsec', freqtol='50Hz', copypointing=False)


        # store a copy of the concatenated file in a secure location
        oname = msout_dir + targs[it] + '.' + EB[i][:-1] + '.peeled'
        os.system('rm -rf ' + oname + '.ms')
        os.system('cp -r ' + fname + '.ms ' + oname + '.ms')


        # export the peeled visibilities in usable format
        vname = visout_dir + targs[it] + '.' + EB[i][:-1] + '.peeled'
        os.system('rm -rf ' + vname + '.vis.npz')
        export_vis(oname + '.ms', vname + '.vis.npz')


        # image the concatenated peeled MS
        print('\n        imaging the concatenated, peeled dataset ....')
        iname = pimg_dir + pref + '-full.targ_only'
        for ext in exts: os.system('rm -rf ' + iname + ext)
        tclean(vis=fname + '.ms', imagename=iname, datacolumn='data', 
               deconvolver='mtmfs', scales=[0], pblimit=pblim, nterms=nterms,
               weighting='briggs', robust=2.0, imsize=imsize, cell=cell, 
               interactive=False, niter=100000, nsigma=1.0, usemask='user', 
               mask=targ_mask, pbmask=0, savemodel='none')
