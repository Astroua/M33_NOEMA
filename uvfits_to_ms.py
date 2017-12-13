
# Convert uvfits from gildas into a CASA MS
# For casa 5.1.1

from astropy.io import fits

# Issues with setting vsys and rest freq of the source
# Presumably this is fine and can just be given when imaging
# The dishes are also all set to the same position, but the baselines
# are correct in the actual data.

ms_names = []

for i in range(1, 89):

    print("On {} of 88".format(i))

    # str_name = 'M33-ARM-{}'.format(i)
    str_name = 'M33-ARM05-{}'.format(i)
    # str_name = 'M33-ARM1-{}'.format(i)

    uvfits = "calib/uvfits/{}.uvfits".format(str_name)
    vis_name = "meas_sets/{}.ms".format(str_name)


    hdu = fits.open(uvfits, mode='update')
    # For some reason, some of the uvfits don't have the correct CRVAL for
    # RA and DEC. The correct ones are set as OBSRA and OBSDEC. Make sure
    # these are the same before importing to CASA
    hdu[0].header['CRVAL5'] = hdu[0].header['OBSRA']
    hdu[0].header['CRVAL6'] = hdu[0].header['OBSDEC']
    hdu.flush()
    hdu.close()

    importuvfits(fitsfile=uvfits, vis=vis_name)

    # Change the field name
    vishead(vis="meas_sets/{}.ms".format(str_name), mode='put',
            hdkey='field', hdvalue=str_name)

    # Add in rest freq and vsys
    hdu = fits.open(uvfits)

    tb.open("{}/SOURCE".format(vis_name), nomodify=False)
    tb.putcol('REST_FREQUENCY', [[hdu[0].header['RESTFREQ']]])
    tb.putcol('SYSVEL', [[hdu[0].header['VELO-LSR']]])
    tb.putcol('NAME', [[str_name]])
    tb.close()

    hdu.close()

    ms_names.append(vis_name)

# Now concatenate

# concat(vis=ms_names, concatvis='meas_sets/M33-ARM.ms')
concat(vis=ms_names, concatvis='meas_sets/M33-ARM05.ms')
# concat(vis=ms_names, concatvis='meas_sets/M33-ARM1.ms')
