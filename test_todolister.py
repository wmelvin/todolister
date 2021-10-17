
import textwrap

import todolister


def test_1():
    args = ["todolister.py", "-f", "todolister.opt", "--no-browser"]
    result = todolister.main(args)
    assert result == 0


def test_2(tmp_path):
    test_dir = tmp_path / "todo"
    test_dir.mkdir()
    test_file = test_dir / "notes-test2.txt"
    test_file.write_text(
        textwrap.dedent(
            """
            [ ] Do this thing.

            [x] ...but not this thing, because it's already done.
            """
        )
    )
    args = ["todolister.py", str(test_dir), "--no-browser"]
    # args = ["todolister.py", str(test_dir)]
    result = todolister.main(args)
    assert result == 0
