from twill import get_browser
from twill.commands import *
from BeautifulSoup import BeautifulSoup
import html2text

b = get_browser()
b.set_agent_string('Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)')
go("http://ddahl.com")
html = b.get_html()
soup = BeautifulSoup(html)

h,txt = html2text.html2text(soup.__str__())
txt
