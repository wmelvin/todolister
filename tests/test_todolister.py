"""
Tests for todolister.py.

TDD was not used in creating todolister.py.  These tests were added after
there was a working version.  Most, if not all, of these tests are functional
tests rather than unit tests.

"""

import textwrap
from importlib import reload
from pathlib import Path

import html5lib
import pytest

from todolister import todolister


def write_notes_txt(dir_path):
    p = dir_path / "notes.txt"
    p.write_text(
        textwrap.dedent(
            """
            [ ] notes.txt
                One more line

            [ ] An item with a #hashtag.

            #extrahash should not show up

            After to-do.
            """
        )
    )
    assert p.exists()


def write_notes_md(dir_path):
    p = dir_path / "notes.md"
    p.write_text(
        textwrap.dedent(
            """
            [ ] notes.md
            """
        )
    )
    assert p.exists()


def write_subdir_notes_txt(dir_path):
    d = dir_path / "SubDir"
    d.mkdir()
    p = d / "notes.txt"
    p.write_text(
        textwrap.dedent(
            """
            [ ] notes.txt in SubDir
                One more line

            After to-do.
            """
        )
    )
    assert p.exists()


def write_notthis_txt(dir_path):
    p = dir_path / "notthis.txt"
    p.write_text(
        textwrap.dedent(
            """

            [ ] notthis.txt
            This file should be skipped.

            """
        )
    )
    assert p.exists()


def write_notthisdir_notes_txt(dir_path):
    d = dir_path / "NotThisDir"
    d.mkdir()
    p = dir_path / "NotThisDir" / "notes.txt"
    p.write_text(
        textwrap.dedent(
            """

            [ ]* As test for --exclude-path, notes.txt in NotThisDir
                 should not be included.

            """
        )
    )
    assert p.exists()


def write_notes_uc_txt(dir_path):
    p = dir_path / "Notes-UC.txt"
    p.write_text(
        textwrap.dedent(
            """
            [ ] Notes-UC.txt
                One more line

            [ ] A different hash #tag.

            [ ] One in parens (#tag).

            [ ] Just some hash #.

            After to-do.
            """
        )
    )
    assert p.exists()


def write_somenotes_txt(dir_path):
    p = dir_path / "somenotes.txt"
    p.write_text(
        textwrap.dedent(
            """
            [ ] somenotes.txt
                "notes" at the end of file name.

            After to-do.
            """
        )
    )
    assert p.exists()


def write_thisis_notodo_txt(dir_path):
    p = dir_path / "thisis-notodo.txt"
    p.write_text(
        textwrap.dedent(
            """
            [ ] thisis-notodo.txt
                This should be skipped if requiring that the suffix
                be "-todo" (dash required).

            After to-do.
            """
        )
    )
    assert p.exists()


def write_thisis_todo_txt(dir_path):
    p = dir_path / "thisis-todo.txt"
    p.write_text(
        textwrap.dedent(
            """
            [ ] thisis-todo.txt
                This should be included if requiring that the suffix
                be "-todo" (dash required).

            After to-do.

            [ ] Another to-do.

            [ ] And another.
            |
            Connected line.

            [ ] An ampersand &, a greater-than >, and a less-than <.
            """
        )
    )
    assert p.exists()


def write_todo_lc_txt(dir_path):
    p = dir_path / "todo-lc.txt"
    p.write_text(
        textwrap.dedent(
            """
            [ ] todo-lc.txt
                One more line

            After to-do.
            """
        )
    )
    assert p.exists()


def write_todo_uc_txt(dir_path):
    p = dir_path / "ToDo-UC.txt"
    p.write_text(
        textwrap.dedent(
            """
            [ ] ToDo-UC.txt
                One more line

            [ ] A #hashtag in the middle.

            [ ] #hashtag at the start.

            [ ] A #hashtag, in the middle, with a comma after.

            After to-do.
            """
        )
    )
    assert p.exists()


def write_todo_txt(dir_path):
    p = dir_path / "todo.txt"
    p.write_text(
        textwrap.dedent(
            """
            [ ] todo.txt
                One more line

            After to-do.

            [ ]* A flagged item.

            [ ]+ An elevated item (should be bold).

            [x] A done item should not be listed.

            That's all.
            """
        )
    )
    assert p.exists()


def write_todo_md(dir_path):
    p = dir_path / "todo.md"
    p.write_text(
        textwrap.dedent(
            """
            [ ] todo.md - Markdown file.
                One more line.

            After to-do.

            [ ]* A flagged item.

            [ ]+ An elevated item (should be bold).

            [x] A done item should not be listed.

            That's all.
            """
        )
    )
    assert p.exists()


def write_wonotest_txt(dir_path):
    p = dir_path / "wonotest.txt"
    p.write_text(
        textwrap.dedent(
            """
            [ ] wonotest.txt
                "notes" in the middle of the file name.

            After to-do.
            """
        )
    )
    assert p.exists()


