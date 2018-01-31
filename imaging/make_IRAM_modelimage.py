
'''
Load the reprojected IRAM cube and mask the edges at the NOEMA map extent.

Then try to get into the correct shape for CASA to use.

Uses the stage 1 of cleaning from line_imaging just to set the coordsys for
the model image.
'''

import numpy as np
from spectral_cube import SpectralCube
import astropy.units as u
from astropy.wcs.utils import proj_plane_pixel_area

from taskinit import iatool

ia = iatool()

iram_cube = SpectralCube.read("/home/ekoch/bigdata/ekoch/M33/co21/noema/m33.co21_iram.noema_regrid.fits")
beam = iram_cube.beam

ia.open("line_imaging/M33-ARM05_stage1.pb")
noema_pb = ia.getchunk().squeeze()
ia.close()

# Convert to Jy/pixel. K -> Jy/beam not yet working in spectral-cube so do it
# by-hand
beam_per_pix = (proj_plane_pixel_area(iram_cube.wcs) * u.deg**2).to(u.sr) / beam.sr
iram_data = ((iram_cube.filled_data[:] / iram_cube.beam.jtok(230.538 * u.GHz))) * beam_per_pix

iram_data[np.where(noema_pb.T == 0.0)] = 0.0

tmp = ia.newimagefromimage(infile="line_imaging/M33-ARM05_stage1.model",
                           outfile="line_imaging/sdmodel_tests/M33-ARM05.iram_model.image",
                           overwrite=True)

# Set the beam
tmp.setrestoringbeam(major="{0}{1}".format(beam.major.value, beam.major.unit),
                     minor="{0}{1}".format(beam.minor.value, beam.minor.unit),
                     pa="{0}{1}".format(beam.pa.value, beam.pa.unit))

# add stokes axis
iram_data = iram_data.T[:, :, np.newaxis, :]
tmp.putchunk(iram_data)
tmp.done()
tmp.close()
