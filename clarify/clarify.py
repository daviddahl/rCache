"""
Clarify: a wrapper around several tools that convert PDF (as image) to TIFF
Then, the TIFF is pumped through Tesseract-ocr to capture the text.
This program was created to make it easy to text index obfuscated data contained
in PDFs released by organizations who have to release the information, but 
do not want the data poked, prodded or searched

Clarify calls 'pdfripimage', which converts PDF to PPM to TIFF (via xpdf and netpbm)
Then, tesseract-ocr is called for each TIFF image, and the resulting data is saved
as TEXT. 

'Clarify' is the opposite of 'obfuscate'
"""

import os
import sys
import re
import glob

PDFRIPIMAGE = '/usr/local/bin/pdfripimage'
PNMTOTIFF = '/usr/bin/pnmtotiff'
TESSERACT = '/usr/local/bin/tesseract'

class Clarify(object):
    
    def __init__(self,input_file,output_path,text_file_path):
        self.input_file = input_file
        self.output_path = output_path
        self.text_file_path = text_file_path
        self.tiff_lst = []
        self.resulting_text = [] #empty list to add each page's text
        self.txt_lst = [] #empty list to add tesseract txt file paths
        
    def rip_images(self):
        """call the ripper to get uncompressed images out of the PDF"""
        cmd = "%s %s" % (PDFRIPIMAGE,self.input_file,)
        res = os.popen(cmd)
        return res
    
    def convert_pnm_tiff(self):
        """Convert all pnm images to TIFF"""
        pass
    
    def dir_to_lst(self,pth):
        """get a list of files with abs path in a directory"""
        lst = os.listdir(pth)
        new_list = []
        for f in lst:
            new_lst.append(os.path.join(pth, f))
        return new_list
    
    def ocr_page(self,tiff_img,txt_pth):
        """Perform Ocr on a Tiff image"""
        cmd = "%s %s %s" % (TESSERACT,tiff_img,txt_pth)
        res = os.popen(cmd)
        #fixme: res is a list that can be used as an operation log
        self.txt_lst.append(txt_pth)
        return res
    
    def ocr_all(self,tiffs):
        """perform ocr on a list of tiff paths"""
        pg = 0
        for tiff in tiffs:
            outpath = "%s%s" % (tiff,str(pg))
            #fixme: see if tesseract will just output the txtdatat to stdout
            self.ocr_page(tiff,outpath)
            pg += 1

    def scrape_txt(self,pth):
        """scrape text out of tesseract txt file"""
        try:
            f = open(pth)
            lines = f.readlines()
            return "\n".join(lines)
        except:
            pass
