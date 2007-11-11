#!/bin/bash
#svn url
export SVN_URL='file:///var/svn/repo_rcache rcache'
#datestr
export THE_DATE=`date +%C%y%m%d%H%M`
#create dir for new export from svn
mkdir /home/david/deploy/$THE_DATE
#chang dir
cd /home/david/deploy/$THE_DATE
#svn export command
svn export $SVN_URL
#byte-compile the whole dir
python /usr/lib/python2.4/compileall.py /home/david/deploy/$THE_DATE/rcache
#remove symlink
rm /home/david/deploy/rcache
#make symlink
ln -s /home/david/deploy/$THE_DATE/rcache /home/david/deploy/rcache
#restart apache
sudo apache2ctl restart
