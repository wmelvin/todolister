#!/usr/bin/env python3

# ---------------------------------------------------------------------
#  todolister.py
# ---------------------------------------------------------------------

import argparse
import re
import sys
import webbrowser

from collections import namedtuple
from datetime import datetime
from pathlib import Path
from typing import List


ScanProps = namedtuple("ScanProps", "dir_name, do_recurse")

FileInfo = namedtuple("FileInfo", "last_modified, full_name")

TodoItem = namedtuple(
    "TodoItem", "is_flagged, is_elevated, item_text, source_file"
)

TodoFile = namedtuple("TodoFile", "last_modified, full_name, todo_items")

AppOptions = namedtuple(
    "AppOptions",
    "folders, optfile, recurse, by_mtime, output_file, do_text, "
    "do_text_dt, no_html, page_title, no_browser",
)


app_version = "230926.1"
pub_version = "0.1.dev1"

app_name = Path(__file__).name
app_title = f"{app_name} (v.{app_version})"


css_mode = 2
# 0 = link to external css file (use for trying css changes).
# 1 = embed from external css file (use to get css to update embed_style).
# 2 = embed from function embed_style.

debug_stop_after_args = False

default_file_specs = [
    "^notes.*.md$",
    "^notes.*.txt$",
    ".*notes.txt$",
    "^todo.*.md$",
    "^todo.*.txt$",
    ".*-todo.txt$",
    "^Context-.*.txt$",
]

css_file_name = str(Path.cwd() / "style.css")

default_output_file = str(Path.cwd() / "from-todolister.html")

run_dt = datetime.now()

file_specs = []
dirs_to_scan = []
dirs_to_exclude = []
file_list = []
error_messages = []
todo_files: List[TodoFile] = []
flagged_items = []
item_tags = {}


def matches_filespec(file_name):
    for spec in file_specs:
        try:
            if re.search(spec.lower(), file_name.lower()):
                return True
        except Exception as e:
            msg = "ERROR bad match spec '{0}'. Error message: '{1}'".format(
                spec.lower(), e
            )
            print(msg)
            if msg not in error_messages:
                error_messages.append(msg)

    return False


def exclude_dir(dir_name):
    return any(dir_name == dir for dir in dirs_to_exclude)


# TODO: Is simple string match good enough?


def get_matching_files(dir_name, do_recurse):
    p = Path(dir_name).resolve()

    if exclude_dir(str(p)):
        print("  Exclude [{0}]".format(str(p)))
        return

    try:
        for f in [x for x in p.iterdir() if x.is_file()]:
            if matches_filespec(f.name):
                ts = datetime.fromtimestamp(f.stat().st_mtime)
                file_list.append(
                    FileInfo(ts.strftime("%Y-%m-%d %H:%M"), str(f))
                )

        if do_recurse:
            for d in [
                x for x in p.iterdir() if x.is_dir() and not x.is_symlink()
            ]:
                get_matching_files(d, do_recurse)

    except FileNotFoundError:
        msg = "ERROR (FileNotFoundError): Cannot scan directory {0}".format(
            dir_name
        )
        print(msg)
        error_messages.append(msg)

    except PermissionError:
        msg = "ERROR (PermissionError): Cannot scan directory {0}".format(
            dir_name
        )
        print(msg)
        error_messages.append(msg)


def get_todo_items(file_name):
    todo_items = []
    try:
        with open(file_name, "r", errors="replace") as text_file:
            in_todo = False
            todo_text = ""
            is_flagged = False
            is_elevated = False
            lines = text_file.readlines()
            for line_raw in lines:
                line_trim = line_raw.strip()
                if in_todo:
                    if not line_trim:
                        in_todo = False
                        if todo_text:
                            todo_items.append(
                                TodoItem(
                                    is_flagged,
                                    is_elevated,
                                    todo_text,
                                    file_name,
                                )
                            )
                            todo_text = ""
                            is_flagged = False
                            is_elevated = False
                    else:
                        todo_text += line_raw
                else:
                    if line_trim.startswith("[ ]"):
                        in_todo = True
                        is_flagged = line_trim.startswith("[ ]*")
                        is_elevated = line_trim.startswith("[ ]+")
                        todo_text += line_raw

            #  Save last item, in case there were no blank lines at the
            #  end of the file.
            if todo_text:
                todo_items.append(
                    TodoItem(is_flagged, is_elevated, todo_text, file_name)
                )

    except PermissionError:
        msg = "ERROR (PermissionError): Cannot read {0}".format(file_name)
        print(msg)
        error_messages.append(msg)
        todo_items.append(TodoItem(True, True, msg, file_name))

    return todo_items


