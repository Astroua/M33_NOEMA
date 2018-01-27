
# Convert uvfits from gildas into a CASA MS
# For casa 5.1.1

from astropy.io import fits
import astropy.units as u
from astropy.coordinates import SkyCoord
import numpy as np
import os

# Issues with setting vsys and rest freq of the source
# Presumably this is fine and can just be given when imaging
# The dishes are also all set to the same position, but the baselines
# are correct in the actual data.

# Loop through the different spectral resolutions Jonathan made
# str_prefix = ['M33-ARM-', 'M33-ARM05-', 'M33-ARM1-', 'M33-ARM13-', 'M33-ARM2-',
#               'M33-ARMcont-', 'M33-ARM05-merged-']
str_prefix = ['M33-ARM-', 'M33-ARM05-', 'M33-ARM1-', 'M33-ARM13-', 'M33-ARM2-',
              'M33-ARMcont-']

if not os.path.exists('meas_sets'):
    os.mkdir('meas_sets')

for pref in str_prefix:

    print("On {}".format(pref))

    ms_names = []

    for i in range(1, 89):

        print("On {} of 88".format(i))

        str_name = '{}{}'.format(pref, i)

        uvfits = "calib/uvfits/{}.uvfits".format(str_name)
        uncor_vis_name = "meas_sets/{}_uncor.ms".format(str_name)
        vis_name = "meas_sets/{}.ms".format(str_name)

        hdu = fits.open(uvfits, mode='update')
        # UVFITS have two directions: CRVAL5 and 6 are the phase direction,
        # and OBSRA and DEC are the pointing centres. But CASA doesn't
        # recognize the latter keywords and assumes that they are the pointing
        # and phase centres. We'll fix these below using the fixvis routine,
        # but we'll need the pointing centres
        point = SkyCoord(hdu[0].header['OBSRA'] * u.deg,
                         hdu[0].header['OBSDEC'] * u.deg)
        point_string = point.to_string(style='hmsdms')

        # hdu[0].header['CRVAL5'] = hdu[0].header['OBSRA']
        # hdu[0].header['CRVAL6'] = hdu[0].header['OBSDEC']

        # The ref freq is also confusing. It's the frequency in the rest frame
        # So it needs to be altered to be in the observed frame.
        # GILDAS appears to have this conversion built-in everywhere
        restfreq = hdu[0].header['RESTFREQ'] * u.Hz
        rest_cent_freq = hdu[0].header['CRVAL4'] * u.Hz
        source_vel = hdu[0].header['VELO-LSR'] * u.m / u.s

        # Calculate the frequency shift
        del_f = rest_cent_freq - source_vel.to(u.Hz, u.doppler_radio(restfreq))

        # Adjust CRVAL4 to the observed frame frequency
        hdu[0].header['CRVAL4'] -= del_f.value

        # Need to assign the SD visibilities to an ant pair
        # CASA doesn't barf when doing this, but I can't be sure it worked in
        # any useful way. So don't use this for any science products, just as
        # a check against the GILDAS imaging
        if 'merged' in pref:
            raise ValueError("This does not work. Don't import merged files "
                             "into CASA!")
            baselines = hdu[0].data['BASELINE']
            baselines[np.where(baselines == 0)] = baselines[0]
            hdu[0].data['BASELINE'] = baselines

        hdu.flush()
        hdu.close()

        importuvfits(fitsfile=uvfits, vis=uncor_vis_name)

        # Recalculate uv data with the phase at the pointing centre
        fixvis(vis=uncor_vis_name,
               outputvis=vis_name,
               field='M33-ARM',
               phasecenter='J2000 {}'.format(point_string))

        # Remove the uncorrected version
        rmtables(uncor_vis_name)

        # Change the field name
        vishead(vis="meas_sets/{}.ms".format(str_name), mode='put',
                hdkey='field', hdvalue=str_name)

        # If you want to use tclean, you'll need to rename the telescope to
        # IRAMPDB instead of IRAM PDB. The former is the correct beam response
        # name, the latter is the name that CASA recognizes elsewhere.
        vishead(vis='meas_sets/{}.ms'.format(str_name), mode='put',
                hdkey='telescope',
                hdvalue=(np.array(["IRAMPDB"] * 2)))

        # Add in rest freq and vsys
        hdu = fits.open(uvfits)

        tb.open("{}/SOURCE".format(vis_name), nomodify=False)
        # tb.putcol('REST_FREQUENCY', [[hdu[0].header['RESTFREQ']]])
        tb.putcol('SYSVEL', [[hdu[0].header['VELO-LSR']]])
        tb.putcol('NAME', [[str_name]])
        tb.close()

        hdu.close()

        ms_names.append(vis_name)

    # Now concatenate

    concat(vis=ms_names, concatvis='meas_sets/{}.ms'.format(pref[:-1]))

    # Delete the individual MSs
    for ms_name in ms_names:
        rmtables(ms_name)
