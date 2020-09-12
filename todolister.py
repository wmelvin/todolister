#!/usr/bin/env python3

#----------------------------------------------------------------------
# todolister.py
#
# 
#
# 2020-09-11
#----------------------------------------------------------------------


from pathlib import Path
from collections import namedtuple
from datetime import datetime

TodoFile = namedtuple('TodoFile', 'last_modified, full_name')
ScanProps = namedtuple('ScanProps', 'dir_name, do_recurse')

dirs_to_scan = [ScanProps('~/Desktop/wemDesk/txt', True)]

file_specs = ['notes*.txt', 'todo*.txt']

file_list = []

for dir in dirs_to_scan:
    p = Path(dir.dir_name)
    for file_spec in file_specs:
        if dir.do_recurse:
            files = p.rglob(file_spec)
        else:
            files = p.glob(file_spec)
        for f in files:
            #file_list.append(str(f))
            ts = datetime.fromtimestamp(f.stat().st_mtime)
            file_list.append(TodoFile(ts.strftime('%Y-%m-%dT%H:%M:%S'), str(f)))

file_list.sort()
file_list.reverse()

for a in file_list:
    print(a)


#----------------------------------------------------------------------
# NEXT: 
# For each file
#   get content
#   for each line
#      if match to-do marker
#         add connected lines to todo-items-list
# Write todo-items-list to HTML file.  
#   html_header
#   html_style
#   html_body
#   html_footer
#
# Seems like this is simple enough that using html templates is not necessary.
#
#----------------------------------------------------------------------


print('Done.')
