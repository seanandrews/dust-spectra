from casatools import table
import numpy as np
from datetime import datetime, timedelta


def mjd_to_decimal_year(mjd):
    # convert MJD in s to year
    mjd /= (24 * 3600)

    # MJD epoch is 1858-11-17
    ref_date = datetime(1858, 11, 17)
    dt = ref_date + timedelta(days=mjd)

    # Calculate start and end of the current year
    year_start = datetime(dt.year, 1, 1)
    year_end = datetime(dt.year + 1, 1, 1)

    # Calculate fraction: (time passed in year) / (total time in year)
    year_fraction = (dt - year_start) / (year_end - year_start)
    return dt.year + year_fraction



def dd_to_dms(dd):
    # Determine the sign and work with the absolute value
    is_positive = dd >= 0
    dd = abs(dd)

    # Calculate minutes and seconds using total seconds
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)

    # Restore the sign to the degrees component
    degrees = degrees if is_positive else -degrees

    return (int(degrees), int(minutes), round(seconds, 3))



def pm_corr(dt_epoch, RA, DEC, mu_RA, mu_DEC):
    # load input coordinates and proper motions
    xx, yy, mu_x, mu_y = RA, DEC, mu_RA, mu_DEC

    # compute corrected RA and DEC in decimal degrees
    dms = [1, 60, 3600]
    yd = np.sum(np.array([float(j) for j in DEC.split(":")]) / dms)
    yc = yd + (dt_epoch * 1e-3 * mu_DEC / 3600)
    xd = np.sum(np.array([float(j) for j in RA.split(":")]) * 15 / dms)
    xc = xd + (dt_epoch * 1e-3 * mu_RA / (np.cos(np.radians(yd)) * 3600))

    # convert back to strings in CRTF
    xx_ = dd_to_dms(xc / 15)
    yy_ = dd_to_dms(yc)
    ra_delim = ['h', 'm', 's']
    m_xx = "".join([str(xx_[j]).zfill(2)+ra_delim[j] for j in range(len(xx_))])
    m_yy = ".".join([str(j).zfill(2) for j in yy_])

    return m_xx, m_yy



def has_corrected_column(ms_path):
    tb = table()
    try:
        # Open the main table of the measurement set
        tb.open(ms_path)

        # Get all column names
        colnames = tb.colnames()

        # Check if 'CORRECTED_DATA' is in the list
        return 'CORRECTED_DATA' in colnames

    except Exception as e:
        print(f"Error accessing MS table: {e}")
        return False

    finally:
        # Always close the table tool
        tb.close()


def imparamcalc(msfile, D_ant=12.0):
    # get frequency information
    tb = casatools.table()
    tb.open(msfile+'/SPECTRAL_WINDOW')
    nu = tb.getcol('REF_FREQUENCY')
    nu_avg, nu_min, nu_max = np.average(nu), np.min(nu), np.max(nu)
    tb.close()

    # get the maximum uv distance and compute cellsize
    ms = casatools.ms()
    ms.open(msfile)
    maxuv = ms.range(["uvdist"])["uvdist"][1]
    ms.close()
    cellsize = 206265. * 2.997925e8 / nu_max / maxuv / 5.0
    est_beam = 5 * cellsize
    mycell = str(round(cellsize, 2)) + 'arcsec'

    # get the primary beam and compute image size
    su = casatools.synthesisutils()
    PB = 206265. * 2.997925e8 / nu_min / D_ant
    myimsize = max(200, su.getOptimumSize(int(PB * 1.2 / cellsize)))

    return mycell, myimsize, est_beam, nu_avg, PB


def estimate_SNR(imagename, disk_mask, noise_mask):
    headerlist = imhead(imagename, mode = 'list')
    bmaj = headerlist['beammajor']['value']
    bmin = headerlist['beamminor']['value']
    bpa = headerlist['beampa']['value']
    print(" ")
    print("# %s" % imagename)
    print("# Beam %.3f arcsec x %.3f arcsec (%.2f deg)" % (bmaj, bmin, bpa))
    disk_stats = imstat(imagename = imagename, region = disk_mask)
    disk_flux = disk_stats['flux'][0]
    print("# Flux inside mask: %.1f uJy" % (disk_flux*1e6,))
    peak_intensity = disk_stats['max'][0]
    print("# Peak intensity of source: %.1f uJy/beam" % (peak_intensity*1e6,))
    rms = imstat(imagename = imagename, region = noise_mask)['rms'][0]
    print("# rms: %.1f uJy/beam" % (rms*1e6,))
    SNR = peak_intensity/rms
    print("# Peak SNR: %.1f" % (SNR,))


def export_vis(visname, outname, combine_pol=False):
    # get the tables out of the MS 
    tb.open(visname)
    data = tb.getcol("DATA")
    flag = tb.getcol("FLAG")
    uvw = tb.getcol("UVW")
    spwid = tb.getcol("DATA_DESC_ID")
    cols = tb.colnames()
    if 'WEIGHT_SPECTRUM' in cols:
        weight = tb.getcol("WEIGHT_SPECTRUM")
    else:
        weight = tb.getcol("WEIGHT")
    tb.close()

    # get the frequency information
    tb.open(visname+'/SPECTRAL_WINDOW')
    freqlist = tb.getcol("CHAN_FREQ")
    tb.close()

    # array shapes!
    # data, flag = [Npol, Nchan, Nvis] 
    # uvw = [3, Nvis] 
    # weight = [Npol, Nvis]
    # spwid = [Nvis] 
    # freqlist = [Nchan, Nspw]

    # copy the single SPW weights into individual channels (ALMA pipeline does
    # not yet provide channel-dependent weights)
    if len(weight.shape) < len(data.shape):
        weight = np.repeat(weight[:, np.newaxis, :], data.shape[1], axis=1)

    # remove lingering flagged columns (actually, *keep* unflagged columns)
    good = np.any(~flag, axis=(0,1))
    data = data[:,:,good]
    weight = weight[:,:,good]
    uvw = uvw[:,good]
    spwid = spwid[good]

    # associate each datapoint with a frequency: freqs = [Nchan, Nvis]
    get_freq = lambda ispw: freqlist[:,ispw]
    freqs = get_freq(spwid)

    # convert (u,v) positions into wavelength units
    um, vm = uvw[0,:], uvw[1,:]
    u = um[np.newaxis, :] * freqs / 2.9979e8
    v = vm[np.newaxis, :] * freqs / 2.9979e8

    # if requested, average the polarizations
    if combine_pol:
        Re = np.sum(data.real * weight, axis=0) / np.sum(weight, axis=0)
        Im = np.sum(data.imag * weight, axis=0) / np.sum(weight, axis=0)
        vis = Re + 1j*Im
        wgt = np.sum(weight, axis=0)
    else:
        u = np.repeat(u[np.newaxis, :, :], 2, axis=0)
        v = np.repeat(v[np.newaxis, :, :], 2, axis=0)
        freqs = np.repeat(freqs[np.newaxis, :, :], 2, axis=0)
        vis = 1. * data
        wgt = 1. * weight

    # flatten the outputs for simplicity
    u = u.flatten()
    v = v.flatten()
    freqs = freqs.flatten()
    vis = vis.flatten()
    wgt = wgt.flatten()

    # output to a numpy save file
    np.savez(outname, u=u, v=v, nu=freqs, Vis=vis, Wgt=wgt)
