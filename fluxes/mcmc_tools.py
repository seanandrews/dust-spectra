import os
import sys
import numpy as np
from scipy import stats

""" 
    These autocorrelation tools come directly out of emcee, so I can use them
    after the fact in a reproducible way.
"""
def next_pow_two(n):
    i = 1
    while i < n:
        i = i << 1
    return i

def autocorr_func_1d(x, norm=True):
    x = np.atleast_1d(x)
    if len(x.shape) != 1:
        raise ValueError("invalid dimensions for 1D autocorr function")
    n = next_pow_two(len(x))

    # Compute the FFT and then (from that) the auto-correlation function
    f = np.fft.fft(x - np.mean(x), n=2 * n)
    acf = np.fft.ifft(f * np.conjugate(f))[: len(x)].real
    acf /= 4 * n

    # Optionally normalize
    if norm:
        acf /= acf[0]

    return acf

# Automated windowing procedure following Sokal (1989)
def auto_window(taus, c):
    m = np.arange(len(taus)) < c * taus
    if np.any(m):
        return np.argmin(m)
    return len(taus) - 1

# Following suggestion from Goodman & Weare (2010)
def autocorr_gw2010(y, c=5.0):
    f = autocorr_func_1d(np.mean(y, axis=0))
    taus = 2.0 * np.cumsum(f) - 1.0
    window = auto_window(taus, c)
    return taus[window]

# Following @fardal suggestion on emcee github
def autocorr_new(y, c=5.0):
    f = np.zeros(y.shape[1])
    for yy in y:
        f += autocorr_func_1d(yy)
    f /= len(y)
    taus = 2.0 * np.cumsum(f) - 1.0
    window = auto_window(taus, c)
    return taus[window]


def mcmc_out(samples, logposts, 
             maxtau=1500, cutfactor=50, burnfactor=10, thinfactor=1,
             return_more=False, outliers=True):

    # samples shape
    nstep, nwalk, ndim = samples.shape

    # identify outlier walkers (based on lnprob)
    if outliers:
        ncut = round(nstep / cutfactor)
        dev_ = (np.median(logposts[ncut:,:], axis=0) - \
                np.median(logposts[ncut:,:])) / np.std(logposts[ncut:,:])
        out_ix = np.where(np.abs(dev_) >= 2)

        # reduce 
        samples  = np.delete(samples, out_ix, axis=1)
        logposts = np.delete(logposts, out_ix, axis=1)

    # compute autocorrelation times
    tau_ = np.array([autocorr_new(samples[:-1,:,ix].T)
                     for ix in range(samples.shape[-1])])

    # burn and thin
    tau_max = np.min([tau_.max(), maxtau])
    print(tau_max, tau_.max(), maxtau)
    nburn = round(burnfactor * tau_max)
    nthin = round(thinfactor * tau_max)
    out_ = samples[nburn::nthin,:,:]
    s = list(out_.shape[1:])
    s[0] = np.prod(out_.shape[:2])
    flat_chain = out_.reshape(s)

    pout_ = logposts[nburn::nthin,:]
    s = list(pout_.shape[1:])
    s[0] = np.prod(pout_.shape)
    flat_posts = pout_.reshape(s)

    if return_more:
        return flat_chain, flat_posts, tau_max
    else:
        return flat_chain


def post_summary(p, prec=0.1, mu='peak', CIlevs=[84.135, 15.865]):

    # calculate percentiles as designated
    CI_p = np.percentile(p, CIlevs)

    # find peak of posterior
    if (mu == 'peak'):
        kde_p = stats.gaussian_kde(p)
        ndisc = np.int(np.round((CI_p[0] - CI_p[1]) / prec))
        x_p = np.linspace(CI_p[1], CI_p[0], ndisc)
        pk_p = x_p[np.argmax(kde_p.evaluate(x_p))]
    else:
        pk_p = np.percentile(p, 50.)

    # return the peak and upper, lower 1-sigma
    return (pk_p, CI_p[0]-pk_p, pk_p-CI_p[1])
