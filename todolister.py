#!/usr/bin/env python3

#----------------------------------------------------------------------
# todolister.py
#
# 
#
# 2020-11-27
#----------------------------------------------------------------------

from pathlib import Path
from collections import namedtuple
from datetime import datetime
import re
import argparse


ScanProps = namedtuple('ScanProps', 'dir_name, do_recurse')

FileInfo = namedtuple('FileInfo', 'last_modified, full_name')

TodoItem = namedtuple('TodoItem', 'is_flagged, is_elevated, item_text')

TodoFile = namedtuple('TodoFile', 'last_modified, full_name, todo_items')


app_version = '20201127.1'

css_mode = 0
# 0 = link to external css file (use for trying css changes).
# 1 = embed from external css file (use to get css to update embed_style).
# 2 = embed from function embed_style.


default_file_specs = ['^notes.*.txt', '.*notes.txt', '^todo.*.txt', '.*-todo.txt']

css_file_name = Path.cwd() / "style.css"

default_output_file = Path.cwd() / "todolist.html"


def matches_filespec(file_name):
    for spec in file_specs:
        if re.search(spec.lower(), file_name.lower()):
            return True
    return False


def get_matching_files(dir_name, do_recurse):
    p = Path(dir_name).resolve()

    for f in [x for x in p.iterdir() if x.is_file()]:
        if matches_filespec(f.name):
            ts = datetime.fromtimestamp(f.stat().st_mtime)
            file_list.append(FileInfo(ts.strftime('%Y-%m-%d %H:%M'), str(f)))

    if do_recurse:
        for d in [x for x in p.iterdir() if x.is_dir() and not x.is_symlink()]:
            get_matching_files(d, do_recurse)


