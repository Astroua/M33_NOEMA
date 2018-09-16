
'''
Make a signal mask and compute the moments for the final non-feathered cube
'''

from astropy import log
from cube_analysis import run_pipeline
from cube_analysis.masking import common_beam_convolve
from spectral_cube import SpectralCube
import astropy.units as u

from paths import (noema_data_path)

# Load in the pb cube to create a spatial noise map
pb = SpectralCube.read(noema_data_path('yclean_05/M33-ARM05_yclean.tc_final.pb.fits'))[0]

rms_noise = 0.22 * u.K

noise_map = (rms_noise / pb)

# NOEMA cube

# Make a cube version convolved to a common beam.
# The beam hardly changes between channels (<<1 pix), so it isn't useful to
# have different beams for each channel
# Increase epsilon from the default to avoid the pts common beam algorithm
# from marginally failing
log.info("Convolving NOEMA cube to a common beam")
common_beam_convolve(noema_data_path("M33-ARM05_yclean.tc_final.image.pbcor.K.fits"),
                     noema_data_path("M33-ARM05_yclean.tc_final.image.pbcor.K.com_beam.fits",
                                     no_check=True),
                     epsilon=8e-4)

log.info("Masking and moments for the NOEMA cube")
run_pipeline(noema_data_path("M33-ARM05_yclean.tc_final.image.pbcor.K.com_beam.fits"),
             noema_data_path("", no_check=True),
             masking_kwargs={"method": "ppv_connectivity",
                             "save_cube": True,
                             "is_huge": False,
                             "noise_map": rms_noise,
                             "smooth_chans": None,
                             "min_chan": 5,
                             "peak_snr": 5.,
                             "min_snr": 2,
                             "edge_thresh": 1,
                             },
             moment_kwargs={"num_cores": 2,
                            "verbose": True})
