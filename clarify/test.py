from clarify import *
from time import sleep
#DOJDocsPt1-2070319.pdf
c = Clarify('/home/david/code/transcript.pdf','/tmp/pdf_ocr')
info = c.pdf_info()

print info

c.rip_images('/tmp/pdf_ocr')

sleep_secs = int(info['Pages'])

sleep(sleep_secs)

lst = c.dir_to_lst('/tmp/pdf_ocr')
tiff_lst = c.convert_all_pnms(lst)
lst = c.dir_to_lst('/tmp/pdf_ocr')
c.ocr_all(lst)

sleep((sleep_secs / 2))

lst = c.dir_to_lst('/tmp/pdf_ocr')
c.scrape_all(lst)

sleep((sleep_secs / 2))

txt_lst = []
pages = c.txt_dct.keys()
pages.sort()

for p in pages:
    txt_lst.append(c.txt_dct[p])
    
txt = '\n\n'.join(txt_lst)

print txt
f = open('/home/david/Desktop/KSM.txt','w')
f.writelines(txt)
f.close()
