#!/usr/bin/python

import os
import sys
import glob
import time
import gzip
from optparse import OptionParser


def old_backup_list(pth):
    old = []
    now = time.time()
    two_days_ago = now - (86400 *2)
    print pth
    try:
        bckup_lst = os.listdir(pth) 
        print bckup_lst
        for bck in bckup_lst:
            the_path = os.path.join(pth, bck)
            ctime = os.path.getctime(the_path)
            if ctime < two_days_ago:
                old.append(bck)
        return old
    except Exception,e:
        print e

def delete_files(pth_lst):
    for pth in pth_lst:
        os.remove(pth)

def back_up_pth(pth,ext):
    dte = str(time.strftime('%Y%m%d%H%M%S'))
    dte += ext
    return os.path.join(pth, dte)

def gzip_sh(pth):
    cmd = "gzip %s" % pth
    try:
        os.popen(cmd)
        return True
    except:
        return False

def gzipit(pth,data):
    fileObj = gzip.GzipFile(pth, 'wb');
    fileObj.write(fileContent)
    fileObj.close()

def open_backup(path):
    f = open(path)
    lines = f.readlines()
    data = "\n".join(lines)
    return data

def make_backup(db,passwd,pth):
    try:
        cmd = "mysqldump -u root -p%s %s > %s" % (passwd,db,pth,)
        results = os.popen(cmd)
        return True
    except:
        return False

def make_svn_backup(repo,pth):
    try:
        cmd = "svnadmin dump %s > %s" % (repo,pth,)
        results = os.popen(cmd)
        return True
    except:
        return False

    
if __name__ == '__main__':
    
    parser = OptionParser()
    parser.add_option("-b", "--backup", dest="backup_type",
                      help="Which backup to do: s - SVN or d - DATABASE")
    
    opt_args = parser.parse_args()
    cfg = opt_args[0]
    
    backup_path = "/var/backups/rcache"
    if os.path.exists(backup_path):
        pass
    else:
        os.mkdir(backup_path)

    
    if cfg.backup_type == 'd':
        
        db = os.environ['RCACHE_DB_NAME']
        passwd = os.environ['RCACHE_DB_PASSWD']
        print "starting database backup..."
        this_backup = back_up_pth(backup_path,'.sql')
        print "saving to %s" % this_backup
        b = make_backup(db,passwd,this_backup)
        print "gzipping..."
        gzip_sh(this_backup)
        print "done."

    if cfg.backup_type == 's':
        
        print "starting SVN backup"
        this_backup = back_up_pth(backup_path,'.dump')
        print "saving to %s" % this_backup
        repo = os.environ['SVN_REPO']
        b = make_svn_backup(repo,this_backup)
        print "gzipping..."
        gzip_sh(this_backup)
        print "done."
        
