import os
import sys
from pathlib import Path
import glob
import numpy as np
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')



# observing band and execution blocks
band = 'X'
EB = ['03_1', '11_1', '12_1', '02_1', '10_1', '01_1', '07_1', '08_1',
      '05_1', '14_1', '04_1', '06_1', '09_1', '13_1', '03_2', '02_2',
      '14_2', '07_2', '12_2', '18_1', '15_1', '16_1', '16_2', '17_1']
EB = [band + item + '/' for item in EB]



### Basic definitions
# paths
proc_dir = '/d4/asha1/dust-spectra/DR/VLA/'
exts = ['.image', '.mask', '.model', '.pb', '.psf', '.residual',
        '.sumwt', '.*.tt*', '.alpha', '.alpha.error', '.beta', '.beta.error']

if band == 'X':
    Nspw = 32
elif band == 'U':
    Nspw = 48
elif ((band == 'K') or (band == 'A') or (band == 'Q')):
    Nspw = 64


# loop over execution blocks
for i in [7]: #range(len(EB)):
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
    for it in [0]: #range(5, len(targs)):
        print(f"\nProcessing data for {targs[it]} from execution {EB[i]}...")

        # get imaging / self-cal information from dictionary
        idict = td[targs[it]][band][EB[i][:-1]]

        # get some useful imaging parameters
        cell, imsize, est_beam, nu_, pb = imparamcalc(msfiles[it], D_ant=25.)
        nt, lnt, imscl = idict['nt'], idict['lnt'], idict['imscl']
        if 'pblim' in idict:
            pblim = idict['pblim']
        else: pblim = -0.1


        ### PEELING
        if idict['peel']:
            print('Peeling background sources...')

            # copy the reduced MS to an initial, pre-processing MS 
            cont_pre = self_dir + targs[it] + '.' + band + '.cont_pre.ms'
            os.system('rm -rf ' + cont_pre + '*')
            os.system('cp -r ' + msfiles[it] + ' ' + cont_pre)

            # extract the peeling parameters if available
            if 'peel_nt' in idict:          # autothresh mask in peel
                p_nt = idict['peel_nt']
            else: p_nt = nt
            if 'peel_lnt' in idict:         # autothresh mask growth in peel
                p_lnt = idict['peel_lnt']
            else: p_lnt = lnt
            if 'peel_pb' in idict:          # boundary in PBFWHM for peel
                p_pb = idict['peel_pb']
            else: p_pb = '0.1'
            if 'p_pblim' in idict:          # PBlimit for peel (rare use)
                p_pblim = idict['p_pblim']
            else: p_pblim = -0.1
            if 'peel_mode' in idict:        # MTMFS or PER-SPW 
                peel_mode = idict['peel_mode']
            else: peel_mode = 'MTMFS'
            if 'peel_selfcal' in idict:     # self-cal inside the peel
                peel_selfcal = idict['peel_selfcal']
                if 'peel_psolint' in idict:    # selfcal pha solution intervals
                    p_psolint = idict['peel_psolint']
                else: p_psolint = ['inf']
                if 'peel_asolint' in idict:    # selfcal amp solution intervals
                    p_asolint = idict['peel_asolint']
                else: p_asolint = ['inf']
            else: peel_selfcal = False


            # make an initial MTMFS image to define the peel mask
            print('Initial imaging to define peel mask...')
            pname = simg_dir + targs[it] + '.' + band + '.cont_pre'
            for ext in exts: os.system('rm -rf ' + pname + ext)
            tclean(vis=cont_pre, imagename=pname, selectdata=True, 
                   datacolumn='data', specmode='mfs', gridder='standard', 
                   deconvolver='mtmfs', scales=[0], pblimit=p_pblim, nterms=2, 
                   weighting='briggs', robust=2.0, imsize=int(imscl * imsize),
                   cell=cell, niter=100000, nsigma=1.0, interactive=False,
                   usemask='auto-multithresh', cutthreshold=0.05, 
                   noisethreshold=p_nt, lownoisethreshold=p_lnt, 
                   smoothfactor=1.0, sidelobethreshold=2.0, minbeamfrac=0.1, 
                   pbmask=0.0, savemodel='none')

            # remove the sources (including target) inside 'peel_pb' from the
            # mask, so these are not part of the peel model
            os.system('rm -rf ' + pname + '.peel-mask')
            immath(imagename=[pname + '.mask', pname + '.pb.tt0'],
                   outfile=pname + '.peel-mask', imagemd = pname + '.mask',
                   mode='evalexpr', expr='iif(IM1<'+p_pb+',IM0,0.0)')
            makemask(mode='delete', inpmask=pname + '.peel-mask:mask0')

            # gate for the peel_mode (per SPW or continue MTMFS)
            os.system('rm -rf ' + simg_dir + targs[it] + '.' + band + '.peel*')
            os.system('rm -rf ' + cont_pre + '.peel*')
            cont_p0 = self_dir + targs[it] + '.' + band + '.cont_p0.ms'
            os.system('rm -rf ' + cont_p0)
            if peel_mode == 'PER-SPW':
                # per SPW initial imaging
                iname = simg_dir + targs[it] + '.' + band + '.peel'
                for ispw in range(Nspw):
                    sspw = str(ispw).zfill(2)
                    print('\nInitial imaging for peel: SPW ' + sspw + '...')
                    tclean(vis=cont_pre, imagename=iname + '-spw' + sspw, 
                           selectdata=True, datacolumn='data', specmode='mfs',
                           spw=str(ispw), gridder='standard', 
                           deconvolver='mtmfs', scales=[0], pblimit=p_pblim, 
                           nterms=1, weighting='briggs', robust=2.0, 
                           imsize=int(imscl * imsize), cell=cell, niter=100000, 
                           nsigma=1.0, interactive=False, usemask='user', 
                           mask=pname + '.peel-mask', savemodel='modelcolumn')

                # per SPW self-calibration if requested
                if peel_selfcal:
                    for ispw in range(Nspw):
                        sspw = str(ispw).zfill(2)
                        print('\nPeel self-calibration: SPW ' + sspw + '...')

                        # gain solutions (amp + pha)
                        gcal = cont_pre + '.peel-spw' + sspw + '.ap1'
                        gaincal(vis=cont_pre, caltable=gcal, solint='inf',
                                combine='scan', spw=str(ispw), minsnr=2.5, 
                                gaintype='G', calmode='ap')
                    
                        # apply gain solutions (amp + pha)
                        applycal(vis=cont_pre, gaintable=gcal, spw=str(ispw),
                                 applymode='calonly', calwt=False)

                    # subtract the self-calibrated peel model
                    uvsub(vis=cont_pre)
                    mstransform(vis=cont_pre, 
                                outputvis=cont_pre + '.peel-selfcal', 
                                datacolumn='corrected')

                    # undo the self-cal solutions for the subtracted data
                    for ispw in range(Nspw):
                        sspw = str(ispw).zfill(2)
                        gcal = cont_pre + '.peel-spw' + sspw + '.ap1'
                        os.system('cp -r ' + gcal + ' ' + gcal + '_undo')
                       
                        # re-scale gaintable to undo the solutions
                        tb.open(gcal + '_undo', nomodify=False)
                        tmp = tb.getcol('CPARAM')
                        tb.putcol('CPARAM', 1.0 / tmp)
                        tb.done()

                        # apply those gaintable corrections
                        applycal(vis=cont_pre + '.peel-selfcal',
                                 gaintable=gcal + '_undo', spw=str(ispw), 
                                 applymode='calonly', calwt=False)

                    # split out the peel + selfcal products to continue
                    mstransform(vis=cont_pre + '.peel-selfcal',
                                outputvis=cont_p0, datacolumn='corrected')
    

                # direct model subtraction (no self-calibration in peel)
                else:
                    # subtract the clean components in peel mask
                    uvsub(vis=cont_pre)
                    mstransform(vis=cont_pre, outputvis=cont_p0, 
                                datacolumn='corrected')


            else:
                # determine the Taylor-expansion order
                if 'peel_nterms' in idict:
                    p_nterms = idict['peel_nterms']
                else: p_nterms = 2

                # composite MTMFS initial imaging
                iname = simg_dir + targs[it] + '.' + band + '.peel'
                for ext in exts: os.system('rm -rf ' + iname + '-mfs' + ext)
                print('\nInitial imaging for peel (full-band)...')
                tclean(vis=cont_pre, imagename=iname + '-mfs', selectdata=True, 
                       datacolumn='data', specmode='mfs', gridder='standard', 
                       deconvolver='mtmfs', scales=[0], pblimit=p_pblim, 
                       nterms=p_nterms, weighting='briggs', robust=2.0, 
                       imsize=int(imscl * imsize), cell=cell, niter=100000, 
                       nsigma=1.0, interactive=False, usemask='user', 
                       mask=pname + '.peel-mask', savemodel='modelcolumn')

                # full-band MTMFS self-calibration if requested
                if peel_selfcal:
                    print('\nPeel self-calibration (full-band)...')

                    # gain solutions (amp + pha)
                    gcal = cont_pre + '.peel-mfs.ap1'
                    gaincal(vis=cont_pre, caltable=gcal, solint='inf',
                            combine='spw', minsnr=2.5, gaintype='G', 
                            calmode='ap')
                    
                    # apply gain solutions (amp + pha)
                    applycal(vis=cont_pre, gaintable=gcal, spwmap=[Nspw*[0]], 
                             applymode='calonly', calwt=False)

                    # subtract the self-calibrated peel model
                    uvsub(vis=cont_pre)
                    mstransform(vis=cont_pre, 
                                outputvis=cont_pre + '.peel-selfcal', 
                                datacolumn='corrected')

                    # undo the self-cal solutions for the subtracted data
                    os.system('cp -r ' + gcal + ' ' + gcal + '_undo')
                       
                    # re-scale gaintable to undo the solutions
                    tb.open(gcal + '_undo', nomodify=False)
                    tmp = tb.getcol('CPARAM')
                    tb.putcol('CPARAM', 1.0 / tmp)
                    tb.done()

                    # apply those gaintable corrections
                    applycal(vis=cont_pre + '.peel-selfcal',
                             gaintable=gcal + '_undo', spwmap=[Nspw*[0]],
                             applymode='calonly', calwt=False)

                    # split out the peel + selfcal products to continue
                    mstransform(vis=cont_pre + '.peel-selfcal',
                                outputvis=cont_p0, datacolumn='corrected')
    

                # direct model subtraction (no self-calibration in peel)
                else:
                    # subtract the clean components in peel mask
                    uvsub(vis=cont_pre)
                    mstransform(vis=cont_pre, outputvis=cont_p0,
                                datacolumn='corrected')

        else:
            # NO PEELING: copy the init MS into the cont_p0 MS for further use
            cont_p0 = self_dir + targs[it] + '.' + band + '.cont_p0.ms'
            os.system('rm -rf ' + cont_p0)
            os.system('cp -r ' + msfiles[it] + ' ' + cont_p0)



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
            tclean(vis=cont_p0, imagename=pre_name, selectdata=True, 
                   datacolumn='data', specmode='mfs', gridder='standard', 
                   deconvolver='mtmfs', scales=[0], pblimit=pblim, 
                   nterms=nterms, weighting='briggs', robust=2.0, 
                   imsize=int(imscl * imsize), cell=cell, niter=100000, 
                   nsigma=1.0, interactive=False, usemask='auto-multithresh', 
                   cutthreshold=0.05, noisethreshold=sc_nt, 
                   lownoisethreshold=sc_lnt, smoothfactor=1.0, 
                   sidelobethreshold=2.0, minbeamfrac=0.1, pbmask=0., 
                   savemodel='modelcolumn')


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
                for isc in range(1,3):
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
                    tclean(vis=viso + '.ms', imagename=iname, selectdata=True, 
                           datacolumn='data', specmode='mfs', 
                           gridder='standard', deconvolver='mtmfs', scales=[0], 
                           pblimit=pblim, nterms=nterms, weighting='briggs', 
                           robust=2.0, imsize=int(imscl * imsize), cell=cell, 
                           niter=100000, nsigma=1.0, interactive=False,
                           usemask='auto-multithresh', cutthreshold=0.05, 
                           noisethreshold=sc_nt, lownoisethreshold=sc_lnt, 
                           smoothfactor=1.0, sidelobethreshold=2.0, 
                           minbeamfrac=0.1, pbmask=0., savemodel='modelcolumn')


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
                    tclean(vis=viso + '.ms', imagename=iname, selectdata=True,
                           datacolumn='data', specmode='mfs', 
                           gridder='standard', deconvolver='mtmfs', scales=[0],                            pblimit=pblim, nterms=nterms, weighting='briggs', 
                           robust=2.0, imsize=int(imscl * imsize), cell=cell, 
                           niter=100000, nsigma=1.0, interactive=False,
                           usemask='auto-multithresh', cutthreshold=0.05,
                           noisethreshold=sc_nt, lownoisethreshold=sc_lnt, 
                           smoothfactor=1.0, sidelobethreshold=2.0, 
                           minbeamfrac=0.1, pbmask=0., savemodel='modelcolumn')


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
            tclean(vis=cont_p0, imagename=pre_name, selectdata=True,
                   datacolumn='data', specmode='mfs', gridder='standard',
                   deconvolver='mtmfs', scales=[0], pblimit=pblim,
                   nterms=2, weighting='briggs', robust=2.0,
                   imsize=int(imscl * imsize), cell=cell, niter=100000,
                   nsigma=1.0, interactive=False, usemask='auto-multithresh',
                   cutthreshold=0.05, noisethreshold=nt, lownoisethreshold=lnt, 
                   smoothfactor=1.0, sidelobethreshold=2.0, minbeamfrac=0.1, 
                   pbmask=0., savemodel='modelcolumn')

            selfcal_MS = EB_dir + targs[it] + '.' + band + '.selfcal.ms'
            os.system('rm -rf ' + selfcal_MS)
            os.system('cp -r ' + cont_p0 + ' ' + selfcal_MS)
