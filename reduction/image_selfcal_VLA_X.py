import os
import sys
from pathlib import Path
import glob
import numpy as np
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')


# I/O paths
proc_dir = '/d4/asha1/dust-spectra/DR/VLA/'


# fixed quantities: observing band, image extensions
band = 'X'
exts = ['.image', '.mask', '.model', '.pb', '.psf', '.residual',
        '.sumwt', '.*.tt0', '.*.tt1', '.*.tt2', '.alpha', '.alpha.error']


# execution identifiers
EB = ['03_1', '11_1', '12_1', '02_1', '10_1', '01_1', '07_1', '08_1',
      '05_1', '14_1', '04_1', '06_1', '09_1', '13_1', '03_2', '02_2',
      '14_2', '07_2', '12_2', '18_1', '15_1', '16_1', '16_2', '17_1']
EB = [band + item + '/' for item in EB]

'''
X12_1 IRAS 04385, IRAS 04370, CIDA 7
probably try self-cal with combined IRAS 04125 (maybe others)
look into X14_1
X02_2: can't get decent image of CY Tau...
'''


# loop over execution blocks
for i in [0]: #range(1,len(EB)):
    # tracking
    print(f"--------------------------------------------------")
    print(f"Imaging dataset {i:02d} for execution {EB[i]}...")

    # identify the available targets and reduced MS filenames
    EB_dir = proc_dir + EB[i]
    ms = [f.name for f in Path(EB_dir).glob('*.' + band + '.reduced.ms')]
    targs = [f.split('.' + band + '.reduced.ms', 1)[0] for f in ms]
    msfiles = [proc_dir + EB[i] + f for f in ms]
    print(targs)



    # make sure there's a self-cal / imaging path for this execution block
    self_dir = EB_dir + 'selfcal/'
    if not os.path.exists(self_dir):
        os.system('mkdir ' + self_dir)
    if not os.path.exists(self_dir + 'images/'):
        os.system('mkdir ' + self_dir + 'images/')

    # loop over targets
    for it in [6]: #range(len(targs)):
        # tracking
        print(f"\ninitial imaging for execution {EB[i]} of {targs[it]}...")

        # get imaging / self-cal information from dictionary
        idict = td[targs[it]]['X'][EB[i][:-1]]

        # get some useful imaging parameters
        cell, imsize, est_beam, nu_, pb = imparamcalc(msfiles[it], D_ant=25.)
        nt, lnt, imscl = idict['nt'], idict['lnt'], idict['imscl']
        if 'pblim' in idict:
            pblim = idict['pblim']
        else: pblim = -0.1

        # peel background sources outside of PB if needed
        if idict['peel']:
            # copy the reduced MS file to a initial MS file
            cont_pre = self_dir + targs[it] + '.' + band + '.cont_pre.ms'
            os.system('rm -rf ' + cont_pre + '*')
            os.system('cp -r ' + msfiles[it] + ' ' + cont_pre)

            # extract widefield imaging / peeling parameters if available
            if 'peel_nt' in idict:
                p_nt = idict['peel_nt']
            else: p_nt = nt
            if 'peel_lnt' in idict:
                p_lnt = idict['peel_lnt']
            else: p_lnt = lnt
            if 'peel_pb' in idict:
                p_pb = idict['peel_pb']
            else: p_pb = '0.1'
            if 'p_pbl' in idict:
                p_pblim = idict['p_pbl']
            else: p_pblim = -0.1
            if 'peel_mode' in idict:
                peel_mode = idict['peel_mode']
            else: peel_mode = 'mfs'

            # make an initial MTMFS image
            iname = self_dir + 'images/' + targs[it] + '.' + band + '.cont_pre'
            for ext in exts: os.system('rm -rf ' + iname + ext)
            tclean(vis=cont_pre, imagename=iname, selectdata=True, 
                   datacolumn='data', specmode='mfs', gridder='standard', 
                   deconvolver='mtmfs', scales=[0], pblimit=p_pblim, nterms=2, 
                   weighting='briggs', robust=2.0, imsize=int(imscl * imsize),
                   cell=cell, niter=100000, nsigma=1.0, interactive=False,
                   usemask='auto-multithresh', cutthreshold=0.05, 
                   noisethreshold=p_nt, lownoisethreshold=p_lnt, 
                   smoothfactor=1.0, sidelobethreshold=2.0, minbeamfrac=0.1, 
                   pbmask=0.0, savemodel='none')

            # save the initial image (before peeling subtraction), as a double
            # check that the peeling goes well
            os.system('rm -rf ' + iname + '.init.image.tt0')
            os.system('cp -r ' + iname + '.image.tt0 ' + \
                       iname + '.init.image.tt0')

            # mask model
