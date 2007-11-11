#!/usr/bin/env python
#
# htmlparser3.py
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

import sys, re
from htmlutils import getcodec, BLOCK, CDATA, INLINE_IMMED, NON_NESTED, VALID_TAGS

__all__ = [ 'SGMLParser3', 'HTMLHandler', 'HTMLParser3' ]


##  SGMLParser3
##
class SGMLParser3:
  """
  Robust feed based SGML parser.
  Mainly for instantiating HTMLParser3.
  """

  def __init__(self):
    # parse1: current state:
    #   parse_pcdata, parse_cdata, parse_cdata_end, 
    #   parse_entity_0, parse_entity_1,
    #   parse_tag_0, parse_tag_1, parse_tag_attr_0, parse_tag_attr_1,
    #   parse_tag_attrvalue_0, parse_tag_attrvalue_1,
    #   parse_decl, parse_comment_0, parse_comment_1, parse_comment_2,
    self.parse1 = self.parse_pcdata
    # parse0: previous state
    self.parse0 = None
    return

  def close(self):
    """Finish parsing and discard all uncomplete tags and entities."""
    return

  # You should inherit the following methods.

  def handle_start_tag(self, name, attrs):
    raise NotImplementedError
  
  def handle_end_tag(self, name, attrs):
    raise NotImplementedError
  
  def handle_decl(self, name):
    raise NotImplementedError
  
  def handle_directive(self, name, attrs):
    raise NotImplementedError
  
  def handle_characters(self, data):
    raise NotImplementedError

  # Internal methods.
  
  from htmlentitydefs import name2codepoint
  def handle_entity(self, name0):
    """Convert an HTML entity name to one or more unicode character(s).

    Generally, you shouldn't change this method, as this is called
    from other internal methods.
    """
    name = name0.lower()
    if name in self.name2codepoint:
      # entityref
      return unichr(self.name2codepoint[name])
    else:
      # charref
      if name.startswith('#x'):
        try:
          return unichr( int(name[2:], 16) )
        except ValueError: # not a hex number, or not valid unichr number.
          pass
      elif name.startswith('#'):
        try:
          return unichr( int(name[1:]) )
        except ValueError: # not a int number, or not valid unichr number.
          pass
      return u'&'+name0

  def feed(self, x):
    """Feed a unicode string to the parser.

    This parser tries to decide things as quickly as possible,
    generally all complete tags and entities included in a string
    are immediately interpreted and proper action is taken.
    """
    i = 0
    assert isinstance(x, unicode)
    while 0 <= i and i < len(x):
      i = self.parse1(x, i)
    return self

  SPECIAL_CHAR0 = re.compile(r'[&<]')
  def parse_pcdata(self, x, i0):
    m = self.SPECIAL_CHAR0.search(x, i0)
    if not m:
      assert i0 < len(x)
      self.handle_characters(x[i0:])
      return -1
    # special character found
    i1 = m.start(0)
    if i0 < i1:
      self.handle_characters(x[i0:i1])
    c = x[i1]
    if c == '&':                      # meet: '&'
      self.feed_entity = self.handle_characters
      self.parse0 = self.parse_pcdata
      self.parse1 = self.parse_entity_0
    else:                             # meet: '<'
      self.parse1 = self.parse_tag_0
    return i1

  def start_cdata(self, endname):
    self.cdata_endstr = '</'+endname
    self.parse1 = self.parse_cdata
    return

  def parse_cdata(self, x, i0):
    try:
      i1 = x.index('<', i0)
      if i0 < i1:
        self.handle_characters(x[i0:i1])
      self.cdata_endcheck = '<'
      self.parse1 = self.parse_cdata_end
      return i1+1
    except ValueError:
      assert i0 < len(x)
      self.handle_characters(x[i0:])
      return -1
    
  def parse_cdata_end(self, x, i0):
    need = len(self.cdata_endstr) - len(self.cdata_endcheck)
    assert 0 < need
    left = len(x) - i0
    if left < need:
      self.cdata_endcheck += x[i0:]
      return -1
    i1 = i0+need
    self.cdata_endcheck += x[i0:i1]
    # now sufficient chars are available, check it.
    if self.cdata_endcheck.lower() == self.cdata_endstr:
      assert self.cdata_endstr.startswith('</')
      # ending tag
      self.cdata_endstr = ''
      self.attr_name = self.cdata_endstr[2:]
      self.handle_tag = self.handle_end_tag
      self.parse1 = self.parse_tag_attr_0
    else:
      # cdata still continues...
      try:
        # partial scan (for handling nasty "</scr</script>" case)
        i = self.cdata_endcheck.index('<', 1)
        self.handle_characters(self.cdata_endcheck[:i])
        self.cdata_endcheck = self.cdata_endcheck[i:]
      except ValueError:
        self.handle_characters(self.cdata_endcheck)
        self.parse1 = self.parse_cdata
    return i1

  # Parse entityrefs.
  
  def parse_entity_0(self, x, i0):
    assert x[i0] == '&'
    self.parse1 = self.parse_entity_1
    self.entity_name = ''
    return i0+1
  
  NOT_ENTITY_NAME = re.compile(r'[^a-zA-Z0-9#]')
  ENTITY_NAME_MAXCHARS = 20
  def parse_entity_1(self, x, i0):
    m = self.NOT_ENTITY_NAME.search(x, i0)
    if not m:
      if len(self.entity_name) < self.ENTITY_NAME_MAXCHARS:
        self.entity_name += x[i0:]
      return -1        
    # end of entity name
    i1 = m.start(0)
    if len(self.entity_name) < self.ENTITY_NAME_MAXCHARS:
      self.entity_name += x[i0:i1]
    self.feed_entity(self.handle_entity(self.entity_name))
    # "return" to the previous state.
    self.parse1 = self.parse0
    c = x[i1]
    if c == ';':
      i1 += 1
    return i1
    
  # Parse start/end tags.
  
  def parse_tag_0(self, x, i0):
    assert x[i0] == '<'
    self.parse1 = self.parse_tag_1
    self.tag_name = ''
    self.tag_attrs = []
    return i0+1

  def parse_tag_1(self, x, i0):
    c = x[i0]
    if c == '!':
      self.decl_string = ''
      self.parse1 = self.parse_decl
      i0 += 1
    elif c == '?':
      self.attr_name = ''
      self.handle_tag = self.handle_directive
      self.parse1 = self.parse_tag_attr_0
      i0 += 1
    elif c == '/':
      self.attr_name = ''
      self.handle_tag = self.handle_end_tag
      self.parse1 = self.parse_tag_attr_0
      i0 += 1
    else:
      self.attr_name = ''
      self.handle_tag = self.handle_start_tag
      self.parse1 = self.parse_tag_attr_0
    return i0

  # Parse tag attributes.
  
  TAGNAME_SOMETHING = re.compile(r'[^\s]')
  def parse_tag_attr_0(self, x, i0):
    # looking for a tagname/attrvalue...
    m = self.TAGNAME_SOMETHING.search(x, i0)
    if not m:
      # ignore intermediate characters.
      return -1
    i1 = m.start(0)
    c = x[i1]
    if c == '=':
      # attr value starting...
      self.parse1 = self.parse_tag_attrvalue_0
      return i1+1
    # tagname/attrname/endoftag found...
    if self.attr_name:
      # fix attr if any.
      self.tag_attrs.append((self.attr_name, self.attr_name))
    self.attr_name = ''
    if c == '<':
      # meet: '<...<'
      self.parse1 = self.parse_tag_0
      self.handle_tag(self.tag_name, self.tag_attrs) # this may change self.parse1 (CDATA).
    elif c == '>':
      # meet: '<...>'
      self.parse1 = self.parse_pcdata
      self.handle_tag(self.tag_name, self.tag_attrs) # this may change self.parse1 (CDATA).
      # eat this character.
      i1 += 1
    else:
      if c in '/?!\"\'':
        i1 += 1
      # attrname starting...
      self.parse1 = self.parse_tag_attr_1
    return i1
  
  NOT_TAGNAME = re.compile(r'[\s<>/\?!=\"\']')
  TAGNAME_MAXCHARS = 30 # maxchars for tag name or attr name.
  def parse_tag_attr_1(self, x, i0):
    # eating characters for a name...
    m = self.NOT_TAGNAME.search(x, i0)
    if not m:
      if len(self.attr_name) < self.TAGNAME_MAXCHARS:
        self.attr_name += x[i0:]
      return -1
    # tagname/attrname now complete, what's next?
    i1 = m.start(0)
    if len(self.attr_name) < self.TAGNAME_MAXCHARS:
      self.attr_name += x[i0:i1]
    self.attr_name = self.attr_name.lower()
    if not self.tag_name:
      self.tag_name = self.attr_name
      self.attr_name = ''
    self.parse1 = self.parse_tag_attr_0
    return i1

  ATTRVALUE_SOMETHING = re.compile(r'[^\s]')
  def parse_tag_attrvalue_0(self, x, i0):
    # looking for a attrvalue...
    m = self.ATTRVALUE_SOMETHING.search(x, i0)
    if not m:
      return -1
    i1 = m.start(0)
    c = x[i1]
    self.attr_value = ''
    if c == '<' or c == '>':
      # value end
      self.parse1 = self.parse_tag_attr_0
    elif c == '"':
      self.not_attrvalue = self.NOT_ATTRVALUE_DQ
      self.parse1 = self.parse_tag_attrvalue_1
      i1 += 1
    elif c == "'":
      self.not_attrvalue = self.NOT_ATTRVALUE_SQ
      self.parse1 = self.parse_tag_attrvalue_1
      i1 += 1
    else:
      self.not_attrvalue = self.NOT_ATTRVALUE0
      self.parse1 = self.parse_tag_attrvalue_1
    return i1

  NOT_ATTRVALUE0 = re.compile(r'[\s><&]')
  NOT_ATTRVALUE_DQ = re.compile(r'[&\"]')
  NOT_ATTRVALUE_SQ = re.compile(r'[&\']')
  ATTRVALUE_MAXCHARS = 4000
  def parse_tag_attrvalue_addentity(self, c):
    self.attr_value += c
    return
  def parse_tag_attrvalue_1(self, x, i0):
    # eating characters for a value...
    m = self.not_attrvalue.search(x, i0)
    if not m:
      if len(self.attr_value) < self.ATTRVALUE_MAXCHARS:
        assert i0 < len(x)
        self.attr_value += x[i0:]
      return -1
    i1 = m.start(0)
    if len(self.attr_value) < self.ATTRVALUE_MAXCHARS:
      self.attr_value += x[i0:i1]
    c = x[i1]
    if c == '&':
      # "call" the entityref parser.
      self.feed_entity = self.parse_tag_attrvalue_addentity
      self.parse0 = self.parse_tag_attrvalue_1
      self.parse1 = self.parse_entity_0
      return i1
    # end of value.
    if self.attr_name:
      self.tag_attrs.append((self.attr_name, self.attr_value))
      self.attr_name = ''
    self.parse1 = self.parse_tag_attr_0
    if c == "'" or c == '"':
      i1 += 1
    return i1

  # Parse SGML declarations or comments.
  
  DECLSTR_MAXCHARS = 1000 # maxchars for decl tag.
  def parse_decl(self, x, i0):
    if x[i0] == '-':
      self.parse1 = self.parse_comment_0
      return i0+1
    try:
      i1 = x.index('>', i0)
      if len(self.decl_string) < self.DECLSTR_MAXCHARS:
        self.decl_string += x[i0:i1]
      self.handle_decl(self.decl_string)
      self.parse1 = self.parse_pcdata
      i1 += 1
    except ValueError:
      if len(self.decl_string) < self.DECLSTR_MAXCHARS:
        self.decl_string += x[i0:]
      i1 = -1
    return i1

  # beginning '-'
  def parse_comment_0(self, x, i0):
    if x[i0] == '-':
      return i0+1
    elif x[i0] == '>':
      self.parse1 = self.parse_comment_2
    else:
      self.handle_start_tag('comment', {})
      self.parse1 = self.parse_comment_1
    return i0
  
  def parse_comment_1(self, x, i0):
    try:
      i1 = x.index('-', i0)
      if i0 < i1:
        self.handle_characters(x[i0:i1])
      self.parse1 = self.parse_comment_2
      self.comment_minuses = 1
      i1 += 1
    except ValueError:
      assert i0 < len(x)
      self.handle_characters(x[i0:])
      i1 = -1
    return i1
  
  # trailing '-'
  COMMENT_MAXMINUSES = 1000
  def parse_comment_2(self, x, i0):
    c = x[i0]
    if c == '>':
      self.handle_end_tag('comment', {})
      self.parse1 = self.parse_pcdata
      return i0+1
    elif c == '-':
      self.comment_minuses += 1
      return i0+1
    self.handle_characters(u'-' * min(self.comment_minuses, self.COMMENT_MAXMINUSES))
    self.parse1 = self.parse_comment_1
    return i0
    

