import os
import sys


def dir_to_lst(pth):
    """get a list of files with abs path in a directory"""
    lst = os.listdir(pth)
    new_lst = []
    for f in lst:
        if f == 'copy.pdf' or os.path.isdir(f):
            pass
        else:
            new_lst.append(os.path.join(pth, f))
        #fixme: sort this list by filename
    return new_lst
