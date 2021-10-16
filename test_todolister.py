
import sys
import todolister


# def test_1(capsys):
#     sys.stderr.write("blah\n")
#     a = capsys.readouterr()
#     assert a.err == "blah\n"
#     # assert False
#     # todolister


def test_1():
    args = ["todolister.py", "-f", "todolister.opt", "--no-browser"]
    result = todolister.main(args)
    assert result == 0
