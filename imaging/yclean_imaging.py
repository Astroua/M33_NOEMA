
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

import os
from distutils.dir_util import mkpath
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

folder_name = "line_imaging/yclean_05"

if not os.path.exists(folder_name):
    mkpath(folder_name)

vis = "meas_sets/M33-ARM05.ms"
imagename = "{}/M33-ARM05_yclean".format(folder_name)

yclean(vis, source, imagename, phasecenter, width=width, start=start,
       nchan=nchan, restfreq=restfreq, imsize=imsize, cell=cell,
       weighting='natural', robust=0.5, gridder='mosaic',
       specmode='cube', interpolation='linear', deconvolver='multiscale',
       scales=[0, 5, 10, 20], outframe='LSRK', uvtaper='', pblimit=0.2,
       interactive=False)

# Check the outputted clean products at each iteration before (hopefully)
# just keeping the final one.

impbcor(imagename='{}/M33-ARM05_yclean.tc_final.image'.format(folder_name),
        pbimage='{}/M33-ARM05_yclean.tc_final.pb'.format(folder_name),
        outfile='{}/M33-ARM05_yclean.tc_final.image.pbcor'.format(folder_name),
        overwrite=True)

exportfits(imagename='{}/M33-ARM05_yclean.tc_final.image.pbcor'.format(folder_name),
           fitsimage='{}/M33-ARM05_yclean.tc_final.image.pbcor.fits'.format(folder_name),
           velocity=True, overwrite=True, dropdeg=True, history=False)

exportfits(imagename='{}/M33-ARM05_yclean.tc_final.pb'.format(folder_name),
           fitsimage='{}/M33-ARM05_yclean.tc_final.pb.fits'.format(folder_name),
           velocity=True, overwrite=True, dropdeg=True, history=False)
