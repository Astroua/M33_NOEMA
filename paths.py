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
    root = os.path.expanduser('~/Dropbox/code_development/VLA_Lband/')
    data_path = "/mnt/MyRAID/M33/"
elif "segfault" == socket.gethostname():
    root = os.path.expanduser("~/Dropbox/code_development/VLA_Lband/")
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

if __name__ == "__main__":

    # Append the repo directory to the path so paths is importable
    os.sys.path.append(root)
