import os
import sys
import time
import importlib
import numpy as np
import emcee
from multiprocessing import Pool
from mcmc_tools import *
import corner
from deproject_vis import *
import matplotlib.pyplot as plt

# style setups (always deployed)
_ = importlib.import_module('plot_setups')
plt.style.use(['default', '/home/sandrews/mpl_styles/nice_line.mplstyle'])



### User Controls

""" User definitions and setups """

# identify datasets
targ = 'LkCa15'
data = ['_K-sub00', '_K-sub01', '_K-sub02', '_K-sub03',
        '_A-sub00', '_A-sub01', '_A-sub02', '_A-sub03',
        '_Q-sub00', '_Q-sub01', '_Q-sub02', '_Q-sub03']
wgt_rescl = 0.33 * np.ones(len(data))


# model type and prior information
mtype = 'point'
uvlim = 65.
pri_type = ['uniform', 'normal', 'normal', 'uniform']

pri_pars = [[0, 0.010], [0., 1.0], [0., 1.0], [-10, 5]]
incl, PA = 0, 0

# MCMC parameters
append = False
nsteps, ninit = 10000, 200
nwalk, nthread = 64, 8
maxtau = 500
burnfactor = 10
thinfactor = 0.5
cutfactor = 50

# location of visibilities
visdir = '/pool/asha0/SCIENCE/VLA_SEDs/DR/VLA/'+targ+'/final_vis/'

# location of posteriors subdirectory
postdir = 'posteriors/VLA/'


""" ======================================================================= """

# prior evaluators
def uniform_prior(par, p):
    if np.logical_and((par >= p[0]), (par <= p[1])):
        return 0
    else:
        return -np.inf

def normal_prior(par, p):
    return -0.5 * ((par - p[0]) / p[1])**2


""" Set function definitions based on model type selection """
if mtype == 'gauss':
    # dimensionality
    ndim = 5

    # notation
    plbls = ['flux', 'dx', 'dy', 'sigma', 'logf']
    punits = ['mJy', 'arcsec', 'arcsec', 'arcsec', '']

    # visibility model
    def vis_model(pars, u, v):
        # set the projection geometry
        theta = 0.5 * np.pi - np.radians(PA)
        mu = np.cos(np.radians(incl))
        uu = (u * np.cos(theta) + v * np.sin(theta)) * pars[3]
        vv = (-u * np.sin(theta) + v * np.cos(theta)) * pars[3] * mu
        scl = np.pi / (180 * 3600)

        # define the model fixed at the phase center
        uuvv = (uu**2 + vv**2) * scl**2
        mvis = pars[0] * np.exp(-2 * np.pi**2 * uuvv) + 1j*np.zeros_like(uuvv)

        # phase shift to treat the offsets
        dx, dy = -pars[1] * scl, -pars[2] * scl
        phase_shift = np.exp(-2 * np.pi * 1j*(u * dx + v * dy))
        mvis *= phase_shift

        return mvis

elif mtype == 'point':
    # dimensionality
    ndim = 4

    # notation
    plbls = ['flux', 'dx', 'dy', 'logf']
    punits = ['mJy', 'arcsec', 'arcsec', '']

    # visibility model
    def vis_model(pars, u, v):
        # define the model fixed at the phase center
        mvis = pars[0] * np.ones_like(u) + 1j*np.zeros_like(u)

        # phase shift to treat the offsets
        scl = np.pi / (180 * 3600)
        dx, dy = -pars[1] * scl, -pars[2] * scl
        phase_shift = np.exp(-2 * np.pi * 1j*(u * dx + v * dy))
        mvis *= phase_shift

        return mvis

elif mtype == 'point_noscat':
    # dimensionality
    ndim = 3

    # notation
    plbls = ['flux', 'dx', 'dy']
    punits = ['mJy', 'arcsec', 'arcsec']

    # visibility model
    def vis_model(pars, u, v):
        # define the model fixed at the phase center
        mvis = pars[0] * np.ones_like(u) + 1j*np.zeros_like(u)

        # phase shift to treat the offsets
        scl = np.pi / (180 * 3600)
        dx, dy = -pars[1] * scl, -pars[2] * scl
        phase_shift = np.exp(-2 * np.pi * 1j*(u * dx + v * dy))
        mvis *= phase_shift

        return mvis


else:
    print('I do not know this model.  Exiting.')
    sys.exit()



""" Probability functions """
# log-prior
def log_prior(pars):
    lnT = 0
    for ii in range(len(pars)):
        cmd = pri_type[ii]+'_prior(pars['+str(ii)+'], '+str(pri_pars[ii])+')'
        lnT += eval(cmd)
    return lnT

