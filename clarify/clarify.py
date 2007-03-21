"""
Clarify: a wrapper around several tools that convert PDF (as image) to TIFF
Then, the TIFF is pumped through Tesseract-ocr to capture the text.
This program was created to make it easy to text index obfuscated data contained
in PDFs released by organizations who have to release the information, but 
do not want the data poked, prodded or searched.

Clarify calls netpbm modules, which converts PDF to PPM to TIFF (via xpdf and netpbm)
Then, tesseract-ocr is called for each TIFF image, and the resulting data is saved
as TEXT. 

'Clarify' is the opposite of 'obfuscate'
"""

import os
import sys
import re
import shutil
from time import sleep

PNMTOTIFF = '/usr/bin/pnmtotiff'
TESSERACT = '/usr/local/bin/tesseract'

#here's how it goes
#pdftoppm file.pdf extract
#pnmtotiff -none extract-000001.ppm > extract01.tiff
#tesseract extract01.tiff extract01.txt


class ClarifyError(Exception):
    pass


class Clarify(object):
    
    def __init__(self,input_file,output_path,text_file_path):
        self.input_file = input_file
        self.output_path = output_path
        self.text_file_path = text_file_path
        self.tiff_lst = []
        self.resulting_text = [] #empty list to add each page's text
        self.txt_lst = [] #empty list to add tesseract txt file paths

        output_path_file = "%s%s" % (output_path,'/copy.pdf')
        print output_path_file
        try:
            shutil.copyfile(input_file,output_path_file)
        except Exception,e:
            raise ClarifyError("Err: Could not copy PDF to /tmp: %s" % str(e))

        
    def rip_images(self,tmpdir):
        """call the ripper to get uncompressed images out of the PDF"""
        cmd = "pdftoppm %s/copy.pdf %s/extract" % (tmpdir,tmpdir,)
        res = os.popen(cmd)
        #need to figure out how many pages are being created 
        #and loop/wait to see of they all have been generated
        return res

    
    def convert_pnm_tiff(self,pnm_pth):
        """Convert all pnm images to TIFF"""
        #pnmtotiff -none extract-000001.ppm > extract01.tiff
        tiff_pth = "%s%s" % (pnm_pth,'.tiff',)
        cmd = "pnmtotiff -none %s > %s" % (pnm_pth,tiff_pth,)
        res = os.system(cmd)
        return res

    
    def convert_all_pnms(self,pnm_lst):
        for pnm in pnm_lst:
            res = self.convert_pnm_tiff(pnm)
            #remove pnm file now
            os.unlink(pnm)
        #need error checking here
        tiff_lst = self.dir_to_lst(self.output_path)
        return tiff_lst


    def dir_to_lst(self,pth):
        """get a list of files with abs path in a directory"""
        lst = os.listdir(pth)
        new_lst = []
        for f in lst:
            if f == 'copy.pdf':
                pass
            else:
                new_lst.append(os.path.join(pth, f))
        #fixme: sort this list by filename
        return new_lst

    
    def ocr_page(self,tiff_img,txt_pth):
        """Perform Ocr on a Tiff image"""
        cmd = "%s %s %s" % (TESSERACT,tiff_img,txt_pth)
        res = os.popen(cmd)
        #fixme: res is a list that can be used as an operation log
        sleep(3)
        os.unlink(tiff_img)
        return
        
    
    def ocr_all(self,tiffs):
        """perform ocr on a list of tiff paths"""
        for tiff in tiffs:
            outpath = "%s" % tiff
            #fixme: see if tesseract will just output the txtdatat to stdout
            txt = self.ocr_page(tiff,outpath)
            #self.txt_lst.append(txt)


    def scrape_txt(self,pth):
        """scrape text out of tesseract txt file"""
        try:
            f = open(pth)
            lines = f.readlines()
            return "\n".join(lines)
        except Exception,e:
            return 'No text recovered: %s' % str(e)

    
    def scrape_all(self,lst):
        """scrap all text out of tesseract txt files"""
        self.txt_lst = []
        for l in lst:
            txt = self.scrape_txt(l)
            self.txt_lst.append(txt)
        return self.txt_lst

    
    def main(self):
        self.rip_images(self.output_path)

        sleep(20)

        lst = self.dir_to_lst(self.output_path)
        tiff_lst = self.convert_all_pnms(lst)
        lst = self.dir_to_lst(self.output_path)
        self.ocr_all(lst)

        sleep(10)

        lst = self.dir_to_lst(self.output_path)
        self.scrape_all(lst)


if __name__ == '__main__':
    
    pass
    
