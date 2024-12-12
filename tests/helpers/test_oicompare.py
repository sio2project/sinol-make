import tempfile

from sinol_make.helpers import oicompare


def test_oicompare():
    with tempfile.TemporaryDirectory() as tmpdir:
        tests = [
            ("", "", True),
            ("ABC", "ABC", True),
            ("ABC\nDEF\n", "ABC\nDEF\n", True),
            ("A B C D E", "A B\tC\0D\tE", True),
            ("A B", "\0\tA    \0 \0B\t\t", True),
            ("A\nB\nC", "A\nB\nC\n\n\n\n\n\n\n", True),
            ("A\n\n\n\n", "A\n\n\n\n\n\n\n\n\n\n", True),
            ("", "ABC", False),
            ("YES", "NO", False),
            ("A B", "A\nB", False),
        ]

        for i, (file1, file2, expected) in enumerate(tests):
            with open(tmpdir + f"/file1_{i}.txt", "w") as f1, open(tmpdir + f"/file2_{i}.txt", "w") as f2:
                f1.write(file1)
                f2.write(file2)
            assert oicompare.compare(tmpdir + f"/file1_{i}.txt", tmpdir + f"/file2_{i}.txt") == expected, f"Test {i} failed"

        for i, (file2, file1, expected) in enumerate(tests):
            with open(tmpdir + f"/file1_{i}.txt", "w") as f1, open(tmpdir + f"/file2_{i}.txt", "w") as f2:
                f1.write(file1)
                f2.write(file2)
            assert oicompare.compare(tmpdir + f"/file1_{i}.txt", tmpdir + f"/file2_{i}.txt") == expected, f"Swapped test {i} failed"