@pytest.fixture(scope="module")
def todo_files_dir(tmp_path_factory):
    """
    Makes a temporary directory and populates it with test files.
    Returns the pathlib.Path object for that directory.

    Also creates the directory 'last_test_output_for_review' in
    the project source directory if it does not already exist.
    """

    out_path = Path.cwd() / "last_test_output_for_review"
    if not out_path.exists():
        out_path.mkdir()

    p = tmp_path_factory.mktemp("testdata")
    write_notes_txt(p)
    write_notes_md(p)
    write_notthis_txt(p)
    write_notthisdir_notes_txt(p)
    write_subdir_notes_txt(p)
    write_notes_uc_txt(p)
    write_somenotes_txt(p)
    write_thisis_notodo_txt(p)
    write_thisis_todo_txt(p)
    write_todo_lc_txt(p)
    write_todo_uc_txt(p)
    write_todo_txt(p)
    write_todo_md(p)
    write_wonotest_txt(p)
    return p


def test_runs_and_fills_lists(todo_files_dir):
    reload(todolister)
    assert len(todolister.file_list) == 0

    d = todo_files_dir
    excl_dir = str(d / "NotThisDir")

    args = [
        str(d),
        "--recurse",
        "-x",
        excl_dir,
        "--page-title",
        "test_runs_and_fills_lists",
        "--no-browser",
        "--output-file",
        "./last_test_output_for_review/from-test_runs_and_fills_lists",
    ]

    result = todolister.main(args)
    assert result == 0

    assert len(todolister.file_specs) > 0
    assert len(todolister.file_specs) == len(todolister.default_file_specs)
    assert len(todolister.dirs_to_scan) == 1
    expected_n_files = 10
    assert len(todolister.file_list) == expected_n_files
    assert len(todolister.todo_files) == expected_n_files
    assert len(todolister.flagged_items) > 0
    assert len(todolister.item_tags) > 0


def test_no_recurse(todo_files_dir):
    reload(todolister)
    assert len(todolister.file_list) == 0
    d = todo_files_dir
    args = [
        str(d),
        "--page-title",
        "test_no_recurse",
        "--no-browser",
        "--output-file",
        "./last_test_output_for_review/from-test_no_recurse",
    ]
    result = todolister.main(args)
    assert result == 0
    n_files_not_in_subdir = 9
    assert len(todolister.file_list) == n_files_not_in_subdir


def test_html_output_is_parsable(todo_files_dir):
    reload(todolister)
    assert len(todolister.file_list) == 0
    args = [
        str(todo_files_dir),
        "--no-browser",
        "--page-title",
        "test_html_output_is_parsable",
        "--output-file",
        "./last_test_output_for_review/from-test_html_output_is_parsable",
    ]
    result = todolister.main(args)
    assert result == 0
    html = todolister.get_html_output("TEST", False)
    parser = html5lib.HTMLParser(strict=True)
    document = parser.parse(html)
    check = document.findall(".//*[@id='main']")
    assert len(check) == 1


def test_file_permission_error(tmp_path):
    reload(todolister)
    assert len(todolister.file_list) == 0

    d = tmp_path / "testerr"
    d.mkdir()
    #  Create a test file.
    p = d / "notes.txt"
    p.write_text(
        textwrap.dedent(
            """
            [ ] This notes.txt should have its read permission removed
                to cause an exception.
            """
        )
    )
    assert p.exists()
    #  Remove read permission.
    p.chmod(0o220)

    #  Run test.
    args = [
        str(d),
        "--no-browser",
        "--page-title",
        "test_file_permission_error",
        "--output-file",
        "./last_test_output_for_review/from-test_file_permission_error",
    ]
    result = todolister.main(args)
    assert result == 0

    assert len(todolister.error_messages) > 0

    html = todolister.get_html_output("test_file_permission_error", False)
    assert "ERROR (PermissionError):" in html


def get_pre_text(element, find_id):
    """
    Use XPath expressions to get text from the <pre> tag elements inside
    an element, such as a <div>, with the given id.
    """
    ns = "{http://www.w3.org/1999/xhtml}"
    pre_qry = f".//*{ns}pre"
    result = []
    a = element.find(f'.//*[@id="{find_id}"]')
    if a is not None:
        b = a.findall(pre_qry)
        if b is not None:
            for e in b:
                result.append(e.text)
    return result


def get_itemtext_elements(element, find_id):
    """
    Use XPath expressions to get text from the <div class="itemtext">
    elements inside an element, such as a <div>, with the given id.
    """
    qry = './/*[@class="itemtext"]'
    result = []
    a = element.find(f'.//*[@id="{find_id}"]')
    if a is not None:
        b = a.findall(qry)
        if b is not None:
            for e in b:
                result.append(e.text)
    return result


