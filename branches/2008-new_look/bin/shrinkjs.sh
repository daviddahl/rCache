#!/bin/bash
export infile='/Users/dahl/Code/rcache_django/FFExt/src/rcache.js'
export outfile='/Users/dahl/Code/rcache_django/FFExt/rcache/chrome/content/rcache_compress.js'

export infile2='/Users/dahl/Code/rcache_django/FFExt/src/rclip.js'
export outfile2='/Users/dahl/Code/rcache_django/FFExt/rcache/chrome/content/rclip_compress.js'


java -jar custom_rhino.jar -c $infile > $outfile 2>&1
java -jar custom_rhino.jar -c $infile2 > $outfile2 2>&1
