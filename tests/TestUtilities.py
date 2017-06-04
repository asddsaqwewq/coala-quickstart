import os
from contextlib import contextmanager


@contextmanager
def generate_files(fnames, file_contents, directory=os.getcwd()):
    """
    Generates files with specified contents temporarily.

    :param fnames:        list of file names to create.
    :param file_contents: list of strings containing content
                          corresponding to the supplied file names.
    """
    fpaths = []
    try:
        for fname, fcontent in zip(fnames, file_contents):
            with open(fname, 'w', encoding='utf-8') as file:
                file.write(fcontent)
            fpaths.append(os.path.join(directory, fname))
        yield fpaths
    finally:
        for fpath in fpaths:
            os.remove(fpath)
