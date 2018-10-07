
'''
Create a version of the NOEMA data corrected for galactic rotation.
'''

from spectral_cube import SpectralCube, Projection
from astropy.io import fits
import astropy.units as u
from galaxies import Galaxy
from astropy.table import Table
import os
import numpy as np

from cube_analysis.rotation_curves.curve_fitting import vcirc_brandt
from cube_analysis.rotation_curves import update_galaxy_params
from cube_analysis.spectra_shifter import cube_shifter

from paths import noema_co21_file_dict, hi_14B088_data_path, noema_data_path

num_cores = 4

# Set the number of spectra to load in and operate on at once.
chunk_size = 50000

gal = Galaxy("M33")

# Make sure this version has 840 kpc as the distance
assert gal.distance == 840 * u.kpc

cube = SpectralCube.read(noema_co21_file_dict['Cube'])

# Create rotation velocities over the cube region
tab = Table.read(hi_14B088_data_path("diskfit_peakvels_noasymm_noradial_nowarp_output/rad.out.params.csv"))

update_galaxy_params(gal, tab)

hi_model = Projection.from_hdu(fits.open(hi_14B088_data_path("diskfit_peakvels_noasymm_noradial_nowarp_output/rad.fitmod.fits")))

radii = gal.radius(header=cube.header).to(u.kpc)
pas = gal.position_angles(header=cube.header)

# Convert 3'' pix to kpc
rmax_kpc = tab['fit_rmax'] * (3 * u.arcsec).to(u.rad).value * \
    gal.distance.to(u.kpc)

vmax_kms = tab['fit_vmax'] * u.km / u.s

pars = [0.56, 110.0, 12.0]

# vcirc = vcirc_brandt(radii, *[tab['fit_n'], vmax_kms, rmax_kpc]) * \
#     u.km / u.s
vcirc = vcirc_brandt(radii.value, *pars) * u.km / u.s

smooth_model = vcirc * np.cos(pas) * np.sin(gal.inclination).value + \
    tab['Vsys'] * u.km / u.s

# Make sure the model is correct by comparing with the HI fit range
# spat_mask_0 = np.logical_and(hi_model.spatial_coordinate_map[1] >= cube.longitude_extrema[0],
#                              hi_model.spatial_coordinate_map[1] <= cube.longitude_extrema[1])
# spat_mask_1 = np.logical_and(hi_model.spatial_coordinate_map[0] >= cube.latitude_extrema[0],
#                              hi_model.spatial_coordinate_map[0] <= cube.latitude_extrema[1])
# spat_mask = np.logical_and(spat_mask_0, spat_mask_1)

# hi_model_noema = hi_model[spat_mask]

# hi_model_reproj = hi_model.reproject(header=cube[0].header)

# Shift with the first moment
filename = os.path.splitext(noema_co21_file_dict['Cube'])[0]

print("Shifting w/ rotation velocity")
rotsub_cube_name = "{}.rotation_corrected.fits".format(filename)
cube_shifter(cube, smooth_model, smooth_model.mean(), save_shifted=True,
             save_name=noema_data_path(rotsub_cube_name, no_check=True),
             return_spectra=False, verbose=True, num_cores=num_cores,
             chunk_size=chunk_size, pad_edges=True)

# Also shift the signal mask to match those shifted here.
print("Shifting mask w/ rotation velocity")
mask = SpectralCube.read(noema_co21_file_dict['Source_Mask'])

rotsub_mask_name = "{}_source_mask.rotation_corrected.fits".format(filename)
cube_shifter(mask, smooth_model, smooth_model.mean(), save_shifted=True,
             save_name=noema_data_path(rotsub_mask_name, no_check=True),
             return_spectra=False, verbose=True, num_cores=num_cores,
             is_mask=True, chunk_size=chunk_size, pad_edges=True)