#            os.system('rm -rf ' + iname + '.model.tt0.masked-within-PB')
#            immath(imagename=[iname + '.model.tt0', iname + '.pb.tt0'],
#                   outfile=iname + '.model.tt0.masked-within-PB',
#                   imagemd=iname + '.model.tt0',
#                   mode='evalexpr', expr='iif(IM1<'+p_pb+',IM0,0.0)')
#            makemask(mode='delete', 
#                     inpmask=iname + '.model.tt0.masked-within-PB:mask0')
#            os.system('rm -rf ' + iname + '.model.tt1.masked-within-PB')
#            immath(imagename=[iname + '.model.tt1', iname + '.pb.tt0'],
#                   outfile=iname + '.model.tt1.masked-within-PB',
#                   imagemd=iname + '.model.tt1',
#                   mode='evalexpr', expr='iif(IM1<'+p_pb+',IM0,0.0)')
#            makemask(mode='delete', 
#                     inpmask=iname + '.model.tt1.masked-within-PB:mask0')

            os.system('rm -rf ' + iname + '.masked.mask')
            immath(imagename=[iname + '.mask', iname + '.pb.tt0'],
                   outfile=iname + '.masked.mask', imagemd = iname + '.mask',
                   mode='evalexpr', expr='iif(IM1<'+p_pb+',IM0,0.0)')
            makemask(mode='delete', inpmask=iname + '.masked.mask:mask0')

            # put into model column
