
'''
Check if the data are offset.
'''

import numpy as np
import astropy.units as u
from spectral_cube import SpectralCube
from astropy.table import Table

from cube_analysis.register_cubes import cube_registration, spatial_shift_cube

from paths import noema_data_path, iram_matched_data_path
from constants import co21_freq

iram_cube = SpectralCube.read(iram_matched_data_path("m33.co21_iram.noema_regrid.fits"))
noema_cube = SpectralCube.read(noema_data_path("M33-ARM05.image.pbcor.fits"))

noema_cube.allow_huge_operations = True
noema_cube = noema_cube.to(u.K)

num_cores = 3

good_chans = slice(60, 110)

# Now find the offsets for each
offset = cube_registration(iram_cube, noema_cube, num_cores=num_cores,
                           restfreq=co21_freq)

# Offsets are still all over the place. Revisit with a less
