#!/usr/bin/env python3

# ---------------------------------------------------------------------
# todolister.py
#
# 
#
# 2021-09-08
# ---------------------------------------------------------------------

import argparse
import re
from collections import namedtuple
from datetime import datetime
from pathlib import Path


ScanProps = namedtuple("ScanProps", "dir_name, do_recurse")

FileInfo = namedtuple("FileInfo", "last_modified, full_name")

TodoItem = namedtuple(
    "TodoItem", "is_flagged, is_elevated, item_text, source_file"
)

TodoFile = namedtuple("TodoFile", "last_modified, full_name, todo_items")

AppArgs = namedtuple(
    "AppArgs",
    "folders, optfile, recurse, mtime, output_file, "
    + "do_text, do_text_dt, nohtml, page_title",
)

app_version = "210908.1"

pub_version = "1.0.dev1"

css_mode = 2
# 0 = link to external css file (use for trying css changes).
# 1 = embed from external css file (use to get css to update embed_style).
# 2 = embed from function embed_style.

debug_stop_after_args = False

default_file_specs = [
    "^notes.*.txt$",
    ".*notes.txt$",
    "^todo.*.txt$",
    ".*-todo.txt$",
    "^Context-.*.txt$",
]

css_file_name = str(Path.cwd() / "style.css")

default_output_file = str(Path.cwd() / "from-todolister.html")


def matches_filespec(file_name):
    for spec in file_specs:
        if re.search(spec.lower(), file_name.lower()):
            return True
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
            for line in lines:
                stripped = line.strip()
                if in_todo:
                    if len(stripped) == 0:
                        in_todo = False
                        if len(todo_text) > 0:
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
                        todo_text += line
                else:
                    if stripped.startswith("[ ]"):
                        in_todo = True
                        is_flagged = stripped.startswith("[ ]*")
                        is_elevated = stripped.startswith("[ ]+")
                        todo_text += line

            # Save last item, in case there were no blank lines at the
            # end of the file.
            if len(todo_text) > 0:
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
            if len(line.strip()) > 0:
                css += "{0}{1}".format(indent, line)
    css += "\n"
    return css


def embed_style():
    # Changes made in external css file pasted here from html output
    # after running with css_mode = 1.
    return (
        """
    <style>
        h1 {color: steelblue;}
        h2 {color: slategrey;}
        #wrapper {padding: 10px;}
        #content {max-width: 960px;}
        #footer {
            border-top: 2px solid #999;
            font-family: monospace;
            font-size: medium;
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
        pre {
            margin: 0px;
            font-family: Consolas, monospace;
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
    </style>"""
    )


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
        s += '    <link rel="stylesheet" href="style.css" />\n'

    s += "</head>\n"
    s += "<body>\n"
    return s


def html_tail():
    s = "</body>\n"
    s += "</html>\n"
    return s


def todo_file_html(file_name, last_modified):
    s = '<div class="fileheader">\n'
    s += '  <p class="filename"><a name="{0}">{1}</a></p>\n'.format(
        as_link_name(file_name), file_name
    )
    s += '  <p class="filetime">Modified {0}</p>\n'.format(last_modified)
    s += "</div>\n"
    return s


def html_text(text):
    s = text.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s


def todo_item_html(item, row):
    if item.is_flagged or item.is_elevated:
        add_class = " flagged"
    else:
        add_class = ""
    s = '<div class="item{0}{1}">\n'.format(row % 2, add_class)
    s += "<pre>\n{0}\n</pre>\n".format(html_text(item.item_text))
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

    s += "<h3>Sections</h2>\n"
    s += "<ul>\n"
    if any_flags:
        s += '<li><a href="#FlaggedItems">Flagged Items</a></li>\n'
    if any_tags:
        s += '<li><a href="#TaggedItems">Tagged Items</a></li>\n'
    s += '<li><a href="#Main">Files with To-do Items</a></li>\n'
    s += "</ul>\n"

    s += "<h3>Files</h2>\n"
    s += "<ul>\n"
    for todo_file in todo_files:
        if len(todo_file.todo_items) > 0:
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
    s += "<pre>\n{0}\n</pre>\n".format(html_text(item.item_text))
    s += "</div>\n"
    return s


def flagged_items_html(items):
    if len(items) == 0:
        return ""
    s = '<div id="flagged_section">\n'
    s += '<h2><a name="FlaggedItems">Flagged Items</a></h2>\n'
    s += '<div id="flagged_items">\n'
    for item in items:
        s += item
    s += "</div>  <!--end flagged_items -->\n"
    s += "</div>  <!--end flagged_section -->\n"
    return s


def get_flagged_items(todo_files):
    flagged_items = []
    row = 0
    for todo_file in todo_files:
        if len(todo_file.todo_items) > 0:
            for item in todo_file.todo_items:
                if item.is_flagged:
                    row += 1
                    flagged_items.append(flagged_item_html(item, row))
    return flagged_items


