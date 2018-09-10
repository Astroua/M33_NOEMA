
'''
Imaging using the autoboxing technique from yclean:
 http://home.strw.leidenuniv.nl/~ycontreras//yclean.html

Run in the same path the data is located.

Results in a cube cleaned down to 2-sigma = 0.0378375 Jy/beam
For the ~1.5''x1.3'' beam, the cube is cleaned down to 0.45 K.

So the 1-sigma error is ~0.22 K, though this will vary by a factor
of a couple due to variation in the primary beam coverage.

Run in casa 4.7
'''

from yclean import *

source = 'M33*'
# vlsrsource = 28
phasecenter = 'J2000 01h33m33.191 +30d32m06.720'
imsize = [1024, 700]
cell = '0.2arcsec'

start = 1
width = 1
nchan = -1

restfreq = "230.538GHz"

vis = "meas_sets/M33-ARM05.ms"
imagename = "yclean_test/M33-ARM05_yclean_test"

yclean(vis, source, imagename, phasecenter, width=width, start=start,
       nchan=nchan, restfreq=restfreq, imsize=imsize, cell=cell,
       weighting='natural', robust=0.5, gridder='mosaic',
       specmode='cube', interpolation='linear', deconvolver='multiscale',
       scales=[0, 5, 10, 20], outframe='LSRK', uvtaper='', pblimit=0.2,
       interactive=False)
