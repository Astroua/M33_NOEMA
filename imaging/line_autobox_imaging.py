
# Some testing with my additions to Amanda's autobox algorithm

import sys

from imagerhelpers.input_parameters import ImagerParameters

# Add code to path
sys.path.append("/home/ekoch/Dropbox/code_development/autobox/")

from autobox import runTclean

sigma = 0.025
point_thresh = 2 * sigma

params = ImagerParameters(
       msname='/mnt/bigdata/ekoch/M33/co21_noema/meas_sets/M33-ARM05.ms',
       datacolumn='data',
       imagename="M33-ARM05_multithresh_test",
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
       usemask='pb',
       pbmask=0.05,
       mask=None,
       deconvolver='hogbom',
       dopbcorr=False,
       chanchunks=-1)

# Using the result from the first multi-scale tclean call in line_imaging.py

runTclean(params,
          sidelobeThreshold=2.0,
          lowNoiseThreshold=1.0,
          noiseThreshold=3.0,
          smoothFactor=3.0,
          cutThreshold=0.001,
          spectralDilate=True,
          minBeamFrac=0.5,
          pbcor=False)