def test_html_details(tmp_path):
    reload(todolister)
    assert len(todolister.file_list) == 0

    test_dir = tmp_path / "testdata2"
    test_dir.mkdir()
    #  Create a test file.
    test_file = test_dir / "notes.txt"
    test_file.write_text(
        textwrap.dedent(
            """
            [ ] Item from notes.txt in testdata2.
                One more line
                And another line

            [ ]* A flagged item.

            [ ]* Another flagged item.

            [ ] An item with a #hashtag.

            [ ] Another item with the same #hashtag.

            Text after to-do (should not be shown).

            #extrahash (should not be shown)
            """
        )
    )
    assert test_file.exists()
    #  Run test.
    args = [
        str(test_dir),
        "--no-browser",
        "--page-title",
        "test_html_details",
        "--output-file",
        "./last_test_output_for_review/from-test_html_details",
    ]
    result = todolister.main(args)
    assert result == 0

    html = todolister.get_html_output("TEST", False)

    doc = html5lib.parse(html)

    flagged_items = get_itemtext_elements(doc, "flagged_items")
    assert len(flagged_items) == 2

    tagged_items = get_itemtext_elements(doc, "tagged_items")
    assert len(tagged_items) == 2

    main_items = get_itemtext_elements(doc, "main")
    assert len(main_items) == 5

    assert "(should not be shown)" not in html


def test_creates_text_output(tmp_path):
    reload(todolister)
    assert len(todolister.file_list) == 0

    test_dir = tmp_path / "testdata3"
    test_dir.mkdir()
    #  Create a test file.
    test_file = test_dir / "notes.txt"
    test_file.write_text(
        textwrap.dedent(
            """
            [ ] Item from notes.txt in testdata3.
            """
        )
    )
    assert test_file.exists()

    wo_suffix = "./last_test_output_for_review/from-test_creates_text_output"

    #  Run test.
    args = [
        str(test_dir),
        "--no-browser",
        "--page-title",
        "test_creates_text_output",
        "--output-file",
        wo_suffix,
        "-t",
    ]
    result = todolister.main(args)
    assert result == 0

    assert Path(wo_suffix).with_suffix(".html").exists()
    assert Path(wo_suffix).with_suffix(".txt").exists()


def test_scenario(tmp_path):
    reload(todolister)
    assert len(todolister.file_list) == 0

    #  Create a test directory tree.
    test_home = tmp_path / "test" / "home"
    test_home.mkdir(parents=True)

    doc_dir = test_home / "Documents"
    doc_dir.mkdir()

    prj_dir = test_home / "Projects"
    prj_dir.mkdir()

    prj_dir_a = prj_dir / "Project_A"
    prj_dir_a.mkdir()

    prj_dir_b = prj_dir / "Project_B"
    prj_dir_b.mkdir()

    hold_dir = prj_dir / "Hold"
    prj_dir_c = hold_dir / "Project_C"
    prj_dir_c.mkdir(parents=True)

    #  Write the temporary test_home path to a local file to make
    #  it easy to find for manual review while the temporary
    #  directory still exists.
    dev_out_dir = Path.cwd() / "output_t"
    if dev_out_dir.exists():
        (dev_out_dir / "test_tmp_path.txt").write_text(str(test_home))

    #  Create test files.
    todo_a = prj_dir_a / "notes.txt"
    todo_a.write_text(
        textwrap.dedent(
            """
            [ ] Finish project-A.

            [ ]* This task is flagged.
                 It shows in a Flagged Items section near the top.
            """
        )
    )
    assert todo_a.exists()

    todo_b = prj_dir_b / "notes.txt"
    todo_b.write_text(
        textwrap.dedent(
            """
            [ ] Finish project-B.

            [ ]+ This task is elevated. It is displayed in bold text.

            [ ] This task is tagged #needs-something
                It shows in a Tagged Items section below Flagged Items.
                Multiple instances of a tag are grouped in that section.
            """
        )
    )
    assert todo_b.exists()

    todo_c = prj_dir_c / "notes.txt"
    todo_c.write_text(
        textwrap.dedent(
            """
            [ ] Finish project-C.
            """
        )
    )
    assert todo_c.exists()

    output_html = doc_dir / "project-tasks.html"
    output_txt = doc_dir / "project-tasks.txt"

    opt_file = test_home / "todolister.opt"
    opt_file.write_text(
        textwrap.dedent(
            """
            # todolister.opt for test.

            [output]
            filename="{0}"
            by_modified_time_desc=False
            do_text_file=Yes
            do_text_file_dt=No
            no_html=n
            title="Projects To-Do"

            #  True/False, Yes/No, y/n, and 1/0 all work for switch settings
            #  (case-insensitive).


            [match]
            "^notes.*.txt$"
            ".*notes.txt$"
            "^todo.*.txt$"
            ".*-todo.txt$"
            "^Context-.*.txt$"

            #  The [match] section is optional. These are same
            #  as the default patterns.


            [folders]
            "{1}"+

            #  '+' is the switch for recursive scan into sub-folders.

            [exclude]
            "{2}

            #  In this scenario, we don't want to see projects
            #  in the "Hold" folder.
            """
        ).format(str(output_html.with_suffix("")), str(prj_dir), str(hold_dir))
    )

    #  Run test.
    args = ["--no-browser", "--options-file", str(opt_file)]
    result = todolister.main(args)
    assert result == 0

    assert output_html.exists()
    assert output_txt.exists()

    text = output_txt.read_text()
    assert "project-A" in text
    assert "project-B" in text
    assert "project-C" not in text


