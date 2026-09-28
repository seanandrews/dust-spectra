import os
import sys
from pathlib import Path
import glob
import numpy as np
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')



# observing band and execution blocks
band = 'B1'
EB = ['01_1', '01_2', '02_1', '02_2', '02_3', '02_4', '03_1', '04_1', '05_1',
      '06_1', '07_1', '08_1', '09_1', '10_1', '11_1']
EB = [band + '_' + item + '/' for item in EB]



### Basic definitions
# paths
proc_dir = '/d4/asha1/dust-spectra/DR/ALMA/'
exts = ['.image', '.mask', '.model', '.pb', '.psf', '.residual',
        '.sumwt', '.*.tt*', '.alpha', '.alpha.error', '.beta', '.beta.error']

Nspw = 4


# loop over execution blocks
for i in [14]:
    print(f"--------------------------------------------------")
    print(f"Processing dataset {i:02d} for execution {EB[i]}...")

    # identify the available targets and reduced MS filenames
    EB_dir = proc_dir + EB[i]
    ms = [f.name for f in Path(EB_dir).glob('*.' + band + '.reduced.ms')]
    targs = [f.split('.' + band + '.reduced.ms', 1)[0] for f in ms]
    msfiles = [proc_dir + EB[i] + f for f in ms]
    print(targs)



    # check for the self-cal / imaging paths for this execution block
    self_dir = EB_dir + 'selfcal/'
    simg_dir = self_dir + 'images/'
    if not os.path.exists(self_dir):
        os.system('mkdir ' + self_dir)
    if not os.path.exists(simg_dir):
        os.system('mkdir ' + simg_dir)

    # loop over targets
    for it in [14]: #, 9, 11]: #range(len(targs)):
        print(f"\nProcessing data for {targs[it]} from execution {EB[i]}...")

        # get imaging / self-cal information from dictionary
        src = td[targs[it]]
        idict = src[band][EB[i][:-1]]

        # get some useful imaging parameters
        cell, imsize, est_beam, nu_, pb = imparamcalc(msfiles[it], D_ant=12.)
        nt, lnt, imscl = idict['nt'], idict['lnt'], idict['imscl']
        if 'pblim' in idict:
            pblim = idict['pblim']
        else: pblim = -0.1


        # copy the init MS into the cont_p0 MS for further use
        cont_p0 = self_dir + targs[it] + '.' + band + '.cont_p0.ms'
        os.system('rm -rf ' + cont_p0)
        os.system('cp -r ' + msfiles[it] + ' ' + cont_p0)

        # make a clean mask (can add background sources with automask)
        ms = casatools.ms()
        ms.open(cont_p0)
        tstart_MS = ms.getdata(['time'])['time'][0]
        ms.close()
        dt_epoch = mjd_to_decimal_year(tstart_MS) - 2000.

        mrr = str(np.max([round(est_beam * 3, 1), 3.0])) + 'arcsec'
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


        ### IMAGING AND SELF-CALIBRATION
        if idict['selfcal']:
            # retrieve / define some parameters
            if 'psolint' in idict:
                p_solint = idict['psolint']
            else: p_solint = ['inf']
            if 'asolint' in idict:
                a_solint = idict['asolint']
            else: a_solint = ['inf']
            if 'pminsnr' in idict:
                p_minsnr = idict['pminsnr']
            else: p_minsnr = 3.0
            if 'aminsnr' in idict:
                a_minsnr = idict['aminsnr']
            else: a_minsnr = 3.0
            if 'sc_nt' in idict:
                sc_nt = idict['sc_nt']
            else: sc_nt = nt
            if 'sc_lnt' in idict:
                sc_lnt = idict['sc_lnt']
            else: sc_lnt = lnt
            if 'selfcal_mode' in idict:
                selfcal_mode = idict['selfcal_mode']
            else: selfcal_mode = 'MTMFS'
            if 'nterms' in idict:
                nterms = idict['nterms']
            else: nterms = 2

            # a handy filename prefix
            pref = targs[it] + '.' + band


            ### Preliminary full-band imaging (used for model in MTMFS mode or
            ### mask for PER-SPW mode)
            print('\nPRELIMINARY IMAGING FOR SELF-CAL MODEL...')
            pre_name = simg_dir + pref + '.cont_p0'
            for ext in exts: os.system('rm -rf ' + pre_name + ext)

            # shallow clean around target (to ensure it is masked)
            tclean(vis=cont_p0, imagename=pre_name, selectdata=True,
                   datacolumn='data', specmode='mfs', gridder='standard',
                   deconvolver='mtmfs', scales=[0], pblimit=pblim,
                   nterms=2, weighting='briggs', robust=2.0,
                   imsize=int(imscl * imsize), cell=cell, niter=100,
                   nsigma=1.0, interactive=False, usemask='user', mask=imask,
                   pbmask=0., savemodel='modelcolumn')

            # deeper clean + add automask for background sources
            tclean(vis=cont_p0, imagename=pre_name, selectdata=True,
                   datacolumn='data', specmode='mfs', gridder='standard',
                   deconvolver='mtmfs', scales=[0], pblimit=pblim,
                   nterms=2, weighting='briggs', robust=2.0,
                   imsize=int(imscl * imsize), cell=cell, niter=100000,
                   nsigma=1.0, interactive=False, usemask='auto-multithresh',
                   cutthreshold=0.05, noisethreshold=sc_nt, 
                   lownoisethreshold=sc_lnt, smoothfactor=1.0, 
                   sidelobethreshold=2.0, minbeamfrac=0.1,
                   pbmask=0., restart=True, savemodel='modelcolumn')



            ### SELF-CAL using images in each SPW
            if selfcal_mode == 'PER-SPW':
                iname = simg_dir + targs[it] + '.' + band + '.cont_p0'
                for ispw in range(Nspw):
                    # Image-based model *per SPW*, using full-band pre_mask
                    sspw = str(ispw).zfill(2)
                    print('INITIAL IMAGING FOR SELF-CAL: SPW ' + sspw + '...')
                    tclean(vis=cont_p0, imagename=iname + '-spw' + sspw,
                           selectdata=True, datacolumn='data', specmode='mfs',
                           spw=str(ispw), gridder='standard',
                           deconvolver='mtmfs', scales=[0], pblimit=p_pblim,
                           nterms=1, weighting='briggs', robust=2.0,
                           imsize=int(imscl * imsize), cell=cell, niter=100000,
                           nsigma=1.0, interactive=False, usemask='user',
                           mask=pre_name + '.mask', savemodel='modelcolumn')

                # remove previous self-cal iteration files for tidiness
                os.system('rm -rf ' + self_dir + pref + '-spw*' + '.p*')
                os.system('rm -rf ' + self_dir + pref + '-spw*' + '.a*')
                for isc in range(1,3):
                    ssc = str(isc)
                    ms_f = self_dir + pref + '-spw*' + '.cont_p' + ssc + '*.ms'
                    os.system('rm -rf ' + ms_f)
                    im_f = simg_dir + pref + '-spw*' + '.cont_p' + ssc + '*'
                    os.system('rm -rf ' + im_f)
                    ms_f = self_dir + pref + '-spw*' + '.cont_a' + ssc + '*.ms'
                    os.system('rm -rf ' + ms_f)
                    im_f = simg_dir + pref + '-spw*' + '.cont_a' + ssc + '*'
                    os.system('rm -rf ' + im_f)

                """ PHA - only self-calibration iterations """
                for ip in range(len(p_solint)):
                    print('\n...PHASE SELF-CAL iteration ' + str(ip+1) + \
                          ': solint=' + p_solint[ip] + '...')

                    # prepare for SPW loop
                    if p_solint[ip] == 'all':
                        gcombine = 'scan'
                        p_solint[ip] = 'inf'
                    else: gcombine = ''
                    visi = self_dir + pref + '.cont_p' + str(ip)

                    # iterate gain cal over SPW to build CORRECTED MS column
                    for ispw in range(Nspw):
                        # gain table file
                        cal_p = self_dir + pref + '-spw' + \
                                str(ispw).zfill(2) + '.p' + str(ip+1)

                        # calculate the gain solutions
                        gaincal(vis=visi + '.ms', caltable=cal_p, calmode='p',
                                solint=p_solint[ip], minsnr=p_minsnr, 
                                combine=gcombine, spw=str(ispw), gaintype='G')

                        # apply the gain solutions
                        applycal(vis=visi + '.ms', gaintable=cal_p, 
                                 spw=str(ispw), applymode='calonly', 
                                 calwt=False)

                    # split off the gain-corrected MS
                    viso = self_dir + pref + '.cont_p' + str(ip+1)
                    os.system('rm -rf ' + viso + '.ms*')
                    mstransform(vis=visi + '.ms', outputvis=viso + '.ms', 
                                datacolumn='corrected')

                    # image the results
                    for ispw in range(Nspw):
                        iname = simg_dir + pref + '.cont_p' + str(ip+1) + \
                                '-spw' + str(ispw).zfill(2)
                        for ext in exts: os.system('rm -rf ' + iname + ext)
                        tclean(vis=viso + '.ms', imagename=iname,
                               selectdata=True, datacolumn='data', 
                               specmode='mfs', spw=str(ispw), 
                               gridder='standard', deconvolver='mtmfs', 
                               scales=[0], pblimit=p_pblim, nterms=1, 
                               weighting='briggs', robust=2.0,
                               imsize=int(imscl * imsize), cell=cell, 
                               niter=100000, nsigma=1.0, interactive=False, 
                               usemask='user', mask=pre_name + '.mask', 
                               savemodel='modelcolumn')


                """ AMP + PHA self-calibration iterations """
                if len(a_solint) > 0:
                    os.system('rm -rf ' + self_dir + pref + '.cont_a0.ms*')
                    os.system('cp -r ' + self_dir + pref + '.cont_p' + \
                              str(len(p_solint)) + '.ms ' + self_dir + pref + \
                              '.cont_a0.ms')

                for ia in range(len(a_solint)):
                    print('\n...AMPLITUDE + PHASE SELF-CAL iteration ' + \
                          str(ia+1) + ': solint=' + a_solint[ia] + '...')

                    # prepare for SPW loop
                    if a_solint[ia] == 'all':
                        gcombine = 'scan'
                        a_solint[ia] = 'inf'
                    else: gcombine = ''
                    visi = self_dir + pref + '.cont_a' + str(ia)

                    # iterate gain cal over SPW to build CORRECTED MS column
                    for ispw in range(Nspw):
                        # gain table file
                        cal_a = self_dir + pref + '-spw' + \
                                str(ispw).zfill(2) + '.a' + str(ia+1)

                        # calculate the gain solutions
                        gaincal(vis=visi + '.ms', caltable=cal_a, calmode='ap',
                                solint=a_solint[ia], minsnr=a_minsnr,
                                combine=gcombine, spw=str(ispw), gaintype='G')

                        # apply the gain solutions
                        applycal(vis=visi + '.ms', gaintable=cal_a,
                                 spw=str(ispw), applymode='calonly',
                                 calwt=True)

                    # split off the gain-corrected MS
                    viso = self_dir + pref + '.cont_a' + str(ia+1)
                    os.system('rm -rf ' + viso + '.ms*')
                    mstransform(vis=visi + '.ms', outputvis=viso + '.ms',
                                datacolumn='corrected')

                    # image the results
                    for ispw in range(Nspw):
                        iname = simg_dir + pref + '.cont_a' + str(ia+1) + \
                                '-spw' + str(ispw).zfill(2)
                        for ext in exts: os.system('rm -rf ' + iname + ext)
                        tclean(vis=viso + '.ms', imagename=iname,
                               selectdata=True, datacolumn='data',
                               specmode='mfs', spw=str(ispw),
                               gridder='standard', deconvolver='mtmfs',
                               scales=[0], pblimit=p_pblim, nterms=1,
                               weighting='briggs', robust=2.0,
                               imsize=int(imscl * imsize), cell=cell,
                               niter=100000, nsigma=1.0, interactive=False,
                               usemask='user', mask=pre_name + '.mask',
                               savemodel='modelcolumn')


            ### SELF-CAL using MTMFS images
            elif selfcal_mode == 'MTMFS':
                # remove previous self-cal iteration files for tidiness
                os.system('rm -rf ' + self_dir + pref + '.p*')
                os.system('rm -rf ' + self_dir + pref + '.a*')
                for isc in range(1,4):
                    ms_f = self_dir + pref + '.cont_p' + str(isc) + '*.ms'
                    os.system('rm -rf ' + ms_f)
                    im_f = simg_dir + pref + '.cont_p' + str(isc) + '*'
                    os.system('rm -rf ' + im_f)
                    ms_f = self_dir + pref + '.cont_a' + str(isc) + '*.ms'
                    os.system('rm -rf ' + ms_f)
                    im_f = simg_dir + pref + '.cont_a' + str(isc) + '*'
                    os.system('rm -rf ' + im_f)

                """ PHA - only self-calibration iterations """
                for ip in range(len(p_solint)):
                    print('\n...PHASE SELF-CAL iteration ' + str(ip+1) + \
                          ': solint=' + p_solint[ip] + '...')

                    # calculate the gain solutions
                    cal_p = self_dir + pref + '.p' + str(ip+1)
                    os.system('rm -rf ' + cal_p)
                    visi = self_dir + pref + '.cont_p' + str(ip)
                    gaincal(vis=visi + '.ms', caltable=cal_p, gaintype='G', 
                            calmode='p', combine='spw', 
                            solint=p_solint[ip], minsnr=p_minsnr)

                    # apply the gain solutions
                    applycal(vis=visi + '.ms', gaintable=cal_p, spw='', 
                             spwmap=[Nspw*[0]], interp=['nearest,linearpd'], 
                             calwt=False, applymode='calonly')

                    # split off the gain-corrected MS
                    viso = self_dir + pref + '.cont_p' + str(ip+1)
                    os.system('rm -rf ' + viso + '.ms*')
                    mstransform(vis=visi + '.ms', outputvis=viso + '.ms', 
                                datacolumn='corrected')

                    # image the results
                    iname = simg_dir + pref + '.cont_p' + str(ip+1)
                    for ext in exts: os.system('rm -rf ' + iname + ext)

                    # shallow clean around target (to ensure it is masked)
                    tclean(vis=viso + '.ms', imagename=iname, selectdata=True,
                           datacolumn='data', specmode='mfs', 
                           gridder='standard', deconvolver='mtmfs', scales=[0], 
                           pblimit=pblim, nterms=nterms, weighting='briggs', 
                           robust=2.0, imsize=int(imscl * imsize), cell=cell, 
                           niter=100, nsigma=1.0, interactive=False, 
                           usemask='user', mask=imask, pbmask=0., 
                           savemodel='modelcolumn')

                    # deeper clean + add automask for background sources
                    tclean(vis=viso + '.ms', imagename=iname, selectdata=True,
                           datacolumn='data', specmode='mfs', 
                           gridder='standard', deconvolver='mtmfs', scales=[0], 
                           pblimit=pblim, nterms=nterms, weighting='briggs', 
                           robust=2.0, imsize=int(imscl * imsize), cell=cell, 
                           niter=100000, nsigma=1.0, interactive=False, 
                           usemask='auto-multithresh', cutthreshold=0.05, 
                           noisethreshold=sc_nt, lownoisethreshold=sc_lnt,
                           smoothfactor=1.0, sidelobethreshold=2.0, 
                           minbeamfrac=0.1, pbmask=0., restart=True, 
                           savemodel='modelcolumn')


                """ AMP + PHA self-calibration iterations """
                if len(a_solint) > 0:
                    os.system('rm -rf ' + self_dir + pref + '.cont_a0.ms*')
                    os.system('cp -r ' + self_dir + pref + '.cont_p' + \
                              str(len(p_solint)) + '.ms ' + self_dir + pref + \
                              '.cont_a0.ms')

                for ia in range(len(a_solint)):
                    print('\n...AMPLITUDE + PHASE SELF-CAL iteration ' + \
                          str(ia+1) + ': solint=' + a_solint[ia] + '...')

                    # calculate the gain solutions
                    cal_a = self_dir + pref + '.a' + str(ia+1)
                    os.system('rm -rf ' + cal_a)
                    visi = self_dir + pref + '.cont_a' + str(ia)
                    gaincal(vis=visi + '.ms', caltable=cal_a, gaintype='G', 
                            calmode='ap', combine='spw', 
                            solint=a_solint[ia], minsnr=a_minsnr)

                    # apply the gain solutions
                    applycal(vis=visi + '.ms', gaintable=cal_a, spw='', 
                             spwmap=[Nspw*[0]], interp=['nearest,linearpd'], 
                             calwt=True, applymode='calonly')

                    # split off the gain-corrected MS
                    viso = self_dir + pref + '.cont_a' + str(ia+1)
                    os.system('rm -rf ' + viso + '.ms*')
                    mstransform(vis=visi + '.ms', outputvis=viso + '.ms', 
                                datacolumn='corrected')

                    # image
                    iname = simg_dir + pref + '.cont_a' + str(ia+1)
                    for ext in exts: os.system('rm -rf ' + iname + ext)

                    # shallow clean around target (to ensure it is masked)
                    tclean(vis=viso + '.ms', imagename=iname, selectdata=True,
                           datacolumn='data', specmode='mfs', 
                           gridder='standard', deconvolver='mtmfs', scales=[0],                            pblimit=pblim, nterms=nterms, weighting='briggs', 
                           robust=2.0, imsize=int(imscl * imsize), cell=cell, 
                           niter=100, nsigma=1.0, interactive=False, 
                           usemask='user', mask=imask, pbmask=0., 
                           savemodel='modelcolumn')

                    # deeper clean + add automask for background sources
                    tclean(vis=viso + '.ms', imagename=iname, selectdata=True,
                           datacolumn='data', specmode='mfs', 
                           gridder='standard', deconvolver='mtmfs', scales=[0],                            pblimit=pblim, nterms=nterms, weighting='briggs', 
                           robust=2.0, imsize=int(imscl * imsize), cell=cell, 
                           niter=100000, nsigma=1.0, interactive=False, 
                           usemask='auto-multithresh', cutthreshold=0.05, 
                           noisethreshold=sc_nt, lownoisethreshold=sc_lnt,
                           smoothfactor=1.0, sidelobethreshold=2.0, 
                           minbeamfrac=0.1, pbmask=0., restart=True, 
                           savemodel='modelcolumn')


                # copy the self-calibrated MS back up a layer
                selfcal_MS = EB_dir + targs[it] + '.' + band + '.selfcal.ms'
                os.system('rm -rf ' + selfcal_MS)
                os.system('cp -r ' + viso + '.ms ' + selfcal_MS)

            else:
                print('\n\n Do not recognize this selfcal_mode: STOP.')
                sys.exit()

            # copy the self-calibrated MS back up a layer
            selfcal_MS = EB_dir + targs[it] + '.' + band + '.selfcal.ms'
            os.system('rm -rf ' + selfcal_MS)
            os.system('cp -r ' + viso + '.ms ' + selfcal_MS)

        else:
            ### NO SELF-CALIBRATION: just make an image and copy the MS
            print('\nIMAGING: NO SELF-CAL...')
            pre_name = simg_dir + targs[it] + '.' + band + '.cont_p0'
            for ext in exts: os.system('rm -rf ' + pre_name + ext)

            # shallow clean around target (to ensure it is masked)
            tclean(vis=cont_p0, imagename=pre_name, selectdata=True,
                   datacolumn='data', specmode='mfs', gridder='standard',
                   deconvolver='mtmfs', scales=[0], pblimit=pblim,
                   nterms=2, weighting='briggs', robust=2.0,
                   imsize=int(imscl * imsize), cell=cell, niter=100,
                   nsigma=1.0, interactive=False, usemask='user', mask=imask,
                   pbmask=0., savemodel='modelcolumn')

            # deeper clean + add automask for background sources
            tclean(vis=cont_p0, imagename=pre_name, selectdata=True,
                   datacolumn='data', specmode='mfs', gridder='standard',
                   deconvolver='mtmfs', scales=[0], pblimit=pblim,
                   nterms=2, weighting='briggs', robust=2.0,
                   imsize=int(imscl * imsize), cell=cell, niter=100000,
                   nsigma=1.0, interactive=False, usemask='auto-multithresh',
                   cutthreshold=0.05, noisethreshold=nt, lownoisethreshold=lnt, 
                   smoothfactor=1.0, sidelobethreshold=2.0, minbeamfrac=0.1, 
                   pbmask=0., restart=True, savemodel='modelcolumn')

            selfcal_MS = EB_dir + targs[it] + '.' + band + '.selfcal.ms'
            os.system('rm -rf ' + selfcal_MS)
            os.system('cp -r ' + cont_p0 + ' ' + selfcal_MS)
