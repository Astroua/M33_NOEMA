
'''
Create a version of the CO cube at the same resolution as the IRAM data
'''

from spectral_cube import SpectralCube
import astropy.units as u
from astropy.convolution import Gaussian1DKernel
import numpy as np

from paths import noema_data_path, iram_data_path

# Load the cube
cube = SpectralCube.read(noema_data_path("M33-ARM05_yclean.tc_final.image.pbcor.K.fits"))

# Need to convolve to a common beam
com_beam = cube.beams.common_beam(epsilon=8e-4)
cube = cube.convolve_to(com_beam)

# And the IRAM cube
iram_cube = SpectralCube.read(iram_data_path('m33.co21_iram.fits'))

# Extract out the overlapping velocities
iram_cube = iram_cube.spectral_slab(cube.spectral_extrema[0],
                                    cube.spectral_extrema[1])

targ_res = 2.6 * u.km / u.s
curr_res = 0.5 * u.km / u.s

ratio = (targ_res / curr_res).value

fwhm_factor = np.sqrt(8 * np.log(2))

smcube = cube.spectral_smooth(Gaussian1DKernel(ratio / fwhm_factor))
interp_cube = smcube.spectral_interpolate(iram_cube.spectral_axis,
                                          suppress_smooth_warning=True)

interp_cube.write(noema_data_path('M33-ARM05_yclean.tc_final.image.pbcor.K.26regrid.fits',
                                  no_check=True))