def test_bad_match_spec(tmp_path, capsys):
    reload(todolister)
    assert len(todolister.file_list) == 0

    #  Create a test directory tree.
    test_home = tmp_path / "test" / "home"
    test_home.mkdir(parents=True)

    doc_dir = test_home / "Documents"
    doc_dir.mkdir()

    prj_dir = test_home / "Projects"

    prj_dir.mkdir()
    todo_a = prj_dir / "notes.md"
    todo_a.write_text(
        textwrap.dedent(
            """
            [ ] Hold my beer.
            """
        )
    )

    output_html = doc_dir / "project-tasks.html"

    opt_file = test_home / "todolister.opt"
    opt_file.write_text(
        textwrap.dedent(
            """
            # todolister.opt for test.

            [output]
            filename="{0}"
            by_modified_time_desc=False
            do_text_file=No
            do_text_file_dt=No
            no_html=n
            title="Projects To-Do"

            [match]
            "*.md$"
            ".*\\.md"

            # The first match spec above is bad. It causes an exception if not
            # caught. The second one is good. The backslash has to be escaped
            # here. There will be a single backslash in the opt file.

            [folders]
            "{1}"+
            """
        ).format(str(output_html.with_suffix("")), str(prj_dir))
    )
    #  Run test.
    args = ["--no-browser", "--options-file", str(opt_file)]
    result = todolister.main(args)
    assert result == 0

    captured = capsys.readouterr()
    assert "ERROR bad match spec '*.md$'" in captured.out

    assert output_html.exists()
    text = output_html.read_text()
    assert "Hold my beer." in text


def test_option_add_match(tmp_path, capsys):
    reload(todolister)
    assert len(todolister.file_list) == 0

    #  Create a test directory tree.
    test_home = tmp_path / "test" / "home"
    test_home.mkdir(parents=True)

    doc_dir = test_home / "Documents"
    doc_dir.mkdir()

    prj_dir = test_home / "Projects"

    prj_dir.mkdir()
    todo_a = prj_dir / "dr-quack.md"
    todo_a.write_text(
        textwrap.dedent(
            """
            [ ] Hold my beer.
            """
        )
    )

    output_html = doc_dir / "project-tasks.html"

    #  Run with default match specs.
    args = [str(prj_dir), "--no-browser", "-o", str(output_html)]
    result = todolister.main(args)
    assert result == 0
    assert output_html.exists()
    text1 = output_html.read_text()
    assert "Hold my beer." not in text1, "Should not include the test markdown file."

    #  Run with added spec to match any .md file.
    reload(todolister)
    assert len(todolister.file_list) == 0
    args = [
        str(prj_dir),
        "--no-browser",
        "-o",
        str(output_html),
        "--add-match",
        "'*.md'",
    ]
    result = todolister.main(args)
    assert result == 0
    assert output_html.exists()
    text2 = output_html.read_text()
    assert "Hold my beer." in text2, "Should include the test markdown file."


def test_includes_list_item_style_todo(tmp_path):
    reload(todolister)
    assert len(todolister.file_list) == 0

    #  Create a test directory tree.
    doc_dir = tmp_path / "Documents"
    doc_dir.mkdir()
    prj_dir = tmp_path / "Projects"
    prj_dir.mkdir()
    todo_md = prj_dir / "dr-quack.md"
    todo_md.write_text(
        textwrap.dedent(
            """
            [ ] A to-do item should be listed.

            - [ ] A list-item to-do, such as used in Obsidian, should be listed.

            - [x] A done list-item to-do should not be listed.

            """
        )
    )
    output_html = doc_dir / "project-tasks.html"

    #  include *.md in match specs.
    args = [
        str(prj_dir),
        "--no-browser",
        "-o",
        str(output_html),
        "--add-match",
        "'*.md'",
    ]
    result = todolister.main(args)
    assert result == 0
    assert output_html.exists()
    htm = output_html.read_text()
    assert "A to-do" in htm
    assert "A list-item to-do" in htm
    assert "should not" not in htm
