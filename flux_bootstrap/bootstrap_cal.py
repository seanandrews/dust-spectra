import os
import sys
import importlib
import numpy as np
import scipy.constants as sc
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter


# style setups (always deployed)
_ = importlib.import_module('plot_setups')
plt.style.use(['default', '/home/sandrews/mpl_styles/nice_line.mplstyle'])


fig, ax = plt.subplots(constrained_layout=True)

# labels
ax.text(12, 1.9, 'Perley-Butler', ha='right', color='k')
ax.text(16, 2.57, '25A-330 (2025-08-08)', ha='right',
        color='xkcd:bright lavender')
ax.text(15, 2.88, '25A-330 (2025-06-07)', ha='left', color='xkcd:azure')


# load the 3C138 fluxes bootstrapped from joint obs with 3C286
Xnu_a, XF_a, XeF_a = np.loadtxt('3C138_X_20250607.csv', delimiter=',').T
Unu_a, UF_a, UeF_a = np.loadtxt('3C138_U_20250607.csv', delimiter=',').T
Knu_a, KF_a, KeF_a = np.loadtxt('3C138_K_20250607.csv', delimiter=',').T
mjd_a = 5255971200.
X_scl, U_scl, K_scl = 1.000, 1.017, 1.029
XF_a *= X_scl
UF_a *= U_scl
KF_a *= K_scl
ax.errorbar(Xnu_a, XF_a, yerr=XeF_a, fmt='.', color='xkcd:navy')
ax.errorbar(Unu_a, UF_a, yerr=UeF_a, fmt='.', color='xkcd:azure')
ax.errorbar(Knu_a, KF_a, yerr=KeF_a, fmt='.', color='xkcd:aqua')


# load the 3C138 fluxes bootstrapped from joint obs with 3C286
Xnu_b, XF_b, XeF_b = np.loadtxt('3C138_X_20250808.csv', delimiter=',').T
Unu_b, UF_b, UeF_b = np.loadtxt('3C138_U_20250808.csv', delimiter=',').T
Knu_b, KF_b, KeF_b = np.loadtxt('3C138_K_20250808.csv', delimiter=',').T
print(Knu_b.shape)
mjd_b = 5261328000.
X_scl, U_scl = 1.000, 0.993
K_scl = np.ones_like(Knu_b)
K_scl[32:47] = 0.982
K_scl[47:64] = 0.972
K_scl[0:16] = 0.975
K_scl[16:32] = 0.990
XF_b *= X_scl
UF_b *= U_scl
KF_b *= K_scl
ax.errorbar(Xnu_b, XF_b, yerr=XeF_b, fmt='.', color='xkcd:coral pink')
ax.errorbar(Unu_b, UF_b, yerr=UeF_b, fmt='.', color='xkcd:cerise')
ax.errorbar(Knu_b, KF_b, yerr=KeF_b, fmt='.', color='xkcd:bright lavender')


# load the Perley-Butler model, applied by the pipeline
pb_Xspw, pb_Xnu, pb_XF = np.loadtxt('3C138_X_pipeline.txt').T
pb_Uspw, pb_Unu, pb_UF = np.loadtxt('3C138_U_pipeline.txt').T
pb_Kspw, pb_Knu, pb_KF = np.loadtxt('3C138_K_pipeline.txt').T
ax.plot(pb_Xnu[np.argsort(pb_Xnu)], pb_XF[np.argsort(pb_Xnu)], '-k')
ax.plot(pb_Unu[np.argsort(pb_Unu)], pb_UF[np.argsort(pb_Unu)], '-k')
ax.plot(pb_Knu[np.argsort(pb_Knu)], pb_KF[np.argsort(pb_Knu)], '-k')


# compute and group the calfactors; export for use in CASA scripts
""" NEED TO FIX K-band ORDERING!!! """
calfact_XF = np.sqrt(np.column_stack((pb_XF / XF_a, pb_XF / XF_b)))
calfact_UF = np.sqrt(np.column_stack((pb_UF / UF_a, pb_UF / UF_b)))
#calfact_KF = np.sqrt(np.column_stack((pb_KF / KF_a, pb_KF / KF_b)))
mjd = np.stack((mjd_a, mjd_b))
np.savez('3C138_X.npz', spw=pb_Xspw, nu=pb_Xnu, calfact=calfact_XF, mjd=mjd)
np.savez('3C138_U.npz', spw=pb_Uspw, nu=pb_Unu, calfact=calfact_UF, mjd=mjd)
#np.savez('3C138_K.npz', spw=pb_Kspw, nu=pb_Knu, calfact=calfact_KF, mjd=mjd)

ax.set_xlim([7, 27])
ax.set_xticks([8, 10, 12, 14, 16, 18, 20, 22, 24, 26])
ax.set_ylim([1, 3.5])
ax.set_xlabel('frequency (GHz)', fontsize=10)
ax.set_ylabel('flux density (Jy)', fontsize=10)

plt.savefig('bootstrap.pdf')
fig.clf()



""" TEST THE INTERPOLATOR """
from scipy.interpolate import interp1d

inp_mjd = mjd_a + 250 * 3600 * 24

cfint = interp1d(mjd, calfact_XF, axis=1, kind='linear', bounds_error=False,
                 fill_value=(calfact_XF[:,0], calfact_XF[:,-1]))


fig, ax = plt.subplots(constrained_layout=True)

ax.plot(pb_Xnu, calfact_XF[:,0], '.', color='xkcd:cherry')
ax.plot(pb_Xnu, calfact_XF[:,-1], '.', color='xkcd:grape')

ax.plot(pb_Xnu, cfint(inp_mjd), '.', color='xkcd:gray')


ax.set_xlim([7, 27])
ax.set_xticks([8, 10, 12, 14, 16, 18, 20, 22, 24, 26])
ax.set_ylim([0.8, 1.1])
ax.set_xlabel('frequency (GHz)', fontsize=10)
ax.set_ylabel('cal_factor (Jy)', fontsize=10)

plt.savefig('test.pdf')
fig.clf()
