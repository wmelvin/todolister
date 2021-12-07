# todolister #

The **todolister.py** command-line tool scans text files and generates a HTML report listing found to-do items.

Square brackets with a space in between at the beginning of a line indicate an open to-do item.

```
[ ] A to-do item.
[ ]* A flagged to-do item.
[ ]+ An elevated to-do item.
```

Only **open items** (a space between the brackets) are listed. This is the convention I use for closing my to-do items:

```
[x] Completed.
    (maybe with a note as to when)

[n] Not going to do it.
    (probably with a note as to why)

[>] Moved to another list, but keep the history in the current file.

[.] Stop. Probably something from an old list. 
    Maybe I did it. Maybe I didn't.
    Don't want to be reminded.
```

The closed items above are ignored by *todolister*. They are included here as an example of how my lists are used. Of course, completed items can simply be deleted if you don't want the history.


## Options File ##

### Sections ###

**Output**

The `[output]` section can contain the following settings:

`filename=` Name of the output file. The '.html' extension will be added if not specified. If text output is enabled the same name, but with a *.txt* extension, is used. Same as the -o, --output-file, command-line option.

`by_modified_time_desc=` (Y/N) "Y" = Order the files by modified time, in descending order, in the report.

`do_text_file=` (Y/N) "Y" = Produce a text (.txt) version of the report.

`do_text_file_dt=` (Y/N) "Y" = Produce a text (.txt) version of the report that includes a *date_time* tag in the file name. This can be used to keep a history of changes that can be reviewed using a file comparison tool.

`no_html=` (Y/N) "Y" = do not produce the HTML file. Use to only produce the text file.

`title=` Title to use in the generated HTML file.

The following *yes/no* options can be configured to prompt for user input by entering "ask" for the setting (not case-sensitive):
- `by_modified_time_desc=Ask`
- `do_text_file=ask`
- `do_text_file_dt=ask`
- `no_html=ask`

**Lists**

The `[match]` section contains a list file name matching patterns, one per line, for selecting which files to scan for to-do items.

The `[folders]` section contains a list of one or more folder paths, one per line, to scan for files that match the to-do file patterns.

The `[exclude]`  section contains a list of one or more sub-folder paths, one per line, to exclude while scanning the given list of folders.


## Command-Line Usage ##

```
usage: todolister.py [-h] [-f OPTFILE] [-r] [-m] [-o OUTPUT_FILE] [-t] [-d]
                     [-n] [-x EXCLUDE_PATH] [-p PAGE_TITLE] [-q]
                     [folders [folders ...]]

Read text files containing to-do markers and create a HTML report.

positional arguments:
  folders               Folder(s) to scan. Multiple folders can be specified.

optional arguments:
  -h, --help            show this help message and exit
  -f OPTFILE, --options-file OPTFILE
                        Name of options file.
  -r, --recurse         Recurse sub-folders. Applies to all folders specified.
                        Use an options file to specify the recurse option for
                        individual folders.
  -m, --mtime-desc      Sort files by last-modified time in descending order.
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Name of output file. The '.html' extension will be
                        added if not specified.
  -t, --text-file       Create a text file output.
  -d, --text-file-dt    Create a text file output with the creation date_time
                        in the file name.
  -n, --no-html         Do not create the HTML file output. Use with -t to
                        only create a text file output.
  -x EXCLUDE_PATH, --exclude-path EXCLUDE_PATH
                        Path(s) to exclude from scan. Separate multiple paths
                        using semicolons.
  -p PAGE_TITLE, --page-title PAGE_TITLE
                        Title for HTML page (will show in browser tab).
  -q, --no-browser      Do not try to open the output file in the web browser.
```

## History ##

In past jobs, I have been the sole developer supporting a team whose function is not software development. There was no shared issue tracking system so I had to maintain my own lists. I have used spreadsheets and databases as centralized task trackers. However, I found that it worked better for me, in those roles, to track to-do items in text files that were located with each project.

There were many small projects and sub-projects to support both long-term (core systems) and short-term (support requests, research, prototypes, etc.) work. Having the to-do list, and the history of completed tasks, in the same location as other project artifacts worked well in that context. However, there was still the need to see an aggregate view of pending tasks.

In my previous job, I wrote a PowerShell script to generate a report listing to-do items from across the set of projects I worked on. That script belongs to the company I was working for (you know, that work-for-hire copyright thing). 

I wanted that same functionality for my personal projects, and I wanted more experience programming with Python, so I wrote *todolister.py*.
