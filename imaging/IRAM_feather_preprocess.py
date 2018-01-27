
'''
Get the IRAM CO(2-1) data onto the same grid and check uv-overlap
before feathering.
'''

from spectral_cube import SpectralCube

from cube_analysis.reprojection import reproject_cube

from paths import noema_data_path, iram_data_path, iram_matched_data_path
from constants import beam_eff_30m_druard

# Load the cube
cube = SpectralCube.read(noema_data_path("M33-ARM05.image.pbcor.fits"))

iram_cube = SpectralCube.read(iram_data_path('m33.co21_iram.fits'))


# Make a version with just a spatial reprojection
reproject_cube(iram_data_path('m33.co21_iram.fits'),
               noema_data_path("M33-ARM05.image.pbcor.fits"),
               iram_matched_data_path("m33.co21_iram.noema_regrid.spatial.fits",
                                      no_check=True),
               reproject_type='spatial')

# And another with reprojecting spectrally too.
reproject_cube(iram_data_path('m33.co21_iram.fits'),
               noema_data_path("M33-ARM05.image.pbcor.fits"),
               iram_matched_data_path("m33.co21_iram.noema_regrid.fits",
                                      no_check=True),
               reproject_type='all')

# Open each cube and apply the Ta* -> Tmb correction

rep_spat_cube = SpectralCube.read(iram_matched_data_path("m33.co21_iram.noema_regrid.spatial.fits"))
rep_spat_cube.allow_huge_operations=True
rep_spat_cube /= beam_eff_30m_druard
rep_spat_cube.write(iram_matched_data_path("m33.co21_iram.noema_regrid.spatial.fits"),
                    overwrite=True)

del rep_spat_cube

rep_cube = SpectralCube.read(iram_matched_data_path("m33.co21_iram.noema_regrid.fits"))
rep_cube.allow_huge_operations=True
rep_cube /= beam_eff_30m_druard

del rep_cube
