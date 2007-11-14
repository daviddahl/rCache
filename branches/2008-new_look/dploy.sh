#!/bin/bash
#svn url
export SVN_URL='file:///var/svn/repo_rcache/branches/2008-new_look'  
#'file:///var/svn/rcache rcache'
#datestr
export THE_DATE=`date +%C%y%m%d%H%M`
#create dir for new export from svn
mkdir /usr/local/lib/dploy/$THE_DATE
#chang dir
cd /usr/local/lib/dploy/$THE_DATE
#svn export command
svn export $SVN_URL
#byte-compile the whole dir
python /usr/lib/python2.4/compileall.py /usr/local/lib/dploy/$THE_DATE/rcache
#remove symlink
rm /usr/local/lib/dploy/rcache
#make symlink
ln -s /usr/local/lib/dploy/$THE_DATE/rcache /usr/local/lib/rcache
#restart apache
apache2ctl restart
