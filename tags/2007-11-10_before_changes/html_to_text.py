import formatter
import htmllib


def convert(html=None):
    
    w = formatter.DumbWriter() # plain text
    f = formatter.AbstractFormatter(w)
    file = open("samples/sample.htm")
    # print html body as plain text
    p = htmllib.HTMLParser(f)
    p.save_bgn()
    try:
        p.feed(file.read())
        #p.close()
        links = p.anchorlist()
        data = p.save_end()
        print data
        return data
    except Exception,e:
        return e