# ---------------------------------------------------------------------
#  region -- CSS styling in output:


def get_css_from_file(indent_len):
    css = ""
    indent = " " * indent_len
    with open(css_file_name, "r") as css_file:
        lines = css_file.readlines()
        for line in lines:
            if line.strip():
                css += "{0}{1}".format(indent, line)
    css += "\n"
    return css


def embed_style():
    # Changes made in external css file pasted here from html output
    # after running with css_mode = 1.
    return """
    <style>
        h1 {color: steelblue;}
        h2 {color: slategrey;}
        #wrapper {padding: 10px;}
        #content {max-width: 960px;}
        #footer {
            border-top: 2px solid #999;
            font-family: monospace;
            font-size: 10px;
            color: #111;
        }
        #main {border-top: 2px solid #999;}
        .fileheader {
            border: 1px solid #9797CD;
            background-color: #EEF;
            padding-left: 10px;
        }
        .filename {
            font-family: monospace;
            font-size: large;
            font-weight: bold;
            color: navy;
        }
        .filetime {
            margin-left: 5px;
            font-family: monospace;
            font-size: small;
            color: #111;
        }
        .filecontent {
            margin-left: 20px;
            margin-right: 20px;
            margin-bottom: 25px;
        }
        .itemtext {
            margin: 0px;
            font-family: Consolas, monospace;
            font-size: 14px;
        }
        .item0, .item1 {
            padding-left: 10px;
            padding-top: 5px;
            margin: 4px 0 8px;
        }
        .item0 {background-color: #F5F5F5;}
        .item1 {background-color: #FFF;}
        .flagged {font-weight: bold;}
        #flagged_section, #tags_section, #contents_section {
            border-top: 2px solid #999;
            margin-bottom: 30px;
        }
        #flagged_items a, #tagged_items a, #contents_section a {
            font-family: monospace;
            font-size: large;
            color: navy;
        }
        #flagged_items {
            margin-left: 20px;
            margin-right: 20px;
            margin-bottom: 25px;
        }
        .flag0, .flag1 {
            padding-left: 10px;
            padding-top: 5px;
            margin: 4px 0 8px;
        }
        #tagged_items {margin-bottom: 25px;}
        .tag0, .tag1 {
            padding-left: 10px;
            padding-top: 5px;
            margin: 4px auto 8px 20px;
        }
        .flag0, .tag0 {background-color: #F5F5F5;}
        .flag1, .tag1 {background-color: #FFF;}
        .tagheader {
            margin-top: 20px;
            padding: 5px 5px 5px 10px;
            border: 1px solid rgb(231, 231, 146);
            background-color: rgb(250, 250, 232);
        }
        .toplink {font-size: x-small;}
        #contents_section h3 {margin-left: 20px;}
        #contents_section ul {margin-left: 20px;}
        #settings_section {
            border-top: 2px solid #999;
            font-family: 'Courier New', Courier, monospace;
            font-size: 12px;
        }
    </style>
    """


#  endregion

# ---------------------------------------------------------------------


def html_head(title):
    s = "<!DOCTYPE html>\n"
    s += '<html lang="en">\n'
    s += "<head>\n"
    s += '    <meta charset="UTF-8">\n'
    s += '    <meta name="viewport" content="'
    s += 'width=device-width, initial-scale=1.0">\n'
    s += "    <title>{0}</title>\n".format(title)

    if css_mode == 2:
        s += embed_style()
        s += "\n"
    elif css_mode == 1:
        s += "    <style>\n"
        s += get_css_from_file(indent_len=8)
        s += "    </style>\n"
    else:
        s += '    <link rel="stylesheet" href="../style.css" />\n'
        s += '    <link rel="stylesheet" href="style.css" />\n'

    s += "</head>\n"
    s += "<body>\n"
    return s


def html_tail():
    s = "</body>\n"
    s += "</html>\n"
    return s


def todo_file_html(file_name, last_modified):
    s = '<div class="fileheader" id="{}">\n'.format(as_link_name(file_name))
    s += '  <p class="filename"><a>{}</a></p>\n'.format(file_name)
    s += '  <p class="filetime">Modified {}</p>\n'.format(last_modified)
    s += "</div>\n"
    return s


def html_text(text):
    s = text.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace("\n", "<br />")
    return s


