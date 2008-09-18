import os, sys
from django.utils.translation import ugettext_lazy as _

"""this program requires antiword
Author: David Dahl
Date: 3/29/2006

usage: 

scrape Word Doc, save as tmp file:


"""
from rcache.settings import ANTIWORD
import codecs

def getCommandOutput(command):
    child = os.popen(command)
    data = child.read()
    err = child.close()
    if err:
        raise RuntimeError, _('%(cmd)s failed w/ exit code %(err)d') \
              % {'cmd':command,
                 'err':err}
    return data


def extractText(word_doc):
    cmd = "%s %s" % (ANTIWORD,word_doc)
    txt = getCommandOutput(cmd)
    utxt = codecs.utf_8_decode(txt,'ignore')
    return utxt[0]
    

def save_tmp(data):
    import tempfile
    f, temp_file = tempfile.mkstemp()
    print temp_file
    open(temp_file, "w+b").write(data)
    
    return temp_file

def getTextFromFile(file):
    f = open(file,"r")
    return unicode(f.read())
