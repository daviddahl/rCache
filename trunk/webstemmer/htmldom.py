#!/usr/bin/env python
#
# htmldom.py
#
#  Copyright (c) 2005  Yusuke Shinyama <yusuke at cs dot nyu dot edu>
#  
#  Permission is hereby granted, free of charge, to any person
#  obtaining a copy of this software and associated documentation
#  files (the "Software"), to deal in the Software without
#  restriction, including without limitation the rights to use,
#  copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following
#  conditions:
#  
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#  
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
#  KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import sys
from urlparse import urljoin
from urllib import unquote
from htmlparser3 import HTMLParser3, HTMLHandler
from htmlutils import concat, attr2str, quotestr, INLINE_IMMED, NON_NESTED


def element_tag(x):
  return isinstance(x, HTMLElement) and x.tag.lower()

def get_text(x, elimtags=('style', 'script', 'comment', 'option')):
  if isinstance(x, HTMLElement):
    return concat(x.get_text(elimtags=elimtags))
  else:
    return x


class ElementNotFoundError(KeyError): pass


##  HTMLElement
##
class HTMLElement:
  """
  This class represents an HTML element.
  This object has the following public attributes.
  
  tag: the name of the element.
  root: the root element which is the whole HTML page.
  parent: the parent element.
  children: a list of child elements.
  attrs: dictionary which contains attributes.
  active: boolean flag which indicates whether this element is
          still under construction.
  """
  
  def __init__(self, root, tag, haschild, attrs={}):
    """Creates an instance of the HTMLElement class.
    """
    self.root = root
    self.tag = str(tag)
    if haschild:
      self.children = []
    else:
      self.children = None
    self.attrs = attrs
    self.parent = None
    self.active = True
    return
  
  def __repr__(self):
    return '<%s%s>' % (self.tag, ''.join([ ' %s=%r' % (k,v) for (k,v) in self.attrs.iteritems() ]))

  def dup(self):
    if self.children == None:
      obj = HTMLElement(self.root, self.tag, False, self.attrs)
    else:
      obj = HTMLElement(self.root, self.tag, True, self.attrs)
      obj.children = self.children[:]
    obj.parent = self.parent
    obj.active = self.active
    return obj

  # check the structure is correct.
  def validate(self):
    # check if I am one of my parent's children.
    if self.parent:
      assert self in self.parent.children
    # check if all my children belong to me.
    if self.children:
      for c in self.children:
        if element_tag(c):
          c.validate()
          assert self == c.parent, c
        else:
          assert isinstance(c, str) or isinstance(c, unicode)
    return self

  def finish(self):
    self.active = False
    return self

  def get_attr(self, k, default=None):
    return self.attrs.get(k, default)
  
  def debug(self, i=0):
    print " "*i+str(self)
    if self.children == None: return
    for c in self.children:
      if element_tag(c):
        c.debug(i+1)
      else:
        print " "*(i+1)+repr(c)
    print " "*i+"</%s>" % self.tag
    return
  
  def dump(self, out=sys.stdout, codec='ascii'):
    if self.tag == 'comment':
      out.write('<!--')
    else:
      out.write('<%s%s>' % (self.tag, attr2str(self.attrs.iteritems())))
    # IMMED?
    if self.children == None: return
    # CDATA?
    if self.tag in ('style','script'):
      for x in self.children:
        out.write(x.encode(codec, 'replace'))
    else:
      # BLOCK
      for x in self.children:
        if element_tag(x):
          x.dump(out, encoder)
        else:
          out.write(quotestr(x, codec))
    if self.tag == 'comment':
      out.write('-->')
    else:
      out.write("</%s>" % self.tag)
    return

  def find_first(self, tag):
    for e in self.walk():
      if element_tag(e) == tag:
        return e
    raise ElementNotFoundError(tag)

  def walk(self):
    yield self
    if self.children != None:
      for c in self.children:
        if element_tag(c):
          for x in c.walk():
            yield x
        else:
          yield c
    return

  def get_text(self, elimtags=('style', 'script', 'comment', 'option'), recursive=True):
    if self.tag in elimtags: return
    if self.tag in ("p", "br", "div", "pre", "td"): yield "\n"
    if self.tag == 'img' and 'alt' in self.attrs: yield self.attrs['alt']
    if self.children != None:
      for c in self.children:
        if element_tag(c):
          if recursive:
            for x in c.get_text(elimtags, recursive):
              yield x
        else:
          yield c
    return

  def get_links(self, normalize=False):
    """Return the list of href links in the element.

    When normalize is set, the relative url is normalized based on the documentbase.
    """
    for x in self.walk():
      if element_tag(x) == "a" and x.get_attr("href"):
        url = unquote(x.get_attr("href"))
        if normalize:
          url = self.root.normalize_url(url)
        yield (concat(x.get_text()), url)
    return
  
  def add_child(self, e, i=-1):
    """Add a child HTMLElement."""
    assert self.children != None, 'this element cannot have a child: %r' % self
    #if (not self.children) or element_tag(e) or element_tag(self.children[-1]):
    #  self.children.append(e)
    #else:
    #  self.children[-1] += e
    self.children.append(e)
    if element_tag(e):
      e.parent = self
    return self



