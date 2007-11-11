#!/usr/bin/python
from clarify import *
from time import sleep
from util import *

count = 1

pdf_lst = dir_to_lst('/home/david/Desktop/dl_cache')

ocr_cache = '/tmp/ocr_cache'
output = '/home/david/Desktop/output'

if not os.path.exists(ocr_cache):
        os.system('mkdir %s' % ocr_cache)

if not os.path.exists(output):
        os.system('mkdir %s' % output)

for pdf in pdf_lst:
    working_dir = "%s/%s" % (ocr_cache,count,)

    if not os.path.exists(working_dir):
        os.system('mkdir %s' % working_dir)
        
    c = Clarify(pdf,working_dir)
    info = c.pdf_info()

    print info
    
    c.rip_images(working_dir)
    print "sleeping...b right back."
    sleep_secs = int(info['Pages'])

    sleep(sleep_secs)

    lst = c.dir_to_lst(working_dir)
    tiff_lst = c.convert_all_pnms(lst)
    lst = c.dir_to_lst(working_dir)
    c.ocr_all(lst)

    sleep((sleep_secs / 2))

    lst = c.dir_to_lst(working_dir)
    c.scrape_all(lst)

    sleep((sleep_secs / 2))

    txt_lst = []
    pages = c.txt_dct.keys()
    pages.sort()

    for p in pages:
        txt_lst.append(c.txt_dct[p])

    txt = '\n\n'.join(txt_lst)
    output_file = "%s/%s" % (output,count,)
    print txt
    f = open(output_file,'w')
    f.writelines(txt)
    f.close()
    count = count +1
    c = None
    f = None
    txt = None
