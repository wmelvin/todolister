#!/usr/bin/env python3

#----------------------------------------------------------------------
# todolister.py
#
# 
#
# 2020-11-22
#----------------------------------------------------------------------


from pathlib import Path
from collections import namedtuple
from datetime import datetime
import re


ScanProps = namedtuple('ScanProps', 'dir_name, do_recurse')

FileInfo = namedtuple('FileInfo', 'last_modified, full_name')

TodoFile = namedtuple('TodoFile', 'last_modified, full_name, todo_items')


#dirs_to_scan = [ScanProps('~/Desktop/wemDesk/txt', True)]
dirs_to_scan = [ScanProps('./test', True)]

file_specs = ['^notes.*.txt', '.*notes.txt', '^todo.*.txt', '.*-todo.txt']

css_file_name = Path.cwd() / "style.css"

css_mode = 2  
# 0 = link to external css file.
# 1 = embed from external css file. 
# 2 = embed from function embed_style.

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
            #file_list.append(FileInfo(ts.strftime('%Y-%m-%dT%H:%M:%S'), str(f)))
            file_list.append(FileInfo(ts.strftime('%Y-%m-%d %H:%M'), str(f)))


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
                    #todo_text += "{0}\n".format(line)
                    todo_text += line
            else: 
                if stripped.startswith('[ ]'):
                    in_todo = True
                    #todo_text += "{0}\n".format(line)
                    todo_text += line

        # Save last item, in case there were no blank lines at the 
        # end of the file.
        if len(todo_text) > 0:
            todo_items.append(todo_text)
            todo_text = ''

    return todo_items


def get_css_from_file(indent_len):
    css = ''
    indent = ' ' * indent_len
    with open(css_file_name, 'r') as css_file:
        lines = css_file.readlines()
        for line in lines:
            if len(line.strip()) > 0:
                css += "{0}{1}".format(indent, line)
    return f"{css}\n"


def embed_style():
    # Changes made in external css file pasted here from html output
    # after running with css_mode = 1. 
    return '''
    <style>
        #wrapper {
            padding: 10px;
        }
        #content {
            max-width: 960px;
        }
        .fileheader {
            margin-top: 10px;
            /*
            border-color: blue;
            border-style: solid;
            */
            border: 1px solid rgb(95, 238, 238);    
            background-color: rgb(207, 240, 240);
            padding: 10px;
            border-radius: 12px;
        }
        .filename {
            font-family: monospace;
            font-size: large;
            color: navy;
        }
        .filetime {
            font-family: monospace;
            font-size: small;
            color: darkslategrey;  
            margin-left: 5px;
        }
        .filecontent {
            margin-left: 20px;
            margin-right: 20px;
            margin-bottom: 20px;
        }
        .item0, .item1 {
            padding-left: 10px;
            padding-top: 5px;
            border-radius: 8px;
        }
        .item0 {
            background-color: rgb(232, 248, 250);
        }
        .item1 {
            /* background-color: rgb(250, 250, 240); */
            /* background-color: rgb(250, 249, 240); */
            background-color: rgb(250, 250, 232);
        }
    </style>''' + "\n"


def html_head(title):
    s = "<!DOCTYPE html>\n"
    s += "<html lang=\"en\">\n"
    s += "<head>\n"
    s += "    <meta charset=\"UTF-8\">\n"
    s += "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
    s += "    <title>{0}</title>\n".format(title)
    
    if css_mode == 2:
        s += embed_style()
    elif css_mode == 1:
        s += "    <style>\n"
        s += get_css_from_file(indent_len = 8)
        s += "    </style>\n"
    else:
        s += "    <link rel=\"stylesheet\" href=\"style.css\" />\n"

    s += "</head>\n"
    s += "<body>\n"
    return s


def html_tail():
    s = "</body>\n"
    s += "</html>\n"
    return s


def todo_file_html(file_name, last_modified):
    s = "<div class=\"fileheader\">\n"
    s += "  <p class=\"filename\">{0}</p>\n".format(file_name)
    s += "  <p class=\"filetime\">{0}</p>\n".format(last_modified)
    s += "</div>\n"
    return s


def html_text(text):
    s = text.replace("&", "&amp;")
    #s = s.replace(" ", "&nbsp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    #s = s.replace("\n", "<br />\n")
    return s


def todo_item_html(item, row):
    s = "<div class=\"item{0}\">\n".format(row % 2)
    s += "<pre>\n{0}\n</pre>\n".format(html_text(item))
    s += "</div>\n"
    return s


#----------------------------------------------------------------------

file_list = []

for dir in dirs_to_scan:
    get_matching_files(dir.dir_name, dir.do_recurse)

file_list.sort()
file_list.reverse()

# print('LIST OF FILES')
# for a in file_list:
#     print(a)

print('READ CONTENTS')

todo_files = []

for file_info in file_list:
    print("Reading file [{0}]".format(file_info.full_name))    
    items = get_todo_items(file_info.full_name)
    todo_files.append(TodoFile(file_info.last_modified, file_info.full_name, items))


# print('LIST ITEMS')
# for todo_file in todo_files:
#     print(todo_file.full_name)
#     print(todo_file.last_modified)
#     for item in todo_file.todo_items:
#         print(item)
# print(f"\n")


# Oh no, Pascal!
def writeln(a_file, a_string):
    a_file.write(a_string + "\n")


with open(out_file_name, 'w') as f:
    writeln(f, html_head('ToDo Items'))
    
    writeln(f, '<div id="wrapper">')
    writeln(f, '<div id="content">')

    writeln(f, '<h1>To-do Items</h1>')

    for todo_file in todo_files:
        writeln(f, todo_file_html(todo_file.full_name, todo_file.last_modified))
        writeln(f, '<div class="filecontent">')
        row = 0
        for item in todo_file.todo_items:
            row += 1
            writeln(f, todo_item_html(item, row))
        writeln(f, '</div>  <!--filecontent  -->')
        writeln(f, '')

    writeln(f, '</div>  <!--content  -->')
    writeln(f, '</div>  <!--wrapper  -->')
    writeln(f, html_tail())


print(f"\n{out_file_name} done.")