def todo_item_html(item, row):
    if item.is_flagged or item.is_elevated:
        add_class = " flagged"
    else:
        add_class = ""

    s = '<div class="item{0}{1}">\n'.format(row % 2, add_class)

    s += '<div class="itemtext">\n{0}\n</div>\n'.format(
        html_text(item.item_text)
    )

    s += "</div>\n"
    return s


def as_link_name(file_name):
    return (
        file_name.strip(" /\\")
        .replace(" ", "_")
        .replace("/", "-")
        .replace(".", "-")
    )


def contents_section(todo_files, any_flags, any_tags):
    s = '<div id="contents_section">\n'
    s += "<h2>Contents</h2>\n"

    s += "<h3>Sections</h3>\n"
    s += "<ul>\n"

    if any_flags:
        s += '<li><a href="#flagged_section">Flagged Items</a></li>\n'

    if any_tags:
        s += '<li><a href="#tags_section">Tagged Items</a></li>\n'

    s += '<li><a href="#main">Files with To-do Items</a></li>\n'

    s += "</ul>\n"

    s += "<h3>Files</h3>\n"
    s += "<ul>\n"

    for todo_file in todo_files:
        if todo_file.todo_items:
            s += '<li class="flink"><a href="#{0}">{1}</a></li>{2}'.format(
                as_link_name(todo_file.full_name), todo_file.full_name, "\n"
            )

    s += "</ul>\n"
    s += "</div>  <!--end contents_section -->\n"
    return s


def flagged_item_html(item, row):
    s = '<div class="flag{0}">\n'.format(row % 2)

    s += '<p class="flink"><a href="#{0}">{1}</a></p>\n'.format(
        as_link_name(item.source_file), item.source_file
    )

    s += '<div class="itemtext">\n{0}\n</div>\n'.format(
        html_text(item.item_text)
    )

    s += "</div>\n"
    return s


def flagged_items_html(items):
    if not items:
        return ""

    s = '<div id="flagged_section">\n'
    s += "<h2><a>Flagged Items</a></h2>\n"
    s += '<div id="flagged_items">\n'
    for item in items:
        s += item
    s += "</div>  <!--end flagged_items -->\n"
    s += "</div>  <!--end flagged_section -->\n"
    return s


def get_flagged_items():
    row = 0
    for todo_file in todo_files:
        for item in todo_file.todo_items:
            if item.is_flagged:
                row += 1
                flagged_items.append(flagged_item_html(item, row))


def tagged_item_html(item, row):
    s = '<div class="tag{0}">\n'.format(row % 2)

    s += '<p class="flink"><a href="#{0}">{1}</a></p>{2}'.format(
        as_link_name(item.source_file), item.source_file, "\n"
    )

    s += '<div class="itemtext">\n{0}\n</div>\n'.format(
        html_text(item.item_text)
    )

    s += "</div>\n"
    return s


def tags_section(todo_tags):
    if not todo_tags:
        return ""

    s = '<div id="tags_section">\n'
    s += "<h2><a>Tagged Items</a></h2>\n"
    s += '<div id="tagged_items">\n'

    for tag, items in sorted(todo_tags.items()):
        s += '<div class="tagheader">\n'
        s += "<p>Tag: <strong>{0}</strong></p>\n".format(tag)
        s += "</div>\n"

        for row, item in enumerate(items, start=1):
            s += tagged_item_html(item, row)

    s += "</div>  <!--end tagged_items -->\n"
    s += "</div>  <!--end tags_section -->\n"
    return s


def main_section(todo_files):
    s = '<div id="main">\n'
    s += "<h2><a>Files with To-do Items</a></h2>\n"
    for todo_file in todo_files:
        if todo_file.todo_items:
            s += todo_file_html(todo_file.full_name, todo_file.last_modified)
            s += '<div class="filecontent">\n'

            for row, item in enumerate(todo_file.todo_items, start=1):
                s += "{0}\n".format(todo_item_html(item, row))

            s += '<p class="toplink">'
            s += '(<a href="#contents_section">top</a>)</p>\n'

            s += "</div>  <!--end filecontent -->\n\n"
    s += "</div>  <!--end main -->\n"
    return s


