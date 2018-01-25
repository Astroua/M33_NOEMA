
'''
Image and deconvolve the 0.5 km/s data.

Do imaging in two steps:
 1) Multi-scale clean all peaks down to 5 sigma
 2) Beam size clean down to 2 sigma
'''

from tclean import tclean

import numpy as np
from scipy import ndimage as nd
from radio_beam import Beam, EllipticalTophat2DKernel
from spectral_cube import SpectralCube
import astropy.units as u
from astropy import units as u

# noise level at 0.025 Jy/beam
# Multi-scale clean down to 5 sigma

sigma = 0.025
ms_thresh = sigma * 5

tclean(vis='meas_sets/M33-ARM05.ms',
       datacolumn='data',
       imagename="line_imaging/M33-ARM05",
       field='M33*',
       imsize=[1024, 700],
       cell='0.2arcsec',
       specmode='cube',
       start=1,
       width=1,
       nchan=-1,
       startmodel=None,
       gridder='mosaic',
       weighting='natural',
       niter=100000,
       threshold='{}Jy/beam'.format(ms_thresh),
       phasecenter='J2000 01h33m33.191 +30d32m06.720',
       restfreq='230.538GHz',
       outframe='LSRK',
       pblimit=0.1,
       usemask='pb',
       pbmask=0.15,
       mask=None,
       deconvolver='multiscale',
       scales=[0, 8, 16],
       pbcor=False,
       chanchunks=-1)

# Make separate versions
outputs = ['image', 'mask', 'model', 'pb', 'psf', 'residual', 'sumwt',
           'weight']

for suff in outputs:
    old_file = "line_imaging/M33-ARM05.{}".format(suff)
    new_file = "line_imaging/M33-ARM05_stage1.{}".format(suff)

    ia.open(old_file)
    old_arr = ia.getchunk()
    ia.close()

    tmp = ia.newimagefromimage(infile=old_file,
                               outfile=new_file,
                               overwrite=False)

    tmp.putchunk(old_arr.astype('float'))
    tmp.close()
    tmp.done()
    ia.done()

# Restore stage 1
# for suff in outputs:
#     old_file = "line_imaging/M33-ARM05_stage1.{}".format(suff)
#     new_file = "line_imaging/M33-ARM05.{}".format(suff)

#     ia.open(old_file)
#     old_arr = ia.getchunk()
#     ia.close()

#     tmp = ia.newimagefromimage(infile=old_file,
#                                outfile=new_file,
#                                overwrite=False)

#     tmp.putchunk(old_arr.astype('float'))
#     tmp.close()
#     tmp.done()
#     ia.done()

# Create a mask

ia.open("line_imaging/M33-ARM05_stage1.image")
image = ia.getchunk(dropdeg=True)
beam_props = ia.restoringbeam()
ia.close()
ia.done()

# Load in the pb and mask
# ia.open("line_imaging/M33-ARM05.pb")
# pb_cov = ia.getchunk(dropdeg=True)
# ia.close()
# ia.done()

ia.open("line_imaging/M33-ARM05_stage1.mask")
pb_mask = ia.getchunk(dropdeg=True)
ia.close()
ia.done()

nhigh = 3
nlow = 1.5

good_mask = np.zeros(pb_mask.shape, dtype=bool)

nchan = image.shape[-1]

# Loop through each channel
for i in range(nchan):

    image_plane = image[..., i]
    # pb_cov_plane = pb_cov[..., i]
    pb_mask_plane = pb_mask[..., i].astype(bool)

    good_mask_plane = np.zeros_like(pb_mask_plane)

    low_mask = np.logical_and(image_plane >= nlow * sigma,
                              pb_mask_plane)
    high_mask = np.logical_and(image_plane >= nhigh * sigma,
                               pb_mask_plane)

    low_labels, num_low = nd.label(low_mask, np.ones((3, 3)))

    # Find if there are any valid pixels in the high mask
    high_low_sum = nd.sum(high_mask, low_labels, range(1, num_low + 1))
    low_low_sum = nd.sum(low_mask, low_labels, range(1, num_low + 1))

    major = beam_props['beams']['*{}'.format(i)]['*0']["major"]["value"] * \
        u.Unit(beam_props['beams']['*{}'.format(i)]['*0']["major"]["unit"])
    minor = beam_props['beams']['*{}'.format(i)]['*0']["minor"]["value"] * \
        u.Unit(beam_props['beams']['*{}'.format(i)]['*0']["minor"]["unit"])
    pa = beam_props['beams']['*{}'.format(i)]['*0']["positionangle"]["value"] * \
        u.Unit(beam_props['beams']['*{}'.format(i)]['*0']["positionangle"]["unit"])

    pixscale = (0.2 * u.arcsec).to(u.deg)

    gauss_to_top = np.sqrt(2)
    SIGMA_TO_FWHM = np.sqrt(8 * np.log(2))

    maj_eff = gauss_to_top * major.to(u.deg) / \
        (pixscale * SIGMA_TO_FWHM)
    min_eff = gauss_to_top * minor.to(u.deg) / \
        (pixscale * SIGMA_TO_FWHM)

    # let the beam object be slightly smaller
    kern = EllipticalTophat2DKernel(0.8 * maj_eff.value,
                                    0.8 * min_eff.value,
                                    pa.to(u.radian).value)

    min_pix = (kern.array > 0).sum()

    # Require 1/4 of min_pix be above the high mask
    # and require min_pix in the low_mask
    for lab in range(1, num_low + 1):
        high_check = high_low_sum[lab - 1] >= 0.25 * min_pix
        low_check = low_low_sum[lab - 1] >= min_pix
        if high_check & low_check:
            valid_pts = np.where(low_labels == lab)
            good_mask_plane[valid_pts] = True

    good_mask_plane = nd.binary_opening(good_mask_plane, kern.array > 0)
    good_mask_plane = nd.binary_closing(good_mask_plane, kern.array > 0)
    # Increase to slightly larger than a beam for the clean mask
    good_mask_plane = nd.binary_dilation(good_mask_plane, kern.array > 0)

    good_mask[..., i] = good_mask_plane