##  HTMLHandler
##
class HTMLHandler:

  """
  HTMLHandler class receive All text data and SGML entities
  are converted to Unicode strings and passed to handle_data
  method.  Comments are also converted to Unicode strings and
  passed to handle_comment method. At every occurrence of TAG,
  start_TAG and end_TAG are called. If there is no such a method,
  start_unknown and end_unknown are called at the beginning tag and
  the end tag respectively.
  """

  def set_charset(self, charset):
    return

  def start_unknown(self, tag, attrs):
    """Handles the beginning of an unknown tag."""
    print "HTMLHandler: start_unknown: tag=%s, attrs=%r" % (tag, attrs)
    return
  
  def end_unknown(self, tag):
    """Handles the end of an unknown tag."""
    print "HTMLHandler: end_unknown: tag=%s" % tag
    return
  
  def handle_data(self, data):
    """Handles text data and SGML entities."""
    print "HTMLHandler: handle_data: data=%r" % data
    return
  
  def finish(self):
    """Called when the parser reaches at the end of file."""
    return


##  HTMLParser3
##
##     <HTML>, <BODY>, <HEAD>, <BASE>, .. only once in a document.
##     <BR>, <AREA>, <LINK>, <IMG>, <PARAM>, <INPUT>, <COL>, <FRAME>, <META> .. no data inside.
##     <HR>, no data inside, but end previous <p>
##     <P>, ... end previous <p>
##     block: <h?><ul><ol><dl><pre><div><center><noscript><noframes>
##            <blockquote><form><hr><table><fieldset><address> end previous <p>
##     <DT>, <DD> ... end previous <dd> or <dt>
##     <LI>, ... end previous <li>
##     <OPTION>, ... end previous <OPTION>
##     <THEAD>, <TFOOT>, <TBODY>, ... end previous <THEAD>, <TFOOT>, <TBODY>
##     <COLGROUP>, ... end previous <COLGROUP>,
##     <TR>, ... end previous <TR>, <TD> or <TH>
##     <TD>, <TH> ... end previous <TD> or <TH>
##
class HTMLParser3(SGMLParser3):
  """
  An HTML parser class which handles internationalized text.
  """

  # default charset
  DEFAULT_CHARSET = 'iso-8859-1'

  TAGSTOP = {
    'td':('tr','table',),
    'tr':('table',),
    'li':('ul','ol',),
    'dt':('dl',),
    'dd':('dl',)
    }

  valid_tags = VALID_TAGS
  
  def __init__(self, handler, charset=DEFAULT_CHARSET, debug=0):
    SGMLParser3.__init__(self)
    self.debug = debug
    self.linebuf = ''
    self.handler = handler
    self.set_charset(charset)
    self.tagstack = []
    if self.debug:
      print >>sys.stderr, 'HTMLParser3: start'
    return
  
  def set_charset(self, charset):
    """Changes the current charset and codec."""
    if self.debug:
      print >>sys.stderr, 'set_charset: %s' % charset
    self.codec = getcodec(charset)
    self.handler.set_charset(charset)
    return

  def handle_characters(self, data):
    """Handles text."""
    if self.debug:
      print >>sys.stderr, 'handle_data: %r' % data
    self.handler.handle_data(data)
    return

  def handle_directive(self, name, attrs):
    return
  
  def handle_decl(self, data):
    if self.debug:
      print >>sys.stderr, 'handle_decl: %r' % data
    return

  CHARSET_FIND = re.compile(r'charset\s*=\s*([^">;\s]+)', re.I)
  def hook_charset(self, attrs):
    if attrs.get('http-equiv','').lower() == 'content-type':
      m = self.CHARSET_FIND.search(attrs['content'])
      if m:
        self.set_charset(m.group(1).lower())
    elif 'charset' in attrs:
      self.set_charset(attrs['charset'].lower())
    return

  def feedline(self, line):
    assert isinstance(line, str)
    self.linebuf = ''
    try:
      line = unicode(line, self.codec, 'replace')
    except UnicodeError:
      line = unicode(line, 'ascii', 'replace')
    SGMLParser3.feed(self, line)
    return self

  NEWLINE = re.compile(r'\r\n?|\n')
  def feed(self, data):
    if not data:
      return self.feedline(self.linebuf)
    i = 0
    while 1:
      # feed line by line.
      m = self.NEWLINE.search(data, i)
      if not m:
        self.linebuf += data[i:]
        break
      self.feedline(self.linebuf+data[i:m.end(0)])
      i = m.end(0)
    return self

  def feed_unicode(self, data):
    assert isinstance(data, unicode)
    return SGMLParser3.feed(self, data)

  def feedfile(self, fp, size=4096):
    while True:
      s = fp.read(size)
      if not s: break
      self.feed(s)
    self.feed('')
    return self

  def handle_start_tag(self, tag, attrs):
    if self.valid_tags and tag not in self.valid_tags:
      if self.debug:
        print >>sys.stderr, 'ignored:', tag
      return
    if self.debug:
      print >>sys.stderr, 'start: <%s> attrs=%r' % (tag, attrs)
    attrs = dict(attrs)
    if tag in INLINE_IMMED:
      if tag == 'hr':
        self.end_previous(('p',), BLOCK)
      elif tag == 'meta':
        self.hook_charset(attrs)
      # dispatch
      methodname = 'start_'+tag
      if hasattr(self.handler, methodname):
        getattr(self.handler, methodname)(tag, attrs)
      else:
        self.handler.start_unknown(tag, attrs)
      methodname = 'end_'+tag
      if hasattr(self.handler, methodname):
        getattr(self.handler, methodname)(tag)
      else:
        self.handler.end_unknown(tag)
    else:
      # sorry for yucky tuple syntax... :(
      if tag in ('dt', 'dd'):
        self.end_previous(('dt', 'dd',), ('dl',))
      elif tag == 'li':
        self.end_previous(('li',), ('ul','ol',))
      elif tag == 'option':
        self.end_previous(('option',), ('select',))
      elif tag in ('thead', 'tfoot', 'tbody'):
        self.end_previous(('thead', 'tfoot', 'tbody',), ('table',))
      elif tag == 'colgroup':
        self.end_previous(('colgroup',), ('table',))
      elif tag == 'tr':
        self.end_previous(('tr',), ('table',))
      elif tag in ('td', 'th'):
        self.end_previous(('td', 'th',), ('tr', 'table',))
      elif tag in BLOCK:
        self.end_previous(('p',), BLOCK)
      elif tag in CDATA:
        self.start_cdata(tag)
      if tag not in NON_NESTED:
        self.tagstack.append(tag)
      # dispatch
      methodname = 'start_'+tag
      if hasattr(self.handler, methodname):
        getattr(self.handler, methodname)(tag, attrs)
      else:
        self.handler.start_unknown(tag, attrs)
    return

  def handle_end_tag(self, tag, attrs):
    if self.valid_tags and tag not in self.valid_tags:
      if self.debug:
        print >>sys.stderr, 'ignored:', tag
      return
    if tag in NON_NESTED:
      methodname = 'end_'+tag
      if hasattr(self.handler, methodname):
        getattr(self.handler, methodname)(tag)
      else:
        self.handler.end_unknown(tag)        
    elif tag not in INLINE_IMMED:
      self.end_previous((tag,), self.TAGSTOP.get(tag, ()))
    return

  def end_previous(self, tags, stops):
    for i in range(len(self.tagstack)-1, -1, -1):
      t = self.tagstack[i]
      if t in tags:
        for tag in self.tagstack[i:]:
          if self.debug:
            print >>sys.stderr, 'end: </%s>' % tag
          methodname = 'end_'+tag
          if hasattr(self.handler, methodname):
            getattr(self.handler, methodname)(tag)
          else:
            self.handler.end_unknown(tag)        
        self.tagstack = self.tagstack[:i]
        break
      elif t in stops:
        break
    return

  def close(self):
    self.feed('')
    SGMLParser3.close(self)
    while self.tagstack:
      self.end_previous(self.tagstack, ())
    if self.debug:
      print >>sys.stderr, 'HTMLParser3: close'
    return self.handler.finish()


# test
if __name__ == '__main__':
  import getopt, urllib
  def usage():
    print "usage: htmlparser3.py [-d] [-c charset] [url ...]"
    sys.exit(2)
  try:
    (opts, args) = getopt.getopt(sys.argv[1:], "dc:")
  except getopt.GetoptError:
    usage()
  (debug, charset) = (False, 'iso-8859-1')
  for (k, v) in opts:
    if k == "-d": debug += 1
    elif k == "-c": charset = v
  for fname in args:
    parser = HTMLParser3(HTMLHandler(), charset, debug)
    fp = urllib.urlopen(fname)
    while 1:
      s = fp.read(4096)
      if not s: break
      parser.feed(s)
    fp.close()
    parser.close()
