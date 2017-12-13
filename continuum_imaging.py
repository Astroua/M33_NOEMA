
import numpy as np
from scipy import ndimage as nd
from radio_beam import Beam, EllipticalTophat2DKernel
from astropy import units as u


clean(vis='meas_sets/M33-ARMcont.ms',
      imagename="imaging/M33-ARMcont_dirty",
      field='M33*',
      imsize=[1024, 700],
      cell='0.2arcsec',
      mode='mfs',
      phasecenter='J2000 01h33m33.191 +30d32m06.720',
      imagermode='mosaic',
      ftmachine='mosaic',
      weighting='natural',
      niter=0,
      gain=0.2,
      threshold='70mJy/beam',
      mask=None,
      minpb=0.2,
      pbcor=True,
      interactive=False
      )

# Strategy: clean down to 5 sigma within a pb limit of ~0.4-0.5
# Threshold on the first image and extend the mask to 2-3-sigma
# regions with a 5-sigma detection. Then clean to ~2-3 sigma.

# Noise level is 0.3 mJy/bm.

clean(vis='meas_sets/M33-ARMcont.ms',
      imagename="imaging/M33-ARMcont",
      field='M33*',
      imsize=[1024, 700],
      cell='0.2arcsec',
      mode='mfs',
      phasecenter='J2000 01h33m33.191 +30d32m06.720',
      imagermode='mosaic',
      ftmachine='mosaic',
      weighting='natural',
      niter=10000,
      gain=0.1,
      threshold='1.5mJy/beam',
      mask=None,
      minpb=0.2,
      pbcor=False,
      interactive=False
      )

# Create a mask


ia.open("imaging/M33-ARMcont.image")
image = ia.getchunk(dropdeg=True)
beam_props = ia.restoringbeam()
ia.done()

# Load in the pb mask
ia.open("imaging/M33-ARMcont.flux.pbcoverage")
pb_cov = ia.getchunk(dropdeg=True)
ia.done()

pb_mask = pb_cov >= 0.48

sigma = 3e-4
nhigh = 5
nlow = 2

low_mask = np.logical_and((image / pb_cov) >= nlow * sigma, pb_mask)
high_mask = np.logical_and((image / pb_cov) >= nhigh * sigma, pb_mask)

low_labels, num_low = nd.label(low_mask, np.ones((3, 3)))

# Find if there are any valid pixels in the high mask
high_low_sum = nd.sum(high_mask, low_labels, range(1, num_low + 1))

good_mask = np.zeros_like(low_mask)

min_pix = 4

for lab in range(1, num_low + 1):
    if high_low_sum[lab - 1] >= min_pix:
        valid_pts = np.where(low_labels == lab)
        good_mask[valid_pts] = True

# Get the beam from the image
# Not working yet in CASA 5.X
# beam = Beam.from_casa_image("imaging/M33-ARMcont.image")
# kern = Beam.as_tophat_kernel(pixscale)

major = beam_props["major"]["value"] * \
    u.Unit(beam_props["major"]["unit"])
minor = beam_props["minor"]["value"] * \
    u.Unit(beam_props["minor"]["unit"])
pa = beam_props["positionangle"]["value"] * \
    u.Unit(beam_props["positionangle"]["unit"])

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

good_mask = nd.binary_opening(good_mask, kern.array > 0)
good_mask = nd.binary_closing(good_mask, kern.array > 0)
# Increase to slightly larger than a beam for the clean mask
good_mask = nd.binary_dilation(good_mask, kern.array > 0)


tmp = ia.newimagefromimage(infile="imaging/M33-ARMcont.image",
                           outfile="imaging/M33-ARMcont.sig_mask",
                           overwrite=False)
# add stokes axis
good_mask = good_mask[:, :, np.newaxis, np.newaxis]
tmp.putchunk(good_mask.astype('int16'))
tmp.done()


clean(vis='meas_sets/M33-ARMcont.ms',
      imagename="imaging/M33-ARMcont",
      field='M33*',
      imsize=[1024, 700],
      cell='0.2arcsec',
      mode='mfs',
      phasecenter='J2000 01h33m33.191 +30d32m06.720',
      imagermode='mosaic',
      ftmachine='mosaic',
      weighting='natural',
      niter=10000,
      gain=0.1,
      threshold='0.6mJy/beam',
      mask="imaging/M33-ARMcont.sig_mask",
      minpb=0.2,
      pbcor=True,
      interactive=False
      )
