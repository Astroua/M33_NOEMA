
'''
Compare the flux in the masked NOEMA and 30-m data.
'''

from spectral_cube import SpectralCube
from astropy.io import fits
import numpy as np
import astropy.units as u

from cube_analysis.feather_cubes import flux_recovery

from paths import noema_co21_file_dict, iram_matched_data_path
from constants import co21_freq

noema_cube = SpectralCube.read(noema_co21_file_dict['Cube'])
noema_mask = fits.open(noema_co21_file_dict['Source_Mask'])
noema_cube = noema_cube.with_mask(noema_mask[0].data > 0)

noema_cube.allow_huge_operations = True

iram_cube = SpectralCube.read(iram_matched_data_path("m33.co21_iram.noema_spatialregion.fits"))

# Remove padded area
iram_subcube = iram_cube.subcube(xlo=iram_cube.longitude_extrema[0],
                                 xhi=iram_cube.longitude_extrema[1],
                                 ylo=iram_cube.latitude_extrema[0],
                                 yhi=iram_cube.latitude_extrema[1])

# iram_subcube = iram_subcube.spectral_interpolate(noema_cube.spectral_axis)

# total_hires, total_lores = flux_recovery(noema_cube, iram_subcube,
#                                          frequency=co21_freq,
#                                          doplot=True)

iram_mom0 = iram_subcube.moment0()
noema_mom0 = noema_cube.moment0()

# Adjust for difference in the pixel area
iram_total = np.nansum(iram_mom0) * (iram_mom0.header['CDELT2'] * u.deg)**2
noema_total = np.nansum(noema_mom0) * (noema_mom0.header['CDELT2'] * u.deg)**2

print("IRAM {0}; NOEMA {1}".format(iram_total, noema_total))
# IRAM 1.35010104124 deg2 K m / s; NOEMA 1.01810349853 deg2 K m / s

print("Flux recovered by NOEMA: {}".format(noema_total / iram_total))
# Flux recovered by NOEMA: 0.75409429919
