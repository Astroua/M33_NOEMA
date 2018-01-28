
'''
Test to see if there is an offset in intensity within the uv-overlap region

Compare when matched at the IRAM 2.6 km/s spectral resolution and at the
0.5 km/s of the IRAM data

'''

import numpy as np
from spectral_cube import SpectralCube
import astropy.units as u
import scipy.ndimage as nd
from uvcombine.scale_factor import find_scale_factor

from paths import iram_matched_data_path, noema_data_path
from constants import co21_freq

from cube_analysis.feather_cubes import feather_compare_cube


noema_cube = SpectralCube.read(noema_data_path('M33-ARM26.image.pbcor.fits'))
iram_cube = SpectralCube.read(iram_matched_data_path("m33.co21_iram.noema_regrid.spatial.fits"))

# Also need the pb map. It is constant across the channels so grab the first
# channel
noema_pb = SpectralCube.read(noema_data_path('M33-ARM05.pb.fits'))[0]

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
LAS = (1.18 * (co21_freq.to(u.m, u.spectral()) / min_baseline) * u.rad).to(u.deg)

# Only compare channels with signal in them
good_chans = slice(11, 26)

radii, ratios, highres_pts, lowres_pts = \
    feather_compare_cube(noema_cube[good_chans],
                         iram_cube[good_chans], LAS,
                         lowresfwhm=None,
                         restfreq=co21_freq,
                         verbose=True, num_cores=1, chunk=150,
                         weights=weight_arr)

sfact, sfact_stderr = \
    find_scale_factor(np.hstack(lowres_pts), np.hstack(highres_pts),
                      method='distrib', verbose=True)

print("{0}+/-{1}".format(sfact, sfact_stderr))
# 0.556870076298+/-0.0181629468365
# There's a large discrepancy between the data sets.
# The IRAM data appear to have twice the flux of NOEMA in the overlap region.