def settings_section(by_mtime: bool):
    s = '<div id="settings_section">\n'

    s += "<p>Directories scanned:<br>\n"
    for dir in dirs_to_scan:
        s += "&nbsp;&nbsp;{}&nbsp;&nbsp;&nbsp;(recurse={})<br>\n".format(
            dir.dir_name, dir.do_recurse
        )
    s += "</p>\n"

    if dirs_to_exclude:
        s += "<p>Directories excluded:<br>\n"
        for dir in dirs_to_exclude:
            s += "&nbsp;&nbsp;{}<br>\n".format(dir)
        s += "</p>\n"

    if by_mtime:
        s += "<p>Sorted by file-modified time, most recent first.</p>\n"

    s += "</div>  <!--end settings_section -->\n"
    return s


def get_option_entries(opt_section, opt_content):
    result = []
    in_section = False
    for line in opt_content:
        s = line.strip()
        if s:
            if in_section:
                #  Handle new section w/o blank lines between.
                if s.startswith("["):
                    in_section = False
                #  Support whole-line comments identified by '#' (ignore them).
                elif not s.startswith("#"):
                    result.append(s)
            if s == opt_section:
                in_section = True
        else:
            in_section = False
    return result


def get_option_value(opt_section, opt_name, opt_content):
    opts = get_option_entries(opt_section, opt_content)
    for opt in opts:
        if opt.strip().startswith(opt_name):
            a = opt.split("=", 1)
            if len(a) == 2:
                return a[1].strip("'\"")
    return None


def getopt_output_filename(default_filename, opt_content):
    value = get_option_value("[output]", "filename", opt_content)
    if value is None:
        return default_filename
    else:
        return value


def opt_is_true(value, prompt):
    assert value is not None

    s = value.lower()

    if s == "ask":
        print("\n(Input requested per options file.)")
        s = input("{0} ".format(prompt))
        print(" ")

    #  The option setting can be values such as True or False, Yes or No,
    #  Y or N, 1 or 0. The values True, Yes, and 1 are considered true,
    #  though only the first character is checked (so, for example,
    #  'turtle' is also true).
    return s and (s[0].lower() in ("t", "y", "1"))


def getopt_by_mtime(by_mtime_default, opt_content):
    value = get_option_value("[output]", "by_modified_time_desc", opt_content)
    if value is None:
        return by_mtime_default
    else:
        return opt_is_true(
            value, "Sort by file-modified time in descending order (y/N)?"
        )


def getopt_do_text(default_do_text, opt_content):
    value = get_option_value("[output]", "do_text_file", opt_content)
    if value is None:
        return default_do_text
    else:
        return opt_is_true(value, "Create text file output (y/N)?")


def getopt_do_text_dt(default_do_text_dt, opt_content):
    value = get_option_value("[output]", "do_text_file_dt", opt_content)
    if value is None:
        return default_do_text_dt
    else:
        return opt_is_true(
            value, "Create text file output with date_time in file name (y/N)?"
        )


def getopt_no_html(default_no_html, opt_content):
    value = get_option_value("[output]", "no_html", opt_content)
    if value is None:
        return default_no_html
    else:
        return opt_is_true(value, "Skip creating HTML file output (y/N)?")


def getopt_title(default_title, opt_content):
    value = get_option_value("[output]", "title", opt_content)
    if value is None:
        return default_title
    else:
        return value


def getopt_filespecs(opt_content):
    entries = get_option_entries("[match]", opt_content)
    if entries:
        #  If the options file contains file specs then they override the
        #  defaults.
        specs = [entry.strip("'\" ") for entry in entries]
    else:
        specs = default_file_specs
    for spec in specs:
        file_specs.append(spec)


def getopt_dirs_to_scan(opt_content):
    entries = get_option_entries("[folders]", opt_content)
    if entries:
        for entry in entries:
            recurse = False
            s = entry.strip()
            if s.endswith("+"):
                recurse = True
                s = s.strip("+")
            s = s.strip("'\" ")
            dirs_to_scan.append(
                ScanProps(str(Path(s).expanduser().resolve()), recurse)
            )


def getopt_dirs_to_exclude(opt_content):
    entries = get_option_entries("[exclude]", opt_content)
    for entry in entries:
        s = entry.strip("'\" ")
        dirs_to_exclude.append(str(Path(s).expanduser().resolve()))


def get_output_filename(args_filename, date_time, desired_suffix):
    p = Path(args_filename).expanduser().resolve()

    if date_time is not None:
        p = Path(
            "{0}_{1}".format(
                p.with_suffix(""), date_time.strftime("%Y%m%d_%H%M%S")
            )
        )

    if p.suffix.lower() == desired_suffix:
        s = str(p)
    else:
        s = str(p.with_suffix(desired_suffix))

    if matches_filespec(Path(s).name):
        print(
            "\nWARNING: Output file name matches a specification "
            "for files to be scanned. Its contents will be "
            "included in subsequent scans, causing duplication."
        )
        print("   NAME: {0}\n".format(s))

    return s


