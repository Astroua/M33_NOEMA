
'''
Basic imaging to take a look at the structure of some of the really bright
sources
'''

from tclean import tclean

tclean(vis='meas_sets/M33-ARM05.ms',
       datacolumn='data',
       imagename="line_imaging_uniform/M33-ARM05_uniform",
       field='M33*',
       imsize=[1024, 700],
       cell='0.2arcsec',
       specmode='cube',
       start=1,
       width=1,
       nchan=-1,
       startmodel=None,
       gridder='mosaic',
       weighting='uniform',
       niter=0,
       threshold='0Jy/beam',
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