def tagged_item_html(item, row):
    s = '<div class="tag{0}">\n'.format(row % 2)
    s += '<p class="flink"><a href="#{0}">{1}</a></p>{2}'.format(
        as_link_name(item.source_file), item.source_file, "\n"
    )
    s += "<pre>\n{0}\n</pre>\n".format(html_text(item.item_text))
    s += "</div>\n"
    return s


def tags_section(todo_tags):
    s = '<div id="tags_section">\n'
    s += '<h2><a name="TaggedItems">Tagged Items</a></h2>\n'
    s += '<div id="tagged_items">\n'

    for tag, items in sorted(todo_tags.items()):
        s += '<div class="tagheader">\n'
        s += "<p>Tag: <strong>{0}</strong></p>\n".format(tag)
        s += "</div>\n"
        row = 0
        for item in items:
            row += 1
            s += tagged_item_html(item, row)

    s += "</div>  <!--end tagged_items -->\n"
    s += "</div>  <!--end tags_section -->\n"
    return s


def main_section(todo_files):
    s = '<div id="main">\n'
    s += '<h2><a name="Main">Files with To-do Items</a></h2>\n'
    for todo_file in todo_files:
        if len(todo_file.todo_items) > 0:
            s += todo_file_html(todo_file.full_name, todo_file.last_modified)
            s += '<div class="filecontent">\n'
            row = 0
            for item in todo_file.todo_items:
                row += 1
                s += "{0}\n".format(todo_item_html(item, row))
            s += '<p class="toplink">(<a href="#top">top</a>)</p>\n'
            s += "</div>  <!--end filecontent -->\n\n"
    s += "</div>  <!--end main -->\n"
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
                if s.startswith("["):
                    in_section = False
                # Support whole-line comments identified by '#' (ignore them).
                elif not s.startswith("#"):
                    result.append(s)
            if s == opt_section:
                in_section = True
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
    return (len(s) > 0) and (s[0].lower() in ("t", "y", "1"))


def getopt_mtime(default_mtime, opt_content):
    value = get_option_value("[output]", "by_modified_time_desc", opt_content)
    if value is None:
        return default_mtime
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


def getopt_filespecs(default_specs, opt_content):
    entries = get_option_entries("[match]", opt_content)
    if len(entries) == 0:
        return default_specs
    else:
        return [entry.strip("'\" ") for entry in entries]


def getopt_dirs_to_scan(default_dirs, opt_content):
    entries = get_option_entries("[folders]", opt_content)
    if len(entries) == 0:
        return default_dirs
    else:
        dirs = []
        for entry in entries:
            recurse = False
            s = entry.strip()
            if s.endswith("+"):
                recurse = True
                s = s.strip("+")
            s = s.strip("'\" ")
            dirs.append(
                ScanProps(str(Path(s).expanduser().resolve()), recurse)
            )
        return dirs


def getopt_dirs_to_exclude(default_dirs, opt_content):
    entries = get_option_entries("[exclude]", opt_content)
    if len(entries) == 0:
        return default_dirs
    else:
        dirs = []
        for entry in entries:
            s = entry.strip("'\" ")
            dirs.append(str(Path(s).expanduser().resolve()))
        return dirs


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
            + "for files to be scanned. Its contents will be "
            + "included in subsequent scans, causing duplication."
        )
        print("   NAME: {0}\n".format(s))

    return s


def write_html_output(todo_files, flagged_items, todo_tags):
    out_file_name = get_output_filename(args.output_file, None, ".html")
    print("Writing file [{0}].".format(out_file_name))
    with open(out_file_name, "w") as f:
        f.write("{0}\n".format(html_head(args.page_title)))
        f.write('<div id="wrapper">\n')
        f.write('<div id="content">\n')

        f.write('<h1><a name="top">{0}</a></h1>\n'.format(args.page_title))

        f.write("{0}\n".format(
            contents_section(
                todo_files, (len(flagged_items) > 0), (len(todo_tags) > 0)
            )
        ))

        f.write("{0}\n".format(flagged_items_html(flagged_items)))

        f.write("{0}\n".format(tags_section(todo_tags)))

        f.write("{0}\n".format(main_section(todo_files)))

        f.write('<div id="footer">\n')
        f.write(
            "Created {0} by todolister.py (version {1}).\n".format(
                datetime.now().strftime("%Y-%m-%d %H:%M"), app_version
            )
        )
        f.write("</div>\n\n")
        f.write("</div>  <!--end content -->\n")
        f.write("</div>  <!--end wrapper -->\n")
        f.write(html_tail())


def write_text_output(todo_files, include_datetime):
    sep = "-" * 70

    dt = datetime.now()

    if include_datetime:
        out_file_name = get_output_filename(args.output_file, dt, ".txt")
    else:
        out_file_name = get_output_filename(args.output_file, None, ".txt")

    print("Writing file [{0}].".format(out_file_name))

    with open(out_file_name, "w") as f:
        f.write("Gathered ToDo Items\n")
        for todo_file in todo_files:
            if len(todo_file.todo_items) > 0:
                s = sep + "\n"
                s += todo_file.full_name + "\n"
                s += "  ({0})\n\n".format(todo_file.last_modified)
                for item in todo_file.todo_items:
                    s += item.item_text + "\n"
                s += "\n"
                f.write(s)
        f.write(sep + "\n")
        s = "Created {0} by todolister.py (version {1}).\n".format(
            dt.strftime("%Y-%m-%d %H:%M"), app_version
        )
        f.write(s)


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
    # Remove any repeating spaces.
    while s.find("  ") >= 0:
        s = s.replace("  ", " ")
    return s


