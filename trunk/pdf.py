import os, sys
import re
import codecs

from django.utils.translation import ugettext_lazy as _
"""this program requires xpdf
Author: David Dahl
Date: 2/21/2006

usage: 

scrape PDF from site, save as tmp file:

data = scrape_from_site_use_urllib2(http://pdffile.com/myfile.pdf)

file = save_tmp(data)
the_text = extractPDFText(file)


"""
from rcache.settings import PDFTOTEXT as pdftotext


def extractPDFText(pdf_filename):
    """Given an pdf file name, returns a new file object of the
    text of that PDF.  Uses the 'pdftotext' utility."""
    os.popen("%s %s" % (pdftotext,pdf_filename,))
    
    txtfile = pdf_filename + ".txt"
    txt = getTextFromFile(txtfile)
    try:
        utxt = codecs.utf_8_decode(txt,'ignore')
        return utxt[0]
        #encoded = txt.encode("utf8")
        #return encoded
    except Exception, e:
        raise
        print str(e)
        return unicode("Could not capture text from PDF document: %s" % str(e))
    

def save_tmp(data):
    import tempfile
    f, temp_file = tempfile.mkstemp()
    print temp_file
    open(temp_file, "w+b").write(data)
    
    return temp_file

def getTextFromFile(file):
    f = open(file,"r")
    return f.read()
