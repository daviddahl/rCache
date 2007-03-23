import os
import sys
import re
import shutil
from time import sleep
from util import dir_to_lst

class ClarifyJobsError(Exception):
    pass


class ClarifyJobs(object):

    def __init__(self,download_cache,url_txt_lst):

        self.download_cache = download_cache
        self.url_txt_lst = url_txt_lst
        self.jobs = {}
    
    def get_pdf_http(self,url):
        """Given a url of a PDF download it"""
        #use twill to download
        #save to directory
        pass

    def load_url(self,url):
        self.pdf_urls.append(url)

    def load_urls(self):
        
        pdf_search = re.compile('.pdf$')
        try:
            count = 1
            f = open(self.url_txt_lst,'r')
            for line in f:
                file_url = line.split('/')
                for part in file_url:
                    if pdf_search.search(part):
                        filename = part
                        break
                local_path = "%s/%s" % (self.download_cache,filename,)
                #fixme: downloads to current dir
                cmd = 'wget %s -O %s' % (line,local_path,)
                res = os.popen(cmd)
                self.make_job(count,line,local_path)
                local_path = None
                line = None
                count = count + 1
            return self.jobs
        
        except Exception,e:
            print "error opening File: %s: %s" % (self.url_txt_lst,str(e),)
            pass


    def get_file_http(self,url):
        """download a page with twill: parse for links ending in '.pdf'
        add all links to the pdf_urls list"""
        pass

    def make_job(self,url,local_file,number):
        if not self.jobs:
            self.jobs = {}
        self.jobs[number] = {'url':url,'file':local_file}

    
    
