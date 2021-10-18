"""
Tests for todolister.py.

TDD was not used in creating todolister.py.  These tests were added after
there was a working version.  Most, if not all, of these tests are functional
tests rather than unit tests.

"""

from importlib import reload
import html5lib
import pytest
import textwrap

import todolister


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
    """
    p = tmp_path_factory.mktemp("testdata")
    write_notes_txt(p)
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
    write_wonotest_txt(p)
    return p


def test_runs_and_fills_lists(todo_files_dir):
    reload(todolister)
    assert len(todolister.file_list) == 0

    d = todo_files_dir
    excl_dir = str(d / "NotThisDir")
    args = [
        "todolister.py",
        str(d),
        "--recurse",
        "-x",
        excl_dir,
        "--output-file",
        "from-test_runs_and_fills_lists",
    ]
    args.append("--no-browser")

    result = todolister.main(args)
    assert result == 0

    assert 0 < len(todolister.file_specs)
    assert len(todolister.file_specs) == len(todolister.default_file_specs)
    assert len(todolister.dirs_to_scan) == 1
    expected_n_files = 8
    assert len(todolister.file_list) == expected_n_files
    assert len(todolister.todo_files) == expected_n_files
    assert 0 < len(todolister.flagged_items)
    assert 0 < len(todolister.item_tags)


def test_no_recurse(todo_files_dir):
    reload(todolister)
    assert len(todolister.file_list) == 0
    d = todo_files_dir
    args = [
        "todolister.py",
        str(d),
        "--no-browser",
        "--output-file",
        "from-test_no_recurse",
    ]
    result = todolister.main(args)
    assert result == 0
    n_files_not_in_subdir = 7
    assert len(todolister.file_list) == n_files_not_in_subdir


def test_html_output_is_parsable(todo_files_dir):
    reload(todolister)
    assert len(todolister.file_list) == 0
    args = [
        "todolister.py",
        str(todo_files_dir),
        "--no-browser",
        "--output-file",
        "from-test_html_output_is_parsable",
    ]
    result = todolister.main(args)
    assert result == 0
    html = todolister.get_html_output("TEST")
    parser = html5lib.HTMLParser(strict=True)
    document = parser.parse(html)
    check = document.findall(".//*[@name='Main']")
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
        "todolister.py",
        str(d),
        "--no-browser",
        "--output-file",
        "from-test_file_permission_error",
    ]
    result = todolister.main(args)
    assert result == 0

    assert 0 < len(todolister.error_messages)

    html = todolister.get_html_output("TEST")
    assert "ERROR (PermissionError):" in html


def get_pre_text(element, id):
    """
    Use XPath expressions to get text from the <pre> tag elements inside
    an element, such as a <div>, with the given id.
    """
    ns = "{http://www.w3.org/1999/xhtml}"
    pre_qry = f".//*{ns}pre"
    result = []
    a = element.find(f'.//*[@id="{id}"]')
    if a is not None:
        b = a.findall(pre_qry)
        if b is not None:
            for e in b:
                result.append(e.text)
    return result


def test_html_details(tmp_path):
    reload(todolister)
    assert len(todolister.file_list) == 0

    d = tmp_path / "testdata2"
    d.mkdir()
    #  Create a test file.
    p = d / "notes.txt"
    p.write_text(
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
    assert p.exists()
    #  Run test.
    args = [
        "todolister.py",
        str(d),
        "--no-browser",
        "--output-file",
        "from-test_html_details",
    ]
    result = todolister.main(args)
    assert result == 0

    html = todolister.get_html_output("TEST")

    doc = html5lib.parse(html)

    flagged_items = get_pre_text(doc, "flagged_items")
    assert len(flagged_items) == 2

    tagged_items = get_pre_text(doc, "tagged_items")
    assert len(tagged_items) == 2

    main_items = get_pre_text(doc, "main")
    assert len(main_items) == 5

    assert "(should not be shown)" not in html
