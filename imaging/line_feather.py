
'''
Feather the IRAM and NOEMA data together.
'''

import numpy as np
from spectral_cube import SpectralCube
import astropy.units as u
import scipy.ndimage as nd

from paths import iram_matched_data_path, noema_data_path
from constants import co21_freq

from cube_analysis.feather_cubes import feather_cube


noema_cube = SpectralCube.read(noema_data_path('M33-ARM05_yclean.tc_final.image.pbcor.K.26regrid.fits'))
iram_cube = SpectralCube.read(iram_matched_data_path("m33.co21_iram.noema_regrid.spatial.fits"))

# Cut the IRAM cube to the extent of the NOEMA data
iram_cube = iram_cube.spectral_slab(noema_cube.spectral_extrema[0],
                                    noema_cube.spectral_extrema[1])

# Convert the NOEMA cube to K
# noema_cube = noema_cube.to(u.K)

# Also need the pb map. It is constant across the channels so grab the first
# channel
noema_pb = SpectralCube.read(noema_data_path('yclean_05/M33-ARM05_yclean.tc_final.pb.fits'))[0]

# Define a mask that will be used to smoothly taper the IRAM data near the
# map edges. Otherwise the comparison is dominated by ringing in the Fourier
# transform.
weight_arr = (noema_pb > 0.4).astype(float)

# Taper the edges
weight_arr = nd.gaussian_filter(weight_arr, 10)

feather_cube(noema_cube, iram_cube,
             verbose=True, save_feather=True,
             save_name=noema_data_path('M33-ARM05_yclean.tc_final.image.pbcor.K.26regrid.feather.fits', no_check=True),
             num_cores=1, chunk=100,
             restfreq=co21_freq,
             weights=weight_arr)


# Now do the same for the 0.5 km/s data

noema_cube = SpectralCube.read(noema_data_path('M33-ARM05_yclean.tc_final.image.pbcor.K.fits'))
iram_cube = SpectralCube.read(iram_matched_data_path("m33.co21_iram.noema_regrid.fits"))

# Convert the NOEMA cube to K
# noema_cube.allow_huge_operations = True
# noema_cube = noema_cube.to(u.K)

feather_cube(noema_cube, iram_cube,
             verbose=True, save_feather=True,
             save_name=noema_data_path('M33-ARM05_yclean.tc_final.image.pbcor.K.feather.fits', no_check=True),
             num_cores=1, chunk=100,
             restfreq=co21_freq,
             weights=weight_arr)
