#!/usr/bin/env python3

#----------------------------------------------------------------------
# todolister.py
#
# 
#
# 2020-11-21
#----------------------------------------------------------------------


from pathlib import Path
from collections import namedtuple
from datetime import datetime
import re


ScanProps = namedtuple('ScanProps', 'dir_name, do_recurse')

TodoFile = namedtuple('TodoFile', 'last_modified, full_name')

TodoContent = namedtuple('TodoContent', 'last_modified, full_name, todo_items')


#dirs_to_scan = [ScanProps('~/Desktop/wemDesk/txt', True)]
dirs_to_scan = [ScanProps('./test', True)]

file_specs = ['^notes.*.txt', '.*notes.txt', '^todo.*.txt', '.*-todo.txt']

css_file_name = Path.cwd() / "style.css"

do_embed_css = True

out_file_name = Path.cwd() / "todolist.html"


def matches_filespec(file_name):
    for spec in file_specs:
        if re.search(spec.lower(), file_name.lower()):
            return True
    return False


def get_matching_files(dir_name, do_recurse):
    p = Path(dir_name).resolve()
    
    if do_recurse:
        for d in [x for x in p.iterdir() if x.is_dir()]:
            get_matching_files(d, do_recurse)

    for f in [x for x in p.iterdir() if x.is_file()]:
        if matches_filespec(f.name):
            ts = datetime.fromtimestamp(f.stat().st_mtime)
            file_list.append(TodoFile(ts.strftime('%Y-%m-%dT%H:%M:%S'), str(f)))


def get_todo_items(file_name):
    todo_items = []
    with open(file_name, 'r') as text_file:
        in_todo = False
        todo_text = ''
        lines = text_file.readlines()        
        for line in lines:
            stripped = line.strip()
            if in_todo:
                if len(stripped) == 0:
                    in_todo = False
                    if len(todo_text) > 0:
                        todo_items.append(todo_text)
                        todo_text = ''
                else:
                    todo_text += "{0}\n".format(line)
            else: 
                if stripped.startswith('[ ]'):
                    in_todo = True
                    todo_text += "{0}\n".format(line)

        # Save last item, in case there were no blank lines at the 
        # end of the file.
        if len(todo_text) > 0:
            todo_items.append(todo_text)
            todo_text = ''

    return todo_items


# *!* NEXT: html_style

#def add_line(existing_text, indent, new_text):
#    return "{0}\n{1}{2}".format(existing_text, (" " * indent), new_text)

# def style_css(indent):
#     s = ''
#     s = add_line(s, indent, "<style>")
#     s = add_line(s, indent, "</style>")
#     return s


def get_css(indent_len):
    css = ''
    indent = ' ' * indent_len
    with open(css_file_name, 'r') as css_file:
        lines = css_file.readlines()
        for line in lines:
            if len(line.strip()) > 0:
                css += "{0}{1}".format(indent, line)
    return f"{css}\n"


def html_head(title):
    s = "<!DOCTYPE html>\n"
    s += "<html lang=""en"">\n"
    s += "<head>\n"
    s += "    <meta charset=""UTF-8"">\n"
    s += "    <meta name=""viewport"" content=""width=device-width, initial-scale=1.0"">\n"
    s += f"    <title>{title}</title>\n"
    
    if do_embed_css:
        s += "    <style>\n"
        s += get_css(8)
        s += "    </style>\n"
    else:
        s += "    <link rel=""stylesheet"" href=""style.css"" />\n"

    s += "</head>\n"
    s += "<body>\n"
    return s


def html_tail():
    s = "</body>\n"
    s += "</html>\n"
    return s



#----------------------------------------------------------------------

file_list = []

for dir in dirs_to_scan:
    get_matching_files(dir.dir_name, dir.do_recurse)

file_list.sort()
file_list.reverse()

print('LIST OF FILES')

for a in file_list:
    print(a)

print('READ CONTENTS')

todo_list = []

for a in file_list:
    print("---[{0}]".format(a.full_name))    

    todo_items = get_todo_items(a.full_name)

    #for item in todo_items:
    #    print(item)

    todo_list.append(TodoContent(a.last_modified, a.full_name, todo_items))
    

print('LIST ITEMS')
for todo_item in todo_list:
    print(todo_item.full_name)
    print(todo_item.last_modified)
    for item in todo_item.todo_items:
        print(item)



with open(out_file_name, 'w') as output_file:
    output_file.write(html_head('TEST'))
    output_file.write("<h1>TEST</h1>\n")
    output_file.write("<div class=""fileheader"">File Header</div>\n")
    output_file.write(html_tail())


print('Done.')
