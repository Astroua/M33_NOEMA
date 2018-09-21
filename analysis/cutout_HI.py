
'''
Save a version of the 14B-088 HI cube centered on the NOEMA cube.
'''

from spectral_cube import SpectralCube
import astropy.units as u

from paths import noema_co21_file_dict, hi_14B088_data_path

co_cube = SpectralCube.read(noema_co21_file_dict['Cube'])

hi_cube = SpectralCube.read(hi_14B088_data_path("M33_14B-088_HI.clean.image.GBT_feathered.pbcov_gt_0.5_masked.fits"))

# Pad by one beam width
pad_size = (20 * u.arcsec).to(u.deg)

hi_subcube = hi_cube.subcube(xlo=co_cube.longitude_extrema[0] - pad_size,
                             xhi=co_cube.longitude_extrema[1] + pad_size,
                             ylo=co_cube.latitude_extrema[0] - pad_size,
                             yhi=co_cube.latitude_extrema[1] + pad_size,
                             zhi=-180 * u.km / u.s,
                             zlo='min')

hi_subcube = hi_subcube.to(u.K)

hi_subcube.write(hi_14B088_data_path("M33_14B-088_HI.clean.image.GBT_feathered.pbcov_gt_0.5_masked_noemaco21_slice.fits",
                                     no_check=True))
