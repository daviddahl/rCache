#!/bin/bash

cd code/rcache_django/rcache/
rm *.pyc
svn up
python /usr/lib/python2.4/compileall.py .
sudo apache2ctl restart
