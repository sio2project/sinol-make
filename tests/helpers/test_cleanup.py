import pytest
from sinol_make.helpers.cleanup import get_cleanup_patterns, matches_cleanup_pattern

def test_file_pattern():
    assert matches_cleanup_pattern(
        "foo.bak",
        "*.bak",
        is_dir=False,
    )

    assert matches_cleanup_pattern(
        "prog/foo.bak",
        "*.bak",
        is_dir=False,
    )

    assert not matches_cleanup_pattern(
        "foo.bak",
        "*.bak",
        is_dir=True,
    )


def test_directory_pattern():
    assert matches_cleanup_pattern(
        "__pycache__",
        "__pycache__/",
        is_dir=True,
    )

    assert matches_cleanup_pattern(
        "prog/__pycache__",
        "__pycache__/",
        is_dir=True,
    )

    assert not matches_cleanup_pattern(
        "prog/__pycache__",
        "__pycache__/",
        is_dir=False,
    )


def test_path_pattern():
    assert matches_cleanup_pattern(
        "prog/foo.e",
        "prog/*.e",
        is_dir=False,
    )

    assert not matches_cleanup_pattern(
        "doc/foo.e",
        "prog/*.e",
        is_dir=False,
    )

    assert not matches_cleanup_pattern(
        "prog/sub/foo.e",
        "prog/*.e",
        is_dir=False,
    )


@pytest.mark.parametrize("pattern", [
    "*",
    "*/",
    "../foo",
    "foo/../bar",
    "**/*.bak",
])
def test_invalid_cleanup_pattern(pattern):
    with pytest.raises(SystemExit):
        get_cleanup_patterns({
            "sinol_cleanup_patterns": [pattern],
        })


def test_cleanup_patterns_must_be_list():
    with pytest.raises(SystemExit):
        get_cleanup_patterns({
            "sinol_cleanup_patterns": "*.bak",
        })
