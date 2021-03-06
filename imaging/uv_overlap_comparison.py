
'''
Test to see if there is an offset in intensity within the uv-overlap region

Compare when matched at the IRAM 2.6 km/s spectral resolution and at the
0.5 km/s of the IRAM data

'''

import os
import numpy as np
from spectral_cube import SpectralCube
import astropy.units as u
import scipy.ndimage as nd
from uvcombine.scale_factor import find_scale_factor
from scipy.stats import theilslopes
import matplotlib.pyplot as plt

from paths import iram_matched_data_path, noema_data_path, allfigs_path
from constants import co21_freq
from plotting_styles import onecolumn_figure

from cube_analysis.feather_cubes import feather_compare_cube


figure_folder = allfigs_path("Imaging")
if not os.path.exists(figure_folder):
    os.mkdir(figure_folder)

noema_cube = SpectralCube.read(noema_data_path('M33-ARM05_yclean.tc_final.image.pbcor.K.26regrid.fits'))

iram_cube = SpectralCube.read(iram_matched_data_path("m33.co21_iram.noema_regrid.spatial.fits"))

# Also need the pb map. It is constant across the channels so grab the first
# channel
noema_pb = SpectralCube.read(noema_data_path('yclean_05/M33-ARM05_yclean.tc_final.pb.fits'))[0]

# Define a mask that will be used to smoothly taper the IRAM data near the
# map edges. Otherwise the comparison is dominated by ringing in the Fourier
# transform.
weight_arr = (noema_pb > 0.4).astype(float)

# Taper the edges
weight_arr = nd.gaussian_filter(weight_arr, 10)


# Cut the IRAM cube to the extent of the NOEMA data
iram_cube = iram_cube.spectral_slab(noema_cube.spectral_extrema[0],
                                    noema_cube.spectral_extrema[1])

# Smallest baseline in the NOEMA data is
min_baseline = 15.32 * u.m
LAS = ((co21_freq.to(u.m, u.spectral()) / min_baseline) * u.rad).to(u.deg)
# About 17.5". The resolution of the 30-m data is 12", so there isn't
# much overlap.

# Only compare channels with signal in them
good_chans = slice(11, 26)

radii, ratios, highres_pts, lowres_pts = \
    feather_compare_cube(noema_cube[good_chans],
                         iram_cube[good_chans], LAS,
                         lowresfwhm=None,
                         restfreq=co21_freq,
                         verbose=True, num_cores=1, chunk=150,
                         weights=weight_arr)

onecolumn_figure()

sfact, sfact_stderr = \
    find_scale_factor(np.hstack(lowres_pts), np.hstack(highres_pts),
                      method='distrib', verbose=True)

plt.xlabel("log Ratio (NOEMA / 30-m)")
plt.grid()
plt.tight_layout()
plt.savefig(os.path.join(figure_folder, "NOEMA_30m_overlap_ratio.png"))
plt.savefig(os.path.join(figure_folder, "NOEMA_30m_overlap_ratio.pdf"))
plt.close()

print("{0}+/-{1}".format(sfact, sfact_stderr))
# 0.980326306378+/-0.032036255747
# There's a large discrepancy between the data sets when the Ta* -> Tmb
# conversion. Is applied to the 30-m data. The discrepancy is suspiciously
# the same as the Tmb conversion factor.
# The above ratio and saved plot do NOT have the Tmb conversion factor

# There doesn't appear to be a clear trend with radius, but let's just check

def sentheil_perchan(xvals, yvals, alpha=0.85):

    slope = np.empty((len(xvals)))
    upper_uncert = np.empty((len(xvals)))
    lower_uncert = np.empty((len(xvals)))

    for i, (xval, yval) in enumerate(zip(xvals, yvals)):

        out = theilslopes(yval, x=xval, alpha=alpha)

        slope[i] = out[0]
        upper_uncert[i] = out[3] - out[0]
        lower_uncert[i] = out[0] - out[2]

    return slope, lower_uncert, upper_uncert


ratios = [highres / lowres for highres, lowres in zip(highres_pts, lowres_pts)]

slopes, low_slope, high_slope = \
    sentheil_perchan(radii, ratios)

# Fit for all overlap points
all_slope, inter, all_low_slope, all_high_slope = \
    theilslopes(np.hstack(ratios), x=np.hstack(radii).value)

chans = range(11, 26)

plt.errorbar(chans, slopes,
             yerr=[low_slope, high_slope],
             alpha=0.5)
# plt.plot(chans, slope_lowess_85)
plt.axhline(0, linestyle='--')
plt.axhline(all_slope)
plt.fill_between(chans, all_low_slope, all_high_slope, alpha=0.5)
plt.ylabel("Slope")
plt.xlabel("Channel")
plt.grid()
plt.tight_layout()
plt.savefig(os.path.join(figure_folder, "NOEMA_30m_overlap_ratio_slope.png"))
plt.savefig(os.path.join(figure_folder, "NOEMA_30m_overlap_ratio_slope.pdf"))
plt.close()

# Channel 18 has a severe outlier, but otherwise the slopes are consistent
# with 0+/-0.1. And the intercept is also ~0.5.