def get_todo_items(file_name):
    todo_items = []
    with open(file_name, 'r', errors='replace') as text_file:
        in_todo = False
        todo_text = ''
        is_flagged = False
        is_elevated = False
        lines = text_file.readlines()
        for line in lines:
            stripped = line.strip()
            if in_todo:
                if len(stripped) == 0:
                    in_todo = False
                    if len(todo_text) > 0:
                        todo_items.append(TodoItem(is_flagged, is_elevated, todo_text))
                        todo_text = ''
                        is_flagged = False
                        is_elevated = False
                else:
                    todo_text += line
            else:
                if stripped.startswith('[ ]'):
                    in_todo = True
                    is_flagged = stripped.startswith('[ ]*')
                    is_elevated = stripped.startswith('[ ]+')
                    todo_text += line

        # Save last item, in case there were no blank lines at the
        # end of the file.
        if len(todo_text) > 0:
            todo_items.append(TodoItem(is_flagged, is_elevated, todo_text))

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
        #footer {
            border-top: 2px solid lightslategray;
            font-family: monospace;
            font-size: medium;
            color: navy;
        }
        .fileheader {
            border: 1px solid rgb(95, 238, 238);    
            background-color: rgb(207, 240, 240);
            padding-left: 10px;
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
            margin-bottom: 25px;
        }
        pre {
            margin: 0px;
        }
        .item0, .item1 {
            padding-left: 10px;
            padding-top: 5px;
            border-radius: 8px;
            margin: 4px 0 8px;
        }
        .item0 {
            background-color: rgb(232, 248, 250);
        }
        .item1 {
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
    s += "  <p class=\"filetime\">Modified {0}</p>\n".format(last_modified)
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
    if item.is_flagged or item.is_elevated:
        add_class = ' flagged'
    else:
        add_class = ''
    s = "<div class=\"item{0}{1}\">\n".format(row % 2, add_class)
    s += "<pre>\n{0}\n</pre>\n".format(html_text(item.item_text))
    s += "</div>\n"
    return s


def get_option_entries(opt_section, opt_content):
    result = []
    in_section = False
    for line in opt_content:
        s = line.strip()
        if len(s) == 0:
            in_section = False
        else:
            if in_section:
                # Handle new section w/o blank lines between.
                if s.startswith('['):
                    in_section = False
                # Support whole-line comments identified by '#' (ignore them).
                elif not s.startswith('#'):
                    result.append(s)
            if s == opt_section:
                in_section = True
    return result


def get_file_specs(default_specs, opt_content):
    entries = get_option_entries('[match]', opt_content)
    if len(entries) == 0:
        return default_specs
    else:
        return [entry.strip("'\" ") for entry in entries]
    

def get_dirs_to_scan(default_dirs, opt_content):
    entries = get_option_entries('[folders]', opt_content)
    if len(entries) == 0:
        return default_dirs
    else:
        dirs = []
        for entry in entries:
            recurse = False
            s = entry.strip()
            if s.endswith('+'):
                recurse = True
                s = s.strip('+')
            s = s.strip("'\" ")
            dirs.append(ScanProps(s, recurse))
        return dirs


def get_output_filename(given_filename):
    p = Path(given_filename).resolve()
    if p.suffix.lower() == '.html':
        return str(p)
    else:
        return str(p.with_suffix('.html'))


# Oh no, Pascal!
def writeln(a_file, a_string):
    a_file.write(a_string + "\n")


#----------------------------------------------------------------------

# Note: Using the term 'folder' instead of 'directory' in argument 
# descriptions.

ap = argparse.ArgumentParser(
	description =
	'Read text files containing to-do markers and create a HTML report.')

ap.add_argument(
	'folders', 
    nargs = '*',
    default = [str(Path.cwd())],
	action = 'store', 
	help = 'Folder(s) to scan. Multiple folders can be specified.')

ap.add_argument(
	'-f', '--options-file', 
	dest = 'optfile', 
	action = 'store', 
	help = 'Name of options file.')

ap.add_argument(
	'-r', '--recurse', 
	dest = 'recurse', 
	action = 'store_true', 
	help = 'Recurse sub-folders. Applies to all folders specified. '
        + 'Use an options file to specify the recurse option for '
        + 'individual folders.')

ap.add_argument(
	'-o', '--output-file', 
	dest = 'output_file',
    default = default_output_file,
	action = 'store', 
	help = "Name of output file. The '.html' extension will be " 
        + "added if not specified." )

args = ap.parse_args()

#print(f"optfile={args.optfile}")
#print(f"recurse={args.recurse}")

dirs_to_scan = []
for folder in args.folders:
    folder = str(Path(folder).resolve())
    print(f"Folder {folder}")
    if not Path(folder).exists():
    	raise SystemExit('Path not found: ' + folder)
    dirs_to_scan.append(ScanProps(folder, args.recurse))

if args.optfile is None:
    file_specs = default_file_specs
else:
    p = Path(args.optfile).resolve()
    if not p.exists():
    	raise SystemExit(f"Options file not found: {p}")
    with open(p, 'r') as f:
        opt_lines = f.readlines()
    file_specs = get_file_specs(default_file_specs, opt_lines)
    dirs_to_scan = get_dirs_to_scan(dirs_to_scan, opt_lines)

    
# raise SystemExit('STOPPED')


#----------------------------------------------------------------------

file_list = []

for dir in dirs_to_scan:
    print(f"Scanning folder [{dir.dir_name}]")
    get_matching_files(dir.dir_name, dir.do_recurse)

file_list.sort()
file_list.reverse()

todo_files = []

for file_info in file_list:
    print("Reading file [{0}]".format(file_info.full_name))
    items = get_todo_items(file_info.full_name)
    todo_files.append(TodoFile(file_info.last_modified, file_info.full_name, items))

out_file_name = get_output_filename(args.output_file)

print("Writing file [{0}].".format(out_file_name))

with open(out_file_name, 'w') as f:
    writeln(f, html_head('ToDo Items'))

    writeln(f, '<div id="wrapper">')
    writeln(f, '<div id="content">')

    writeln(f, '<h1>To-do Items</h1>')

    #TODO: Write flagged items section.

    for todo_file in todo_files:
        if len(todo_file.todo_items) > 0:
            writeln(f, todo_file_html(todo_file.full_name, todo_file.last_modified))
            writeln(f, '<div class="filecontent">')
            row = 0
            for item in todo_file.todo_items:
                row += 1
                writeln(f, todo_item_html(item, row))
            writeln(f, '</div>  <!--filecontent  -->')
            writeln(f, '')

    writeln(f, '<div id="footer">')
    writeln(f, 'Created {0} by todolister.py (version {1}).'.format(
        datetime.now().strftime('%Y-%m-%d %H:%M'), 
        app_version
    ))
    writeln(f, '</div>')
    writeln(f, '')
    writeln(f, '</div>  <!--content  -->')
    writeln(f, '</div>  <!--wrapper  -->')
    writeln(f, html_tail())


print("Done.")