# log-likelihood
def log_likelihood(pars, u, v, vis, wgt):
    model_vis = vis_model(pars, u, v)
    if mtype == 'gauss':
        var = (1 / wgt) + np.absolute(model_vis)**2 * np.exp(2 * pars[4])
    elif mtype == 'point':
        var = (1 / wgt) + np.absolute(model_vis)**2 * np.exp(2 * pars[3])
    elif mtype == 'point_noscat':
        var = (1 / wgt)
    return -0.5 * np.sum(np.absolute(vis - model_vis)**2 / var + np.log(var))

# log-posterior
def log_posterior(pars, u, v, vis, wgt):
    if np.isfinite(log_prior(pars)):
        return log_likelihood(pars, u, v, vis, wgt) + log_prior(pars)
    else:
        return -np.inf





""" Inference """
# caution with internal multithreading
if (nthread > 1): os.environ["OMP_NUM_THREADS"] = "1"
 
# iterate over datafiles to fit
for i in range(len(data)):
    print(i)
    # Load the visibility data
    _ = np.load(visdir+targ+data[i]+'.vis.npz')
    u_, v_, vis_, wgt_, nu = _['u'], _['v'], _['Vis'], _['Wgt'], _['nu']
    wgt_ *= wgt_rescl[i]
    freq = np.average(nu, weights=wgt_) / 1e9

    # truncate u,v data if necessary
    uv_data = np.sqrt(u_**2 + v_**2)
    u = u_[uv_data <= 1e3 * uvlim]
    v = v_[uv_data <= 1e3 * uvlim]
    vis = vis_[uv_data <= 1e3 * uvlim]
    wgt = wgt_[uv_data <= 1e3 * uvlim]

    # Assign the output filename prefix
    outfile = targ+data[i]+'.'+mtype

    # Initialize the walkers, starting from the previous run
    if append:
        if os.path.exists(postdir+outfile+'.post.npz'):
            pre_samples = np.load(postdir+outfile+'.post.npz')['samples']
            pre_logpost = np.load(postdir+outfile+'.post.npz')['logpost']
            p00 = pre_samples[-1,:,:]
        else:
            print('I cannot find the file to append samples.  Exiting')
            sys.exit()
    # Initialize the walkers, starting from random posterior draws
    else:
        p0 = np.empty((nwalk, ndim))
        for ip in range(ndim):
            _ = 'np.random.'+pri_type[ip]+'('+str(pri_pars[ip][0])+', '
            _ += str(pri_pars[ip][1])+', '+str(nwalk)+')'
            p0[:,ip] = eval(_)

        # Quick initial run to mitigate stray walkers
        with Pool(processes=nthread) as pool:
            isampler = emcee.EnsembleSampler(nwalk, ndim, log_posterior,
                                             pool=pool, args=(u, v, vis, wgt))
            isampler.run_mcmc(p0, ninit, progress=True)
        isamples = isampler.get_chain()
        lop0 = np.quantile(isamples[-1,:,:], 0.25, axis=0)
        hip0 = np.quantile(isamples[-1,:,:], 0.75, axis=0)
        p00 = [np.random.uniform(lop0, hip0, ndim) for iw in range(nwalk)]
        p00 = np.reshape(p00, p0.shape)

    # Full MCMC run
    with Pool(processes=nthread) as pool:
        sampler = emcee.EnsembleSampler(nwalk, ndim, log_posterior,
                                        pool=pool, args=(u, v, vis, wgt))
        sampler.run_mcmc(p00, nsteps, progress=True)
    samples = sampler.get_chain()
    logpost = sampler.get_log_prob()
    if append: 
        samples = np.concatenate((pre_samples, samples))
        logpost = np.concatenate((pre_logpost, logpost))

    samples_ = mcmc_out(samples, logpost, maxtau=maxtau, cutfactor=cutfactor,
                        burnfactor=burnfactor, thinfactor=thinfactor)

    # Save the outputs
    postfile = postdir+outfile+'.post.npz'
    print('Posterior samples were saved to '+postfile)
    np.savez(postfile, samples=samples, chain=samples_, logpost=logpost)



    """ Diagnostics """
    ### plot the walker traces
    # identify outlier walkers (based on lnprob)
    nstep, nwalk, ndim = samples.shape
    ncut = round(nstep / cutfactor)
    dev_ = (np.median(logpost[ncut:,:], axis=0) - \
            np.median(logpost[ncut:,:])) / np.std(logpost[ncut:,:])
    out_ix = np.where(np.abs(dev_) >= 2)
    _samples  = np.delete(samples, out_ix, axis=1)
    _logposts = np.delete(logpost, out_ix, axis=1)
    _nwalk = _samples.shape[1]

    fig, ax = plt.subplots(nrows=ndim+1, ncols=1, figsize=(5., 8.),
                           constrained_layout=True, sharex=True)
    _samples[:,:,0] *= 1e3
    blob = np.dstack((_samples, np.reshape(_logposts, (nstep, _nwalk, 1))))
    steps = np.arange(nstep)
    for ip in range(ndim+1):
        for iw in range(_nwalk):
            ax[ip].plot(steps, blob[:,iw,ip], '-k', alpha=0.05)
        if ip < ndim:
            ax[ip].set_ylabel(plbls[ip])
        else:
            ax[ip].set_ylabel('log(prob)')
    fig.savefig('figs/'+outfile+'.traces.png')
    fig.clf()


    print(_samples.shape, samples_.shape)
    ### plot the pairwise covariances
    samples_[:,0] *= 1e3
    fig = corner.corner(samples_, 
                        levels=(1-np.exp(-0.5*(np.array([1, 2, 3]))**2)), 
                        labels=plbls)
    plt.savefig('figs/'+outfile+'.corner.png')
    fig.clf()


    ### print simple marginalized posterior summaries
    clevs = [15.85, 50., 84.15]
    CI = np.percentile(samples_, clevs, axis=0)
    print(' ')
    print('nu = %.2f GHz' % freq)
    for j in range(len(plbls)):
        print('%s = %.3f +%.3f / -%.3f %s' % \
              (plbls[j], CI[1,j], CI[2,j]-CI[1,j], CI[1,j]-CI[0,j], punits[j]))
    print(' ')

    # visibility profile + posterior draws
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(5.5, 7.5),
                           constrained_layout=True,
                           gridspec_kw={'height_ratios':[1, 1], 'hspace':0.10})
    uvdist = np.sqrt(u_**2 + v_**2) / 1e3
    duv = 1
    uvbins = np.arange(0, 200, duv)

    class Visibility:
        def __init__(self, vis, u, v, wgt):
            self.vis = vis
            self.u = u
            self.v = v
            self.wgt = wgt

    vp = deproject_vis(Visibility(vis_, u_, v_, wgt_), uvbins,
                       incl=incl, PA=PA, offx=CI[1,1], offy=CI[1,2])
    vp_ = deproject_vis(Visibility(vis_, u_, v_, wgt_), incl=incl, PA=PA,
                        offx=CI[1,1], offy=CI[1,2])

    # calculate the appropriate rescaling factor for the weights
    devs_imag = vp_.vis_prof.imag * np.sqrt(wgt_)
    print('Standard deviations of imaginaries: ', np.std(devs_imag))
    print('Weight re-scaling factor: ', 1./np.std(devs_imag)**2)
    print('\n')

    ndraws = 100
    rix = np.random.randint(0, samples_.shape[0], ndraws)
    for j in range(ndraws):
        mdraw = vis_model(samples_[rix[j],:], u_, v_)
        mvp = deproject_vis(Visibility(mdraw, u_, v_, wgt_), uvbins,
                            incl=incl, PA=PA, offx=CI[1,1], offy=CI[1,2])
        ax[0].plot(1e-3 * mvp.rho_uv, mvp.vis_prof.real,
                   'xkcd:coral pink', alpha=0.03, rasterized=True)
        ax[1].plot(1e-3 * mvp.rho_uv, mvp.vis_prof.imag,
                   'xkcd:coral pink', alpha=0.03, rasterized=True)

    ax[0].axvline(x=uvlim, linestyle='--', color='gray')
    ax[0].axhline(y=0, linestyle=':', color='darkslategray')
    ax[0].errorbar(1e-3 * vp.rho_uv, 1e3 * vp.vis_prof.real,
                   yerr=1e3 * vp.err_std.real, fmt='o', color='k', ms=3,
                   zorder=0, alpha=0.5, rasterized=True)
    ax[0].set_xlim([0, 150])
    ax[0].set_ylim([-0.1 * 1e3 * vp.vis_prof.real.max(),
                     1.25 * 1e3 * vp.vis_prof.real.max()])
#    ax[0].set_xlim([0, 20])
#    ax[0].set_ylim([-0.7, 0.7])
    ax[0].set_ylabel('real visibilities (mJy)')
    ax[0].set_xlabel('deprojected baseline length (k$\lambda$)')

    ax[1].axvline(x=uvlim, linestyle='--', color='gray')
    ax[1].axhline(y=0, linestyle=':', color='darkslategray')
    ax[1].errorbar(1e-3 * vp.rho_uv, 1e3 * vp.vis_prof.imag,
                   yerr=1e3 * vp.err_std.real, fmt='o', color='k', ms=3,
                   zorder=0, alpha=0.5, rasterized=True)
    ax[1].set_xlim([0, 150])
    ax[1].set_ylim([-0.5 * 1.35 * 1e3 * vp.vis_prof.real.max(),
                     0.5 * 1.35 * 1e3 * vp.vis_prof.real.max()])
#    ax[1].set_xlim([0, 20])
#    ax[1].set_ylim([-0.7, 0.7])
    ax[1].set_ylabel('imag visibilities (mJy)')
    ax[1].set_xlabel('deprojected baseline length (k$\lambda$)')

    fig.savefig('figs/'+outfile+'.visprof.png')
    fig.clf()