def get_item_tags(todo_files):
    tags = {}
    for todo_file in todo_files:
        if len(todo_file.todo_items) > 0:
            for item in todo_file.todo_items:
                s = prune(item.item_text)
                # Split into words (which might not really be words).
                wurdz = s.split(" ")
                for wurd in wurdz:
                    if len(wurd) > 1 and wurd.startswith("#"):
                        if wurd in tags.keys():
                            tags[wurd].append(item)
                        else:
                            tags[wurd] = [item]
    return tags


# ---------------------------------------------------------------------


def main():

    print("Running todolister.py (version {0}).".format(app_version))

    global error_messages
    error_messages = []

    #  region -- define arguments

    #  Note: Using the term 'folder' instead of 'directory' in argument
    #  descriptions.

    ap = argparse.ArgumentParser(
        description="Read text files containing to-do markers and create a "
        + "HTML report."
    )

    ap.add_argument(
        "folders",
        nargs="*",
        default=[str(Path.cwd())],
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
        + "Use an options file to specify the recurse option for "
        + "individual folders.",
    )

    ap.add_argument(
        "-m",
        "--mtime-desc",
        dest="mtime",
        action="store_true",
        help="Sort files by last-modified time in descending order.",
    )

    ap.add_argument(
        "-o",
        "--output-file",
        dest="output_file",
        action="store",
        help="Name of output file. The '.html' extension will be "
        + "added if not specified.",
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
        + "file name.",
    )

    ap.add_argument(
        "-n",
        "--no-html",
        dest="nohtml",
        action="store_true",
        help="Do not create the HTML file output. Use with -t to only create "
        + "a text file output.",
    )

    ap.add_argument(
        "-x",
        "--exclude-path",
        dest="exclude_path",
        default="",
        action="store",
        help="Path(s) to exclude from scan. Separate multiple paths using "
        + "semicolons.",
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

    #  endregion

    args_parsed = ap.parse_args()

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

    #  Put application arguments into a named tuple so they are immutable
    #  from this point.
    global args
    args = AppArgs(
        args_parsed.folders,
        args_parsed.optfile,
        args_parsed.recurse,
        getopt_mtime(args_parsed.mtime, opt_lines),
        args_parsed.output_file,
        getopt_do_text(args_parsed.do_text, opt_lines),
        getopt_do_text_dt(args_parsed.do_text_dt, opt_lines),
        getopt_no_html(args_parsed.nohtml, opt_lines),
        getopt_title(args_parsed.page_title, opt_lines),
    )

    dirs_to_scan = []
    for folder in args.folders:
        folder = str(Path(folder).expanduser().resolve())
        print("Folder {0}".format(folder))
        if not Path(folder).exists():
            raise SystemExit("Path not found: " + folder)
        dirs_to_scan.append(ScanProps(folder, args.recurse))

    global dirs_to_exclude
    dirs_to_exclude = []
    for excluded in args_parsed.exclude_path.strip("'\"").split(";"):
        if len(excluded) > 0:
            dirs_to_exclude.append(str(Path(excluded).expanduser().resolve()))

    dirs_to_exclude = getopt_dirs_to_exclude(dirs_to_exclude, opt_lines)

    global file_specs
    file_specs = getopt_filespecs(default_file_specs, opt_lines)

    dirs_to_scan = getopt_dirs_to_scan(dirs_to_scan, opt_lines)

    assert args.output_file is not None

    if debug_stop_after_args:
        raise SystemExit("STOPPED")

    # ---------------------------------------------------------------------

    global file_list
    file_list = []

    for dir in dirs_to_scan:
        print("Scanning folder [{0}]".format(dir.dir_name))
        get_matching_files(dir.dir_name, dir.do_recurse)

    if args.mtime:
        # The last_modified field is the default for sort.
        file_list.sort()
        file_list.reverse()
    else:
        file_list.sort(key=lambda item: item.full_name.lower())

    todo_files = []

    for file_info in file_list:
        print("Reading file [{0}]".format(file_info.full_name))
        items = get_todo_items(file_info.full_name)
        todo_files.append(
            TodoFile(file_info.last_modified, file_info.full_name, items)
        )

    flagged_items = get_flagged_items(todo_files)

    item_tags = get_item_tags(todo_files)

    if not args.nohtml:
        write_html_output(todo_files, flagged_items, item_tags)

    if args.do_text or args.do_text_dt:
        write_text_output(todo_files, args.do_text_dt)

    if 0 < len(error_messages):
        print("\nThere were errors!")
        for msg in error_messages:
            print(msg)
        print("")

    print("Done (todolister.py - version {0}).".format(app_version))


if __name__ == "__main__":
    main()