print("Done Spatial Search")

# Now enforce spectral requirement of 3 connected pixels
spat_posns = np.where(good_mask.sum(2))
for y, x in zip(*spat_posns):
    if good_mask[y, x].sum() < 3:
        good_mask[y, x] = False
        continue

    # Calculate sum of connected objects
    labs, n_con = nd.label(good_mask[y, x])

    conn_objs = nd.find_objects(labs)

    conn_sums = nd.sum(good_mask[y, x], labs, range(1, n_con + 1))

    if (conn_sums >= 3).all():
        continue

    for i in range(1, n_con + 1):
        if conn_sums[i - 1] < 3:
            good_mask[y, x, conn_objs[i - 1][0]] = False

# Dilate the mask by ~ the beam size to include fainter structure and
# avoid biasing clean components near the edge
niter = np.ceil(maj_eff.value).astype(int)

good_mask = nd.binary_dilation(good_mask,
                               structure=(kern.array > 0)[..., np.newaxis],
                               iterations=niter)

# And expand by 1 channel in each direction

good_mask = nd.binary_dilation(good_mask,
                               structure=np.ones((1, 1, 3)))

tmp = ia.newimagefromimage(infile="line_imaging/M33-ARM05.image",
                           outfile="line_imaging/M33-ARM05.sig_mask",
                           overwrite=False)
# add stokes axis
good_mask = good_mask[:, :, np.newaxis, :]
tmp.putchunk(good_mask.astype('int16'))
tmp.done()

del good_mask, image, pb_mask  # pb_cov,

# Deep clean w/o multi-scale
point_thresh = 2 * sigma

rmtables("line_imaging/M33-ARM05.mask")

tclean(vis='meas_sets/M33-ARM05.ms',
       datacolumn='data',
       imagename="line_imaging/M33-ARM05",
       field='M33*',
       imsize=[1024, 700],
       cell='0.2arcsec',
       specmode='cube',
       start=1,
       width=1,
       nchan=-1,
       startmodel=None,
       gridder='mosaic',
       weighting='natural',
       niter=500000,
       threshold='{}Jy/beam'.format(point_thresh),
       phasecenter='J2000 01h33m33.191 +30d32m06.720',
       restfreq='230.538GHz',
       outframe='LSRK',
       pblimit=0.1,
       usemask='user',
       mask="line_imaging/M33-ARM05.sig_mask",
       deconvolver='hogbom',
       pbcor=False,
       chanchunks=-1,
       calcres=False,
       calcpsf=False,
       cyclefactor=2.0)

for suff in outputs:
    old_file = "line_imaging/M33-ARM05.{}".format(suff)
    new_file = "line_imaging/M33-ARM05_stage2.{}".format(suff)

    ia.open(old_file)
    old_arr = ia.getchunk()
    ia.close()

    tmp = ia.newimagefromimage(infile=old_file,
                               outfile=new_file,
                               overwrite=False)

    tmp.putchunk(old_arr.astype('float'))
    tmp.close()
    tmp.done()
    ia.done()

impbcor(imagename="line_imaging/M33-ARM05.image",
        pbimage="line_imaging/M33-ARM05.pb",
        outfile="line_imaging/M33-ARM05.image.pbcor")

exportfits(imagename="line_imaging/M33-ARM05.image.pbcor",
           fitsimage="line_imaging/M33-ARM05.image.pbcor.fits",
           history=False, dropdeg=True)

# Because tclean wants the telescope to be IRAMPDB to get the dish model,
# and the rest of casa seems to want IRAM PDB to get the locations,
# the cube has a frequency axis instead of velocity. But the data are already
# in LSRK, so we can just use spectral-cube to overwrite a velocity version
cube = SpectralCube.read('line_imaging/M33-ARM05.image.pbcor.fits')
cube = cube.with_spectral_unit(u.m / u.s, velocity_convention='radio',
                               rest_value=230.538 * u.GHz)
cube.write('line_imaging/M33-ARM05.image.pbcor.fits',
           overwrite=True)
