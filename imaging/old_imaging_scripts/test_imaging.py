
import astropy.units as u

# Can't find the vptable by default. So save it and feed it in manually
# vp.setpbimage(telescope='NOEMA')

# Create a Gaussian pb model b/c casa doesn't have a NOEMA/PdBI beam model?
fwhm = (((230.538 * u.GHz).to(u.m, u.spectral()) / (15 * u.m)) * u.rad).to(u.deg).value
vp.setpbgauss(telescope='NOEMA', dopb=True,
              halfwidth=fwhm,
              maxrad=4 * fwhm,
              reffreq='230.538GHz')

vp.saveastable('noema_pb.tab')

tclean(vis='meas_sets/M33-ARM05.ms',
       datacolumn='data',
       imagename="imaging/M33-ARM05_tclean_dirty",
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
       niter=0,
       threshold='3.2mJy/beam',
       phasecenter='J2000 01h33m33.191 +30d32m06.720',
       restfreq='230.538GHz',
       outframe='LSRK',
       pblimit=0.1,
       usemask='pb',
       mask=None,
       deconvolver='hogbom',
       pbcor=False,
       chanchunks=-1,)
       # vptable=vp.getvp('IRAMPDB')
       # )


clean(vis='meas_sets/M33-ARM05.ms',
      imagename="imaging/M33_ARM05",
      field='M33*',
      imsize=[1024, 700],
      cell='0.2arcsec',
      mode='channel',
      start=1,
      width=1,
      nchan=-1,
      phasecenter='J2000 01h33m33.191 +30d32m06.720',
      restfreq='230.538GHz',
      imagermode='mosaic',
      ftmachine='mosaic',
      weighting='natural',
      niter=10000,
      gain=0.2,
      threshold='70mJy/beam',
      outframe='LSRK',
      mask=None,
      minpb=0.2,
      pbcor=False,
      interactive=True
      )

# Make a bunch of dirty cubes
names = ['M33-ARM', 'M33-ARM05',
         'M33-ARM1', 'M33-ARM13',
         'M33-ARM2', 'M33-ARM05-merged']

for name in names:
      clean(vis='meas_sets/{}.ms'.format(name),
            imagename="imaging/{}_dirty".format(name),
            field='M33*',
            imsize=[1024, 700],
            cell='0.2arcsec',
            mode='channel',
            start=1,
            width=1,
            nchan=-1,
            phasecenter='J2000 01h33m33.191 +30d32m06.720',
            restfreq='230.538GHz',
            imagermode='mosaic',
            ftmachine='mosaic',
            weighting='natural',
            niter=0,
            gain=0.2,
            threshold='70mJy/beam',
            outframe='LSRK',
            mask=None,
            minpb=0.2,
            pbcor=False,
            interactive=False
            )

      impbcor(imagename='imaging/{}_dirty.image'.format(name),
              pbimage='imaging/{}_dirty.flux'.format(name),
              outfile='imaging/{}_dirty.image.pbcor'.format(name))
