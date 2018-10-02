
'''
Save a version of the IRAM 30-m cube centered on the NOEMA cube (w/o regridding).
'''

from spectral_cube import SpectralCube
from astropy.io import fits
import astropy.units as u

from paths import noema_co21_file_dict, iram_data_path, iram_matched_data_path

co_cube = SpectralCube.read(noema_co21_file_dict['Cube'])

iram_cube = SpectralCube.read(iram_data_path("m33.co21_iram.fits"))
iram_mask = fits.open(iram_data_path('m33.co21_iram_source_mask.fits'))[0].data > 0
iram_cube = iram_cube.with_mask(iram_mask)

del iram_mask

# Pad by one beam width
pad_size = (20 * u.arcsec).to(u.deg)

iram_subcube = iram_cube.subcube(xlo=co_cube.longitude_extrema[0] - pad_size,
                                 xhi=co_cube.longitude_extrema[1] + pad_size,
                                 ylo=co_cube.latitude_extrema[0] - pad_size,
                                 yhi=co_cube.latitude_extrema[1] + pad_size,
                                 zhi=-180 * u.km / u.s,
                                 zlo=-90 * u.km / u.s)

iram_subcube.write(iram_matched_data_path("m33.co21_iram.noema_spatialregion.fits",
                                          no_check=True))
