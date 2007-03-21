from clarify import *
from time import sleep

c = Clarify('/home/david/code/transcript_ISN10024.pdf','/tmp/pdf_rip_cache','/tmp/pdf_rip_cache/text')
c.rip_images('/tmp/pdf_rip_cache')

sleep(20)

lst = c.dir_to_lst('/tmp/pdf_rip_cache')
tiff_lst = c.convert_all_pnms(lst)
lst = c.dir_to_lst('/tmp/pdf_rip_cache')
c.ocr_all(lst)

sleep(10)

lst = c.dir_to_lst('/tmp/pdf_rip_cache')
c.scrape_all(lst)

print c.txt_lst[0]
