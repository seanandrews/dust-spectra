import os
import sys
import numpy as np
from casatools import msmetadata
from pathlib import Path
import glob
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')



# User specifies band and, optionally, specific EB and specific target
band = 'X'
s_EB = '10_1'
s_targ = None



# -------------------------------------

# I/O paths
proc_dir = '/d4/asha1/dust-spectra/DR/VLA/'


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

    print(f"----------------------------\nImage processing execution {EB[i]}")


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
    

    # check for the self-cal / imaging paths for this execution block
    self_dir = EB_dir + 'selfcal/'
    simg_dir = self_dir + 'images/'
    if not os.path.exists(self_dir):
        os.system('mkdir ' + self_dir)
    if not os.path.exists(simg_dir):
        os.system('mkdir ' + simg_dir)



    ### loop over targets
    for it in range(len(targs)):

        print(f"\n    Processing data for {targs[it]} from {EB[i]} ....")


        # get imaging / self-cal information from the target dictionary
        idict = td[targs[it]][band][EB[i][:-1]]


        # set some defaults for non-specified parameters
        nt = 5 if 'nt' not in idict else idict['nt']
        lnt = 2 if 'lnt' not in idict else idict['lnt']
        imscl = 1 if 'imscl' not in idict else idict['imscl']
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

       
        # find the number of SPWs
        ms = casatools.ms()
        ms.open(msfiles[it])
        spw_info = ms.getspectralwindowinfo()
        ms.close()
        Nspw = len(spw_info)


        # a handy filename prefix
        pref = targs[it] + '.' + band


        ### SELF-CALIBRATION if specified in target dictionary
        if idict['selfcal']:

            # remove any previous self-cal files for tidiness
            os.system('rm -rf ' + self_dir + pref + '*')
            os.system('rm -rf ' + simg_dir + pref + '*')


            # initialize datafile with a copy
            cont_p0 = self_dir + pref + '.cont_p0'
            os.system('rm -rf ' + cont_p0 + '.ms')
            os.system('cp -r ' + msfiles[it] + ' ' + cont_p0 + '.ms')


            # define or retrieve some selfcal parameters
            sc_mode = 'MTMFS' if 'sc_mode' not in idict else idict['sc_mode']
            nterms = 2 if 'nterms' not in idict else idict['nterms']
            sc_nt = 1. * nt if 'sc_nt' not in idict else idict['sc_nt']
            sc_lnt = 1. * lnt if 'sc_lnt' not in idict else idict['sc_lnt']

            p_solint = ['inf'] if 'psolint' not in idict else idict['psolint']
            p_minsnr = 3.0
            a_solint = [] if 'asolint' not in idict else idict['asolint']
            a_minsnr = 5.0


            # preliminary MTMFS imaging 
            # (gives model in MTMFS mode or mask for PER-SPW mode)
            print('\n        preliminary imaging for self-cal model ....')
            pre_name = simg_dir + pref + '.cont_p0'
            for ext in exts: os.system('rm -rf ' + pre_name + ext)
            tclean(vis=cont_p0 + '.ms', imagename=pre_name, datacolumn='data', 
                   deconvolver='mtmfs', scales=[0], pblimit=pblim, 
                   nterms=nterms, weighting='briggs', robust=2.0, 
                   imsize=imsize, cell=cell, niter=100000, nsigma=1.0,
                   pbmask=0, interactive=False, usemask=usemask, mask=mask, 
                   noisethreshold=sc_nt, lownoisethreshold=sc_lnt,
                   cutthreshold=0.05, sidelobethreshold=2.0, minbeamfrac=0.1,
                   savemodel='modelcolumn')
            estimate_SNR(pre_name)



            ### SELF-CAL using models in each individual SPW
            if sc_mode == 'PER-SPW':

                print('\n      > PER-SPW self-calibration:')
                print('\n        imaging for initial model ....')


                # set the image-based model per SPW, using full-band pre_mask
                iname = simg_dir + pref + '.cont_p0'
                for ispw in range(Nspw):

                    # SPW identifier for tracking
                    sspw = str(ispw).zfill(2)
                    print('\n            init image for SPW ' + sspw + ' ....')

                    # make an initial clean model for each SPW
                    tclean(vis=cont_p0 + '.ms', 
                           imagename=iname + '-spw' + sspw, datacolumn='data', 
                           spw=str(ispw), deconvolver='mtmfs', scales=[0], 
                           nterms=1, weighting='briggs', robust=2.0,
                           pblimit=pblim, pbmask=0, imsize=imsize, cell=cell, 
                           niter=100000, nsigma=1.0, interactive=False, 
                           usemask='user', mask=pre_name + '.mask', 
                           savemodel='modelcolumn')


                # PHASE self-cal iterations
                for ip in range(len(p_solint)):

                    print('\n        PHASE self-cal iteration ' + str(ip+1) + \
                          ': solint=' + p_solint[ip] + ' ....')


                    # prepare for SPW loop
                    if p_solint[ip] == 'all':
                        gcombine = 'scan'
                        p_solint[ip] = 'inf'
                    else: gcombine = ''
                    visi = self_dir + pref + '.cont_p' + str(ip)


                    # iterate over SPW to build complete CORRECTED column
                    for ispw in range(Nspw):

                        # gain table file
                        cal_p = self_dir + pref + '-spw' + \
                                str(ispw).zfill(2) + '.p' + str(ip+1)

                        # calculate gain solutions
                        gaincal(vis=visi + '.ms', caltable=cal_p, calmode='p',
                                solint=p_solint[ip], minsnr=p_minsnr, 
                                combine=gcombine, spw=str(ispw), gaintype='G')

                        # apply gain solutions
                        applycal(vis=visi + '.ms', gaintable=cal_p, 
                                 spw=str(ispw), applymode='calonly', 
                                 calwt=False)


                    # split off the gain-corrected measurement set
                    viso = self_dir + pref + '.cont_p' + str(ip+1)
                    os.system('rm -rf ' + viso + '.ms*')
                    mstransform(vis=visi + '.ms', outputvis=viso + '.ms', 
                                datacolumn='corrected')


                    # image the results
                    for ispw in range(Nspw):
                        sspw = str(ispw).zfill(2)
                        print('\n            post PHASE self-cal ' + \
                              'iteration ' + str(ip+1) + ' image for SPW ' + \
                              sspw + ' ....')
                        
                        # identifier and cleanup
                        iname = simg_dir + pref + '.cont_p' + str(ip+1) + \
                                '-spw' + str(ispw).zfill(2)
                        for ext in exts: os.system('rm -rf ' + iname + ext)

                        # make the revised clean model for each SPW
                        tclean(vis=viso + '.ms', imagename=iname,
                               datacolumn='data', spw=str(ispw), 
                               deconvolver='mtmfs', scales=[0], nterms=1,
                               weighting='briggs', robust=2.0, pblimit=pblim, 
                               pbmask=0, imsize=imsize, cell=cell, 
                               niter=100000, nsigma=1.0, interactive=False, 
                               usemask='user', mask=pre_name + '.mask', 
                               savemodel='modelcolumn')


                    # MTMFS image of the PER-SPW self-calibrated dataset
                    iname = simg_dir + pref + '.cont_p' + str(ip+1)
                    for ext in exts: os.system('rm -rf ' + iname + ext)
                    print('\n            MTMFS image for cont_p' + \
                          str(ip+1)+ ' ....')
                    tclean(vis=viso + '.ms', imagename=iname, 
                           datacolumn='data', deconvolver='mtmfs', scales=[0], 
                           nterms=nterms, weighting='briggs', robust=2.0, 
                           pblimit=pblim, pbmask=0, imsize=imsize, cell=cell, 
                           niter=100000, nsigma=1.0, interactive=False, 
                           usemask=usemask, mask=mask, noisethreshold=sc_nt, 
                           lownoisethreshold=sc_lnt, cutthreshold=0.05, 
                           sidelobethreshold=2.0, minbeamfrac=0.1,
                           savemodel='none')
                    estimate_SNR(iname)



                # if performing amplitude self-cal, copy over datafile
                if len(a_solint) > 0:
                    os.system('rm -rf ' + self_dir + pref + '.cont_a0.ms*')
                    os.system('cp -r ' + self_dir + pref + '.cont_p' + \
                              str(len(p_solint)) + '.ms ' + \
                              self_dir + pref + '.cont_a0.ms')


                # AMPLITUDE + PHASE self-cal iterations
                for ia in range(len(a_solint)):

                    print('\n        AMPLITUDE + PHASE self-cal iteration ' + \
                          str(ia+1) + ': solint=' + a_solint[ia] + ' ....')


                    # prepare for SPW loop
                    if a_solint[ia] == 'all':
                        gcombine = 'scan'
                        a_solint[ia] = 'inf'
                    else: gcombine = ''
                    visi = self_dir + pref + '.cont_a' + str(ia)


                    # iterate over SPW to build complete CORRECTED column
                    for ispw in range(Nspw):

                        # gain table file
                        cal_a = self_dir + pref + '-spw' + \
                                str(ispw).zfill(2) + '.a' + str(ia+1)

                        # calculate gain solutions
                        gaincal(vis=visi + '.ms', caltable=cal_a, calmode='ap',
                                solint=a_solint[ia], minsnr=a_minsnr,
                                combine=gcombine, spw=str(ispw), 
                                solnorm=True, gaintype='G')

                        # apply gain solutions
                        applycal(vis=visi + '.ms', gaintable=cal_a,
                                 spw=str(ispw), applymode='calonly',
                                 calwt=True)


                    # split off the gain-corrected measurement set
                    viso = self_dir + pref + '.cont_a' + str(ia+1)
                    os.system('rm -rf ' + viso + '.ms*')
                    mstransform(vis=visi + '.ms', outputvis=viso + '.ms',
                                datacolumn='corrected')


                    # image the results
                    for ispw in range(Nspw):
                        sspw = str(ispw).zfill(2)
                        print('\n            post AMPLITUDE + PHASE ' + \
                              'self-cal iteration ' + str(ia+1) + \
                              ' image for SPW ' + sspw + ' ....')

                        # identifier and cleanup
                        iname = simg_dir + pref + '.cont_a' + str(ia+1) + \
                                '-spw' + str(ispw).zfill(2)
                        for ext in exts: os.system('rm -rf ' + iname + ext)

                        # make the revised clean model for each SPW
                        tclean(vis=viso + '.ms', imagename=iname,
                               datacolumn='data', spw=str(ispw),
                               deconvolver='mtmfs', scales=[0], nterms=1,
                               weighting='briggs', robust=2.0, pblimit=pblim,
                               pbmask=0, imsize=imsize, cell=cell, 
                               niter=100000, nsigma=1.0, interactive=False, 
                               usemask='user', mask=pre_name + '.mask',
                               savemodel='modelcolumn')


                    # MTMFS image of the PER-SPW self-calibrated dataset
                    iname = simg_dir + pref + '.cont_a' + str(ia+1)
                    for ext in exts: os.system('rm -rf ' + iname + ext)
                    print('\n            MTMFS image for cont_a' + \
                          str(ia+1)+ ' ....')
                    tclean(vis=viso + '.ms', imagename=iname,
                           datacolumn='data', deconvolver='mtmfs', scales=[0],
                           nterms=nterms, weighting='briggs', robust=2.0,
                           pblimit=pblim, pbmask=0, imsize=imsize, cell=cell,
                           niter=100000, nsigma=1.0, interactive=False,
                           usemask=usemask, mask=mask, noisethreshold=sc_nt, 
                           lownoisethreshold=sc_lnt, cutthreshold=0.05, 
                           sidelobethreshold=2.0, minbeamfrac=0.1,
                           savemodel='none')
                    estimate_SNR(iname)



            ### SELF-CAL using MTMFS expansion
            elif sc_mode == 'MTMFS':

                print('\n      > MTMFS self-calibration:')


                # PHASE self-cal iterations
                for ip in range(len(p_solint)):

                    print('\n        PHASE self-cal iteration ' + str(ip+1) + \
                          ': solint=' + p_solint[ip] + ' ....')


                    # prepare for gain calculations
                    if p_solint[ip] == 'all':
                        gcombine = 'spw, scan'
                        p_solint[ip] = 'inf'
                    else: gcombine = 'spw'
                    visi = self_dir + pref + '.cont_p' + str(ip)


                    # calculate gain solutions
                    cal_p = self_dir + pref + '.p' + str(ip+1)
                    os.system('rm -rf ' + cal_p)
                    gaincal(vis=visi + '.ms', caltable=cal_p, calmode='p', 
                            solint=p_solint[ip], minsnr=p_minsnr, 
                            combine=gcombine, gaintype='G') 


                    # apply gain solutions
                    applycal(vis=visi + '.ms', gaintable=cal_p, spw='', 
                             spwmap=[Nspw*[0]], calwt=False, 
                             applymode='calonly')


                    # split off the gain-corrected measurement set
                    viso = self_dir + pref + '.cont_p' + str(ip+1)
                    os.system('rm -rf ' + viso + '.ms*')
                    mstransform(vis=visi + '.ms', outputvis=viso + '.ms', 
                                datacolumn='corrected')


                    # image the results
                    iname = simg_dir + pref + '.cont_p' + str(ip+1)
                    for ext in exts: os.system('rm -rf ' + iname + ext)
                    tclean(vis=viso + '.ms', imagename=iname, 
                           datacolumn='data', deconvolver='mtmfs', scales=[0], 
                           nterms=nterms, weighting='briggs', robust=2.0, 
                           pblimit=pblim, pbmask=0, imsize=imsize, cell=cell, 
                           niter=100000, nsigma=1.0, interactive=False,
                           usemask=usemask, mask=mask, noisethreshold=sc_nt, 
                           lownoisethreshold=sc_lnt, cutthreshold=0.05, 
                           sidelobethreshold=2.0, minbeamfrac=0.1,
                           savemodel='modelcolumn')
                    estimate_SNR(iname)



                # if performing amplitude self-cal, copy over datafile
                if len(a_solint) > 0:
                    os.system('rm -rf ' + self_dir + pref + '.cont_a0.ms*')
                    os.system('cp -r ' + self_dir + pref + '.cont_p' + \
                              str(len(p_solint)) + '.ms ' + \
                              self_dir + pref + '.cont_a0.ms')


                # AMPLITUDE + PHASE self-cal iterations
                for ia in range(len(a_solint)):

                    print('\n        AMPLITUDE + PHASE self-cal iteration ' + \
                          str(ia+1) + ': solint=' + a_solint[ia] + ' ....')


                    # prepare for grain calculations
                    if a_solint[ia] == 'all':
                        gcombine = 'spw,scan'
                        a_solint[ia] = 'inf'
                    else: gcombine = 'spw'
                    visi = self_dir + pref + '.cont_a' + str(ia)


                    # calculate gain solutions
                    cal_a = self_dir + pref + '.a' + str(ia+1)
                    os.system('rm -rf ' + cal_a)
                    gaincal(vis=visi + '.ms', caltable=cal_a, calmode='ap',
                            solint=a_solint[ia], minsnr=a_minsnr, 
                            combine=gcombine, gaintype='G', solnorm=True)


                    # apply gain solutions
                    applycal(vis=visi + '.ms', gaintable=cal_a, spw='', 
                             spwmap=[Nspw*[0]], calwt=True, 
                             applymode='calonly')


                    # split off the gain-corrected MS
                    viso = self_dir + pref + '.cont_a' + str(ia+1)
                    os.system('rm -rf ' + viso + '.ms*')
                    mstransform(vis=visi + '.ms', outputvis=viso + '.ms', 
                                datacolumn='corrected')


                    # image
                    iname = simg_dir + pref + '.cont_a' + str(ia+1)
                    for ext in exts: os.system('rm -rf ' + iname + ext)
                    tclean(vis=viso + '.ms', imagename=iname,
                           datacolumn='data', deconvolver='mtmfs', scales=[0],
                           nterms=nterms, weighting='briggs', robust=2.0,
                           pblimit=pblim, pbmask=0, imsize=imsize, cell=cell,
                           niter=100000, nsigma=1.0, interactive=False,
                           usemask=usemask, mask=mask, noisethreshold=sc_nt, 
                           lownoisethreshold=sc_lnt, cutthreshold=0.05, 
                           sidelobethreshold=2.0, minbeamfrac=0.1,
                           savemodel='modelcolumn')
                    estimate_SNR(iname)


            else:

                print('\n\n sc_mode is not a valid selfcal_mode: exiting.')
                sys.exit()



            # copy the final self-calibrated measurement set up a layer
            selfcal_ms = EB_dir + pref + '.selfcal'
            os.system('rm -rf ' + selfcal_ms + '.ms')
            os.system('cp -r ' + viso + '.ms ' + selfcal_ms + '.ms')



        ### NO SELF-CAL: make an image and copy the reduced datafile 
        else:

            print('\n      > NO self-calibration:')


            # make an image
            pre_name = simg_dir + pref + '.cont_p0'
            for ext in exts: os.system('rm -rf ' + pre_name + ext)
            tclean(vis=msfiles[it], imagename=pre_name, datacolumn='data', 
                   deconvolver='mtmfs', scales=[0], pblimit=pblim, 
                   nterms=2, weighting='briggs', robust=2.0, 
                   imsize=imsize, cell=cell, niter=100000, nsigma=1.0,
                   interactive=False, usemask=usemask, mask=mask, pbmask=0,
                   noisethreshold=nt, lownoisethreshold=lnt, cutthreshold=0.05, 
                   sidelobethreshold=2.0, minbeamfrac=0.1, savemodel='none')
            estimate_SNR(pre_name)


            # copy the reduced datafile to the output datafile
            selfcal_ms = EB_dir + pref + '.selfcal'
            os.system('rm -rf ' + selfcal_ms + '.ms')
            os.system('cp -r ' + msfiles[it] + ' ' + selfcal_ms + '.ms')