def get_html_output(page_title: str, by_mtime: bool):
    s = "{0}\n".format(html_head(page_title))
    s += '<div id="wrapper">\n'
    s += '<div id="content">\n'
    s += "<h1>{0}</h1>\n".format(page_title)

    s += "{0}\n".format(
        contents_section(todo_files, bool(flagged_items), bool(item_tags))
    )

    s += "{0}\n".format(flagged_items_html(flagged_items))

    s += "{0}\n".format(tags_section(item_tags))

    s += "{0}\n".format(main_section(todo_files))

    s += "{0}\n".format(settings_section(by_mtime))

    s += '<div id="footer">\n'
    s += "Created {0} by {1}.\n".format(
        run_dt.strftime("%Y-%m-%d %H:%M"), app_title
    )

    s += "</div>\n\n"
    s += "</div>  <!--end content -->\n"
    s += "</div>  <!--end wrapper -->\n"
    s += html_tail()
    return s


def write_html_output(opts: AppOptions):
    out_file_name = get_output_filename(opts.output_file, None, ".html")
    print("\nWriting file [{0}].".format(out_file_name))
    with open(out_file_name, "w") as f:
        f.write(get_html_output(opts.page_title, opts.by_mtime))


def get_text_output():
    sep = "-" * 70
    text = "Gathered ToDo Items\n"
    for todo_file in todo_files:
        if todo_file.todo_items:
            s = sep + "\n"
            s += todo_file.full_name + "\n"
            s += "  ({0})\n\n".format(todo_file.last_modified)
            for item in todo_file.todo_items:
                s += item.item_text + "\n"
            s += "\n"
            text += s
    text += sep + "\n"
    text += "Created {0} by {1}.\n".format(
        run_dt.strftime("%Y-%m-%d %H:%M"), app_title
    )
    return text


def write_text_output(opt):
    if opt.do_text_dt:
        out_file_name = get_output_filename(opt.output_file, run_dt, ".txt")
    else:
        out_file_name = get_output_filename(opt.output_file, None, ".txt")

    print("\nWriting file [{0}].".format(out_file_name))

    with open(out_file_name, "w") as f:
        f.write(get_text_output())


def open_html_output(opt):
    if not (opt.no_browser or opt.no_html):
        url = "file://{0}".format(
            get_output_filename(opt.output_file, None, ".html")
        )
        webbrowser.open(url)


# ---------------------------------------------------------------------


def prune(text):
    if text is None:
        return ""
    s = text.replace("\t", " ")
    s = s.replace("\n", " ")
    s = s.replace(",", " ")
    s = s.replace(".", " ")
    s = s.replace("(", " ")
    s = s.replace(")", " ")
    s = s.strip()
    #  Remove any repeating spaces.
    while s.find("  ") >= 0:
        s = s.replace("  ", " ")
    return s


def get_item_tags():
    for todo_file in todo_files:
        for item in todo_file.todo_items:
            s = prune(item.item_text)
            #  Split into words (which might not really be words).
            wurdz = s.split(" ")
            for wurd in wurdz:
                if len(wurd) > 1 and wurd.startswith("#"):
                    if wurd in item_tags.keys():
                        item_tags[wurd].append(item)
                    else:
                        item_tags[wurd] = [item]


# ---------------------------------------------------------------------


