import os
from contextlib import contextmanager


@contextmanager
def generate_files(fnames, file_contents, directory=os.getcwd()):
    """
    Generates files with specified contents temporarily.

    :param fnames:        list of file names to create.
    :param file_contents: list of strings containing content
                          corresponding to the supplied file names.
    :param directory:     path to the directory where the files are
                          to be generated.
    """
    fpaths = []
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        for fname, fcontent in zip(fnames, file_contents):
            fpath = os.path.join(directory, fname)
            with open(fpath, 'w', encoding='utf-8') as file:
                file.write(fcontent)
            fpaths.append(fpath)
        yield fpaths
    finally:
        for fpath in fpaths:
            os.remove(fpath)
