import os, sys

"""this program requires antiword
Author: David Dahl
Date: 3/29/2006

usage: 

scrape Word Doc, save as tmp file:


"""
from rcache.settings import ANTIWORD


def getCommandOutput(command):
    child = os.popen(command)
    data = child.read()
    err = child.close()
    if err:
	raise RuntimeError, '%s failed w/ exit code %d' % (command, err)
    return data


def extractText(word_doc):
    cmd = "%s %s" % (ANTIWORD,word_doc)
    txt = getCommandOutput(cmd)
    return txt
    

def save_tmp(data):
    import tempfile
    f, temp_file = tempfile.mkstemp()
    print temp_file
    open(temp_file, "w+b").write(data)
    
    return temp_file

def getTextFromFile(file):
    f = open(file,"r")
    return f.read()