def get_args(argv):
    ap = argparse.ArgumentParser(
        description="Read text files containing to-do markers and create a "
        "HTML report."
    )

    #  Note: Using the term 'folder' instead of 'directory' in argument
    #  descriptions.

    ap.add_argument(
        "folders",
        nargs="*",
        action="store",
        help="Folder(s) to scan. Multiple folders can be specified.",
    )

    ap.add_argument(
        "-f",
        "--options-file",
        dest="optfile",
        action="store",
        help="Name of options file.",
    )

    ap.add_argument(
        "-r",
        "--recurse",
        dest="recurse",
        action="store_true",
        help="Recurse sub-folders. Applies to all folders specified. "
        "Use an options file to specify the recurse option for "
        "individual folders.",
    )

    ap.add_argument(
        "-m",
        "--mtime-desc",
        dest="by_mtime",
        action="store_true",
        help="Sort files by last-modified time in descending order.",
    )

    ap.add_argument(
        "-o",
        "--output-file",
        dest="output_file",
        action="store",
        help="Name of output file. The '.html' extension will be "
        "added if not specified.",
    )

    ap.add_argument(
        "-t",
        "--text-file",
        dest="do_text",
        action="store_true",
        help="Create a text file output.",
    )

    ap.add_argument(
        "-d",
        "--text-file-dt",
        dest="do_text_dt",
        action="store_true",
        help="Create a text file output with the creation date_time in the "
        "file name.",
    )

    ap.add_argument(
        "-n",
        "--no-html",
        dest="no_html",
        action="store_true",
        help="Do not create the HTML file output. Use with -t to only create "
        "a text file output.",
    )

    ap.add_argument(
        "-x",
        "--exclude-path",
        dest="exclude_path",
        default="",
        action="store",
        help="Path(s) to exclude from scan. Separate multiple paths using "
        "semicolons.",
    )
    # TODO: Perhaps expand on the help message.

    ap.add_argument(
        "-p",
        "--page-title",
        dest="page_title",
        default="ToDo Items",
        action="store",
        help="Title for HTML page (will show in browser tab).",
    )

    ap.add_argument(
        "-q",
        "--no-browser",
        dest="no_browser",
        action="store_true",
        help="Do not try to open the output file in the web browser.",
    )

    return ap.parse_args(argv[1:])


def get_options(argv):
    args_parsed = get_args(argv)

    if args_parsed.optfile is None:
        opt_lines = []
    else:
        p = Path(args_parsed.optfile).expanduser().resolve()
        if not p.exists():
            raise SystemExit("Options file not found: {0}".format(p))
        with open(p, "r") as f:
            opt_lines = f.readlines()

    #  Only check the options file, and potentially use the default value, if
    #  the output file name was not specified as a command line argument.
    if args_parsed.output_file is None:
        args_parsed.output_file = getopt_output_filename(
            default_output_file, opt_lines
        )

    for folder in args_parsed.folders:
        folder = str(Path(folder).expanduser().resolve())
        print("Folder {0}".format(folder))
        if not Path(folder).exists():
            raise SystemExit("Path not found: " + folder)
        dirs_to_scan.append(ScanProps(folder, args_parsed.recurse))

    getopt_dirs_to_scan(opt_lines)

    #  If no directories were specified in the arguments or options file
    #  then only scan the current directory.
    if not dirs_to_scan:
        dirs_to_scan.append(ScanProps(str(Path.cwd()), False))

    for excluded in args_parsed.exclude_path.strip("'\"").split(";"):
        if excluded:
            dirs_to_exclude.append(str(Path(excluded).expanduser().resolve()))

    getopt_dirs_to_exclude(opt_lines)

    getopt_filespecs(opt_lines)

    result = AppOptions(
        args_parsed.folders,
        args_parsed.optfile,
        args_parsed.recurse,
        getopt_by_mtime(args_parsed.by_mtime, opt_lines),
        args_parsed.output_file,
        getopt_do_text(args_parsed.do_text, opt_lines),
        getopt_do_text_dt(args_parsed.do_text_dt, opt_lines),
        getopt_no_html(args_parsed.no_html, opt_lines),
        getopt_title(args_parsed.page_title, opt_lines),
        args_parsed.no_browser,
    )

    return result


def main(argv):
    print("Running {0}.".format(app_title))

    opts = get_options(argv)

    assert opts.output_file is not None

    if debug_stop_after_args:
        raise SystemExit("STOPPED")

    for dir in dirs_to_scan:
        print("Scanning folder [{0}]".format(dir.dir_name))
        get_matching_files(dir.dir_name, dir.do_recurse)

    if opts.by_mtime:
        #  The last_modified field is the default for sort.
        file_list.sort()
        file_list.reverse()
    else:
        file_list.sort(key=lambda item: item.full_name.lower())

    for file_info in file_list:
        print("Reading file [{0}]".format(file_info.full_name))
        items = get_todo_items(file_info.full_name)
        todo_files.append(
            TodoFile(file_info.last_modified, file_info.full_name, items)
        )

    get_flagged_items()

    get_item_tags()

    if not opts.no_html:
        write_html_output(opts)

    if opts.do_text or opts.do_text_dt:
        write_text_output(opts)

    if error_messages:
        print("\nThere were errors!")
        for msg in error_messages:
            print(msg)
        print("")

    open_html_output(opts)

    print("Done ({0}).".format(app_title))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