#            os.system('rm -rf ' + iname + '.model.tt0.save')
#            os.system('mv ' + iname + '.model.tt0 ' + \
#                      iname + '.model.tt0.save')
#            os.system('rm -rf ' + iname + '.model.tt1.save')
#            os.system('mv ' + iname + '.model.tt1 ' + \
#                      iname + '.model.tt1.save')
#            tclean(vis=cont_pre, imagename=iname, selectdata=True, 
#                   datacolumn='data', specmode='mfs', gridder='standard', 
#                   deconvolver='mtmfs', scales=[0], pblimit=-0.1, nterms=2,
#                   weighting='briggs', robust=2.0, imsize=int(imscl * imsize),
#                   cell=cell, niter=0, 
#                   startmodel=[iname + '.model.tt0.masked-within-PB', 
#                               iname + '.model.tt1.masked-within-PB'], 
#                   savemodel='modelcolumn')

            # image each SPW
            if peel_mode == 'spw':
                for ispw in range(32):
                    for ext in exts: 
                        os.system('rm -rf ' + iname + '.spw' + str(ispw) + ext)
                    print('Peeling for SPW ' + str(ispw).zfill(2) + '...\n')
                    tclean(vis=cont_pre, imagename=iname + '.spw' + str(ispw), 
                           selectdata=True, datacolumn='data', specmode='mfs',
                           spw=str(ispw), gridder='standard', 
                           deconvolver='mtmfs', scales=[0], pblimit=p_pblim, 
                           nterms=1, weighting='briggs', robust=2.0, 
                           imsize=int(imscl * imsize), cell=cell, niter=100000, 
                           nsigma=1.0, interactive=False, usemask='user', 
                           mask=iname + '.masked.mask', 
                           savemodel='modelcolumn')
            else:
                for ext in exts: os.system('rm -rf ' + iname + '.mfs' + ext)
                print('Peeling for MFS ...\n')
                tclean(vis=cont_pre, imagename=iname + '.mfs',
                           selectdata=True, datacolumn='data', specmode='mfs',
                           gridder='standard', deconvolver='mtmfs', scales=[0], 
                           pblimit=p_pblim, nterms=1, weighting='briggs', 
                           robust=2.0, imsize=int(imscl * imsize), 
                           cell=cell, niter=100000, nsigma=1.0, 
                           interactive=False, usemask='user', 
                           mask=iname + '.masked.mask', 
                           savemodel='modelcolumn')
                
            # subtract sources outside PB
            uvsub(vis=cont_pre)
            os.system('rm -rf ' + cont_pre + '-peeled*')
            mstransform(vis=cont_pre, outputvis=cont_pre + '-peeled',
                        datacolumn='corrected')

            # copy the peeled MS into the cont_p0 MS for further use
            cont_p0 = self_dir + targs[it] + '.' + band + '.cont_p0.ms'
            os.system('rm -rf ' + cont_p0 + '*')
            os.system('cp -r ' + cont_pre + '-peeled ' + cont_p0)

        else:
            # copy the init MS into the cont_p0 MS for further use
            cont_p0 = self_dir + targs[it] + '.' + band + '.cont_p0.ms'
            os.system('rm -rf ' + cont_p0 + '*')
            os.system('cp -r ' + msfiles[it] + ' ' + cont_p0)


        # initial imaging
        print('...INITIAL IMAGING...\n')
        iname = self_dir + 'images/' + targs[it] + '.' + band + '.cont_p0'
        for ext in exts: os.system('rm -rf ' + iname + ext)
        tclean(vis=cont_p0, imagename=iname, selectdata=True, 
               datacolumn='data', specmode='mfs', gridder='standard', 
               deconvolver='mtmfs', scales=[0], pblimit=pblim, nterms=2, 
               weighting='briggs', robust=2.0, imsize=int(imscl * imsize), 
               cell=cell, niter=100000, nsigma=1.0, interactive=False,
               usemask='auto-multithresh', cutthreshold=0.05, 
               noisethreshold=nt, lownoisethreshold=lnt, smoothfactor=1.0, 
               sidelobethreshold=2.0, minbeamfrac=0.1, pbmask=0.0, 
               savemodel='modelcolumn')


        # remove previous self-cal iteration files for tidiness
        os.system('rm -rf ' + self_dir + targs[it] + '.' + band + '.p*')
        os.system('rm -rf ' + self_dir + targs[it] + '.' + band + '.a*')
        pref = targs[it] + '.' + band
        for isc in range(1,3):
            ms_f = self_dir + pref + '.cont_p' + str(isc) + '*.ms'
            os.system('rm -rf ' + ms_f)
            im_f = self_dir + 'images/' + pref + '.cont_p' + str(isc) + '*'
            os.system('rm -rf ' + im_f)
            ms_f = self_dir + pref + '.cont_a' + str(isc) + '*.ms'
            os.system('rm -rf ' + ms_f)
            im_f = self_dir + 'images/' + pref + '.cont_a' + str(isc) + '*'
            os.system('rm -rf ' + im_f)


        """ phase-only self-calibration iterations """
        # get phase-only solution intervals and minimum SNR thresholds
        p_solint = idict['psolint']
        if 'pminsnr' in idict:
            p_minsnr = idict['pminsnr']
        else: p_minsnr = 3.0

        for ip in range(len(p_solint)):
            print('...PHASE SELF-CAL ' + str(ip+1) + \
                  ': solint=' + p_solint[ip] + '...\n')

            # calculate the gain table
            cal_p = self_dir + targs[it] + '.' + band + '.p' + str(ip+1)
            os.system('rm -rf ' + cal_p)
            visi = self_dir + targs[it] + '.' + band + '.cont_p' + str(ip)
            gaincal(vis=visi + '.ms', caltable=cal_p, gaintype='G', 
                    calmode='p', combine='spw', 
                    solint=p_solint[ip], minsnr=p_minsnr)

            # apply the gain table
            applycal(vis=visi + '.ms', gaintable=cal_p, spw='', 
                     spwmap=[32*[0]], interp=['nearest,linearpd'], 
                     calwt=False, applymode='calonly')

            # split off the gain-corrected MS
            viso = self_dir + targs[it] + '.' + band + '.cont_p' + str(ip+1)
            os.system('rm -rf ' + viso + '.ms*')
            mstransform(vis=visi + '.ms', outputvis=viso + '.ms', 
                        datacolumn='corrected')

            # image
            iname = self_dir + 'images/' + targs[it] + '.' + band + \
                    '.cont_p' + str(ip+1)
            for ext in exts: os.system('rm -rf ' + iname + ext)
            tclean(vis=viso + '.ms', imagename=iname, selectdata=True, 
                   datacolumn='data', specmode='mfs', gridder='standard', 
                   deconvolver='mtmfs', scales=[0], pblimit=pblim, nterms=2, 
                   weighting='briggs', robust=2.0, imsize=int(imscl * imsize), 
                   cell=cell, niter=100000, nsigma=1.0, interactive=False,
                   usemask='auto-multithresh', cutthreshold=0.05, 
                   noisethreshold=nt, lownoisethreshold=lnt, smoothfactor=1.0, 
                   sidelobethreshold=2.0, minbeamfrac=0.1, pbmask=0.0, 
                   savemodel='modelcolumn')


        """ amp + phase self-calibration iterations """
        # get amp + phase solution intervals and minimum SNR thresholds
        a_solint = idict['asolint']
        if 'aminsnr' in idict:
            a_minsnr = idict['aminsnr']
        else: a_minsnr = 3.0

        if len(a_solint) > 0:
            os.system('rm -rf ' + self_dir + targs[it] + '.' + band + \
                      '.cont_a0.ms*')
            os.system('cp -r ' + self_dir + targs[it] + '.' + band + \
                      '.cont_p' + str(len(p_solint)) + '.ms ' + \
                      self_dir + targs[it] + '.' + band + '.cont_a0.ms')

        for ia in range(len(a_solint)):
            print('...AMPLITUDE + PHASE SELF-CAL ' + str(ia+1) + \
                  ': solint=' + a_solint[ia] + '...\n')

            # calculate the gain table
            cal_a = self_dir + targs[it] + '.' + band + '.a' + str(ia+1)
            os.system('rm -rf ' + cal_a)
            visi = self_dir + targs[it] + '.' + band + '.cont_a' + str(ia)
            gaincal(vis=visi + '.ms', caltable=cal_a, gaintype='G', 
                    calmode='ap', combine='spw', 
                    solint=a_solint[ia], minsnr=a_minsnr)

            # apply the gain table
            applycal(vis=visi + '.ms', gaintable=cal_a, spw='', 
                     spwmap=[32*[0]], interp=['nearest,linearpd'], 
                     calwt=True, applymode='calonly')

            # split off the gain-corrected MS
            viso = self_dir + targs[it] + '.' + band + '.cont_a' + str(ia+1)
            os.system('rm -rf ' + viso + '.ms*')
            mstransform(vis=visi + '.ms', outputvis=viso + '.ms', 
                        datacolumn='corrected')

            # image
            iname = self_dir + 'images/' + targs[it] + '.' + band + \
                    '.cont_a' + str(ia+1)
            for ext in exts: os.system('rm -rf ' + iname + ext)
            tclean(vis=viso + '.ms', imagename=iname, selectdata=True, 
                   datacolumn='data', specmode='mfs', gridder='standard', 
                   deconvolver='mtmfs', scales=[0], pblimit=pblim, nterms=2, 
                   weighting='briggs', robust=2.0, imsize=int(imscl * imsize), 
                   cell=cell, niter=100000, nsigma=1.0, interactive=False,
                   usemask='auto-multithresh', cutthreshold=0.05, 
                   noisethreshold=nt, lownoisethreshold=lnt, smoothfactor=1.0, 
                   sidelobethreshold=2.0, minbeamfrac=0.1, pbmask=0.0, 
                   savemodel='modelcolumn')

        # copy the self-calibrated MS back up a layer
        os.system('rm -rf ' + EB_dir + targs[it] + '.' + band + '.selfcal.ms')
        if np.logical_or(len(p_solint) > 0, len(a_solint) > 0):
            os.system('cp -r ' + viso + '.ms ' + \
                      EB_dir + targs[it] + '.' + band + '.selfcal.ms')
        else:
            visi = self_dir + targs[it] + '.' + band + '.cont_p0'
            os.system('cp -r ' + visi + '.ms ' + \
                      EB_dir + targs[it] + '.' + band + '.selfcal.ms')
