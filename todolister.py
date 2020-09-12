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


#dirs_to_scan = [ScanProps('~/Desktop/wemDesk/txt', True)]
dirs_to_scan = [ScanProps('./test', True)]

file_specs = ['notes*.txt', 'todo*.txt']


def matches_filespec(file_name):
    return True

def get_matching_files(dir_name, do_recurse):
    p = Path(dir_name).resolve()
    
    if do_recurse:
        for d in [x for x in p.iterdir() if x.is_dir()]:
            get_matching_files(d, do_recurse)

    for f in [x for x in p.iterdir() if x.is_file()]:
        if matches_filespec(f.name):
            ts = datetime.fromtimestamp(f.stat().st_mtime)
            file_list.append(TodoFile(ts.strftime('%Y-%m-%dT%H:%M:%S'), str(f)))



file_list = []

# for dir in dirs_to_scan:
#     p = Path(dir.dir_name).resolve()
#     for file_spec in file_specs:
#         if dir.do_recurse:
#             files = p.rglob(file_spec)
#         else:
#             files = p.glob(file_spec)
#         for f in files:
#             ts = datetime.fromtimestamp(f.stat().st_mtime)
#             file_list.append(TodoFile(ts.strftime('%Y-%m-%dT%H:%M:%S'), str(f)))

# for dir in dirs_to_scan:
#     p = Path(dir.dir_name).resolve()
#     for f in [x for x in p.iterdir() if x.is_file()]:
#         if matches_filespec(f.name):
#             ts = datetime.fromtimestamp(f.stat().st_mtime)
#             file_list.append(TodoFile(ts.strftime('%Y-%m-%dT%H:%M:%S'), str(f)))


for dir in dirs_to_scan:
    get_matching_files(dir.dir_name, dir.do_recurse)




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
