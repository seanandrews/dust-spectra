import os
import sys
from pathlib import Path
import glob
import numpy as np
sys.path.append('../')
from targets_dict import targ as td
execfile('reduction_tools.py')


# I/O paths
proc_dir = '/d4/asha1/dust-spec/DR/VLA/'


# fixed quantities: observing band, image extensions
band = 'X'
exts = ['.image', '.mask', '.model', '.pb', '.psf', '.residual',
        '.sumwt', '.*.tt0', '.*.tt1', '.*.tt2', '.alpha', '.alpha.error']


# execution identifiers
EB = ['03_1', '11_1', '12_1', '02_1', '10_1', '01_1', '07_1', '08_1',
      '05_1', '14_1', '04_1', '06_1', '09_1', '13_1', '03_2', '02_2',
      '14_2', '07_2', '12_2', '18_1', '15_1', '16_1', '16_2', '17_1']
EB = [band + item + '/' for item in EB]


# loop over execution blocks
for i in [19]: #range(1,len(EB)):
    # tracking
    print(f"--------------------------------------------------")
    print(f"Imaging dataset {i:02d} for execution {EB[i]}...")

    # identify the available targets and reduced MS filenames
    EB_dir = proc_dir + EB[i]
    ms = [f.name for f in Path(EB_dir).glob('*.' + band + '.reduced.ms')]
    targs = [f.split('.' + band + '.reduced.ms', 1)[0] for f in ms]
    msfiles = [proc_dir + EB[i] + f for f in ms]
    print(targs)


    # loop over targets
    for it in [7]: #range(len(targs)):
        # tracking
        print(f"\ninitial imaging for execution {EB[i]} of {targs[it]}...")

        # get target dictionary
        src = td[targs[it]]
        nt, lnt = 5.0, 2.0
#        nt, lnt = 11.0, 4.0
#        nt, lnt = 25.0, 15.0
        imscl = 1.0

        # copy the reduced MS file to a initial MS file
        self_dir = EB_dir + 'selfcal/'
        if not os.path.exists(self_dir):
            os.system('mkdir ' + self_dir)
        if not os.path.exists(self_dir + 'images/'):
            os.system('mkdir ' + self_dir + 'images/')
        cont_p0 = self_dir + targs[it] + '.' + band + '.cont_p0.ms'
        os.system('rm -rf ' + cont_p0 + '*')
        os.system('cp -r ' + msfiles[it] + ' ' + cont_p0)

        # if necessary, make an outlier file
        if 'outlier_RA' in src:
            out_name = self_dir + 'images/' + \
                       targs[it] + '.' + band + '.outlier'
            os.system('rm -rf ' + out_name + '.txt')
            if not isinstance(src['outlier_RA'], list):
                oRA = list([src['outlier_RA']])
                oDEC = list([src['outlier_DEC']])
            else:
                oRA = src['outlier_RA']
                oDEC = src['outlier_DEC']
            for iout in range(len(oRA)):
                oRA_ = oRA[iout]
                oDEC_ = oDEC[iout].replace(':', '.')
                with open(out_name + '.txt', "a") as f:
                    print("imagename=" + out_name + str(iout), file=f)
                    print("imsize = [100,100]", file=f)
                    print("phasecenter = J2000 " + oRA_ + ' ' + oDEC_, file=f)
            outlierfile = out_name + '.txt'
        else:
            outlierfile = ''

        # get some useful imaging parameters
        cell, imsize, est_beam, nu_, pb = imparamcalc(msfiles[it], D_ant=25.)

        # initial imaging
        imname = self_dir + 'images/' + targs[it] + '.' + band + '.cont_p0'
        for ext in exts: os.system('rm -rf ' + imname + ext)
        tclean(vis=cont_p0, imagename=imname, selectdata=True, 
               datacolumn='data', specmode='mfs', gridder='standard', 
               deconvolver='mtmfs', scales=[0], pblimit=-0.1, nterms=2, 
               weighting='briggs', robust=2.0, imsize=int(imscl * imsize),
               cell=cell, niter=100000, nsigma=1.0, interactive=False,
               usemask='auto-multithresh', cutthreshold=0.05, 
               noisethreshold=nt, lownoisethreshold=lnt, smoothfactor=1.0, 
               sidelobethreshold=2.0, minbeamfrac=0.1, pbmask=0.0, 
               outlierfile=outlierfile, savemodel='modelcolumn')
