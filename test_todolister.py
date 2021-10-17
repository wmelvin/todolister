import html5lib
import pytest
import textwrap

import todolister


def text_content():
    return textwrap.dedent(
        """
        [ ] Do this thing.

        [x] ...but not this thing, because it's already done.
        """
    )


@pytest.fixture(scope="module")
def todo_files_dir(tmp_path_factory):
    p = tmp_path_factory.mktemp("todo")
    file_1 = p / "notes-test.txt"
    file_1.write_text(text_content())
    return p


# def test_1():
#     args = ["todolister.py", "-f", "todolister.opt", "--no-browser"]
#     result = todolister.main(args)
#     assert result == 0


# def test_2(tmp_path):
#     test_dir = tmp_path / "todo"
#     test_dir.mkdir()
#     test_file = test_dir / "notes-test2.txt"
#     test_file.write_text(
#         textwrap.dedent(
#             """
#             [ ] Do this thing.

#             [x] ...but not this thing, because it's already done.
#             """
#         )
#     )
#     args = ["todolister.py", str(test_dir)]
#     args.append("--no-browser")
#     result = todolister.main(args)
#     assert result == 0


def test_runs_and_fills_lists(todo_files_dir):
    args = ["todolister.py", str(todo_files_dir)]
    args.append("--no-browser")
    result = todolister.main(args)
    assert result == 0
    assert 0 < len(todolister.file_specs)
    assert 0 < len(todolister.dirs_to_scan)
    assert 0 < len(todolister.file_list)
    assert 0 < len(todolister.todo_files)


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