##  HTMLRootElement
##
class HTMLRootElement(HTMLElement):
  """A special element which contains the whole HTML document.
  """

  def __init__(self, charset=None, base_href=None, base_ok=False):
    self.charset = charset
    self.base_href = base_href
    self.base_ok = base_ok
    HTMLElement.__init__(self, self, "html", True, {})
    return

  def set_root_attrs(self, attrs):
    self.attrs = attrs
    return

  def set_root_charset(self, charset):
    self.charset = charset
    return

  # handle_special(element) <base>
  def set_base(self, e):
    """set base."""
    if self.base_href:
      e.attrs["href"] = self.base_href
    else:
      self.base_href = e.get_attr("href")
    self.base_ok = True
    return

  # normalize_url(url)
  def normalize_url(self, url):
    """Convert a relative URL to an absolute one."""
    return urljoin(self.base_href, url)

  def finish(self):
    HTMLElement.finish(self)
    if not self.base_ok:
      base = HTMLElement(self, "base", False, { "href": self.base_href })
      try:
        head = self.find_first("head")
        head.children.insert(0, base)
      except ElementNotFoundError:
        head = HTMLElement(self, "head", True).add_child(base)
        self.children.insert(0, head)
        head.parent = self
    return self


##  HTMLDocumentBuilder
##
class HTMLDocumentBuilder(HTMLHandler):
  
  def __init__(self, base_href=None):
    self.root = HTMLRootElement(base_href=base_href)
    self.curform = None
    self.curstack = [self.root]
    return

  def set_charset(self, charset):
    self.root.set_root_charset(charset)
    return

  def handle_data(self, s):
    #print "data:", repr(s)
    assert self.curstack
    self.curstack[-1].add_child(s)
    return
  
  def process_formobj(self, e):
    if self.curform and not filter(lambda e1:e1.tag == "form", self.curstack):
      if not hasattr(self.curform, "fields"): self.curform.fields = []
      self.curform.fields.append(e)
      e.form = self.curform
    return

  def start_unknown(self, tag, attrs):
    #print "start:", tag, attrs
    if tag == "html":
      self.root.set_root_attrs(attrs)
    elif tag in NON_NESTED:
      # form kludge
      e = HTMLElement(self.root, tag, False, attrs)
      self.curstack[-1].add_child(e)
      self.curform = e
    else:
      e = HTMLElement(self.root, tag, tag not in INLINE_IMMED, attrs)
      self.curstack[-1].add_child(e)
      self.curstack.append(e)
      if tag in ("input", "select", "textarea", "fieldset", "label"):
        self.process_formobj(e)
      elif tag == "base":
        self.root.set_base(e)
    return

  def end_unknown(self, tag):
    if tag in ("html"): return
    self.curstack[-1].finish()
    if tag in NON_NESTED:
      e = HTMLElement(self.root, '/'+tag, False)
      self.curstack[-1].add_child(e)
      self.curform = None
    else:
      self.curstack.pop()
    return

  def finish(self):
    assert len(self.curstack) == 1, self.curstack
    self.root.finish()
    return self.root



# utilities

def parsefile(fp, base_href=None, charset='iso-8859-1', debug=0):
  p = HTMLParser3(HTMLDocumentBuilder(base_href=base_href), charset=charset, debug=debug)
  p.feedfile(fp)
  return p.close()
def parsestr(s, base_href=None, charset='iso-8859-1', debug=0):
  p = HTMLParser3(HTMLDocumentBuilder(base_href=base_href), charset=charset, debug=debug)
  p.feed(s)
  return p.close()

# main
if __name__ == "__main__":
  import getopt
  from htmlutils import getcodec
  from urllib import urlopen
  def usage():
    print "usage: htmldom.py [-d] [-c charset_in] [-C charset_out] [url ...]"
    sys.exit(2)
  try:
    (opts, args) = getopt.getopt(sys.argv[1:], "dc:C:")
  except getopt.GetoptError:
    usage()
  (debug, charset_in, charset_out) = (False, 'iso-8859-1', 'iso-8859-1')
  for (k, v) in opts:
    if k == "-d": debug += 1
    elif k == "-c": charset_in = v
    elif k == "-C": charset_out = v
  codec = getcodec(charset_out)
  for url in args:
    fp = urlopen(url)
    root = parsefile(fp, base_href=url, charset=charset_in)
    fp.close()
    if debug:
      root.debug()
    else:
      root.dump(codec=codec)
