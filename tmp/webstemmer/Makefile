# Makefile

VERSION=0.6.0
DESTDIR=/tmp/please/specify/the/directory

FILES=Makefile \
	README.txt \
	analyze.py \
	extract.py \
	htmldom.py \
	htmlparser3.py \
	htmlutils.py \
	httplib.py \
	zipdb.py \
	layoutils.py \
	urldbutils.py \
	html2txt.py \
	textcrawler.py \
	perf.py

all:

clean:
	-rm *.pyc *.pyo *~

pack: clean
	ln -s webstemmer ../webstemmer-$(VERSION)
	cd ..; gtar c -z --dereference -f webstemmer-$(VERSION).tar.gz webstemmer-$(VERSION) \
		--exclude OLD --exclude '*.obj'
	rm ../webstemmer-$(VERSION)

install: clean
	[ -d $(DESTDIR) ] && cp $(FILES) $(DESTDIR)

