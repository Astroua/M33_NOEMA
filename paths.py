import os
import socket
from functools import partial
import glob

'''
Common set of paths giving the location of data products.
'''

def name_return_check(filename, path, no_check=False):
    full_path = os.path.join(path, filename)

    if not os.path.exists(full_path) and not no_check:
        raise OSError("{} does not exist.".format(full_path))

    return full_path


if socket.gethostname() == 'ewk':
    root = os.path.expanduser('~/Dropbox/code_development/M33_NOEMA/')
    data_path = "/mnt/MyRAID/M33/"
elif "segfault" == socket.gethostname():
    root = os.path.expanduser("~/Dropbox/code_development/M33_NOEMA/")
    data_path = "/mnt/bigdata/ekoch/M33"

imaging_path = partial(name_return_check,
                       path=os.path.join(root, 'imaging'))

analysis_path = partial(name_return_check,
                        path=os.path.join(root, 'analysis'))

noema_path = partial(name_return_check,
                     path=os.path.join(data_path, 'co21_noema'))

noema_data_path = partial(name_return_check,
                          path=os.path.join(data_path,
                                            'co21_noema/line_imaging'))

iram_data_path = partial(name_return_check,
                         path=os.path.join(data_path,
                                           'co21'))

iram_matched_data_path = partial(name_return_check,
                                 path=os.path.join(data_path,
                                                   'co21/noema'))

fig_path = os.path.expanduser("~/Dropbox/Various Plots/M33/NOEMA/")
allfigs_path = lambda x: os.path.join(fig_path, x)


def find_dataproduct_names(path):
    '''
    Given a path, return a dictionary of the data products with the name
    convention used in this repository.
    '''

    search_dict = {"Moment0": "mom0",
                   "Moment1": "mom1",
                   "LWidth": "lwidth",
                   "Skewness": "skewness",
                   "Kurtosis": "kurtosis",
                   "PeakTemp": "peaktemps",
                   "PeakVels": "peakvels.",
                   "Cube": "pbcor.K.com_beam.fits",
                   "Source_Mask": "pbcor.K.com_beam_source_mask.fits", }
                   # "CentSub_Cube": "masked.centroid_corrected",
                   # "CentSub_Mask": "masked_source_mask.centroid_corrected",
                   # "RotSub_Cube": "masked.rotation_corrected",
                   # "RotSub_Mask": "masked_source_mask.rotation_corrected",
                   # "PeakSub_Cube": "masked.peakvels_corrected",
                   # "PeakSub_Mask": "masked_source_mask.peakvels_corrected"}

    found_dict = {}

    for filename in glob.glob(os.path.join(path, "*.fits")):

        for key in search_dict:
            if search_dict[key] in filename:
                found_dict[key] = filename
                search_dict.pop(key)
                break

    return found_dict


# Return dictionaries with names for the existing directories
noema_co21_file_dict = \
    find_dataproduct_names(noema_data_path("", no_check=True))

if __name__ == "__main__":

    # Append the repo directory to the path so paths is importable
    os.sys.path.append(root)
