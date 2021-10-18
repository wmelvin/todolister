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
    p = tmp_path_factory.mktemp("todo")
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


def todolister_args_1(dir_path):
    excl_dir = dir_path / "NotThisDir"
    return [
        "todolister.py",
        str(dir_path),
        "--recurse",
        "-x",
        str(excl_dir),
    ]


# def test_todolister_1(todo_files_dir):
#     args = todolister_args_1(todo_files_dir)

#     args.append("--no-browser")

#     result = todolister.main(args)
#     assert result == 0


def test_runs_and_fills_lists(todo_files_dir):
    args = todolister_args_1(todo_files_dir)
    args.append("--no-browser")

    result = todolister.main(args)
    assert result == 0

    assert 0 < len(todolister.file_specs)

    assert len(todolister.file_specs) == len(todolister.default_file_specs)

    assert len(todolister.dirs_to_scan) == 1

    assert len(todolister.file_list) == 8

    assert len(todolister.todo_files) == 8


def test_html(todo_files_dir):
    args = ["todolister.py", str(todo_files_dir)]
    args.append("--no-browser")
    result = todolister.main(args)
    assert result == 0
    html = todolister.get_html_output("TEST TITLE")
    parser = html5lib.HTMLParser(strict=True)
    document = parser.parse(html)
    check = document.findall(".//*[@name='Main']")
    assert len(check) == 1
