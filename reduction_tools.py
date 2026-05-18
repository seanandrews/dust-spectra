from casatools import table
import numpy as np


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


# tool for getting optimal image parameters
def imparamcalc(inpms):
    su = casatools.synthesisutils()

    numSpws = []
    tb = casatools.table()
    tb.open(inpms+'/SPECTRAL_WINDOW')
    maxfreq = max(tb.getcol('REF_FREQUENCY'))
    minfreq = min(tb.getcol('REF_FREQUENCY'))
    numSpws.append(len(tb.getcol('REF_FREQUENCY')))
    tb.close()

    ms = casatools.ms()
    ms.open(inpms)
    uv_range = ms.range(["uvdist"])
    maxuv = (uv_range["uvdist"][1])
    ms.close()

    c = 2.997925e8
    wave = c / maxfreq
    cellsize = 206265. * wave / maxuv / 5.0
    mycell = str(cellsize) + 'arcsec'
#    print("Cell size calculated: ",mycell)
    antsize = 25.0
    fwhm = 206265. * c / minfreq / antsize
    myimsize = max(200, su.getOptimumSize(int(fwhm * 2.0 / cellsize)))
#    print("Imsize calculated: ", myimsize)
    return mycell, myimsize


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


def export_vis(visname, outname):
    # get the data tables out of the MS file
    tb.open(visname)
    data = np.squeeze(tb.getcol("DATA"))
    flag = np.squeeze(tb.getcol("FLAG"))
    uvw = tb.getcol("UVW")
    weight = tb.getcol("WEIGHT")
    spwid = tb.getcol("DATA_DESC_ID")
    tb.close()

    # get the frequency information
    tb.open(visname+'/SPECTRAL_WINDOW')
    freqlist = np.squeeze(tb.getcol("CHAN_FREQ"))
    tb.close()

    # remove lingering flagged columns
    good = np.squeeze(np.any(flag, axis=0) == False)
    data = data[:,good]
    weight = weight[:,good]
    uvw = uvw[:,good]
    spwid = spwid[good]

    # average the polarizations
    Re = np.sum(data.real * weight, axis=0) / np.sum(weight, axis=0)
    Im = np.sum(data.imag * weight, axis=0) / np.sum(weight, axis=0)
    vis = Re + 1j*Im
    wgt = np.sum(weight, axis=0)

    # associate each datapoint with a frequency
    get_freq = lambda ispw: freqlist[ispw]
    freqs = get_freq(spwid)

    # (u,v) positions in wavelengths
    u, v = uvw[0,:] * freqs / 2.9979e8, uvw[1,:] * freqs / 2.9979e8

    # output to a numpy save file
    np.savez(outname, u=u, v=v, nu=freqs, Vis=vis, Wgt=wgt)
