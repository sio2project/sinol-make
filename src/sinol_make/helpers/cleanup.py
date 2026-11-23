import fnmatch
import os
import shutil

from sinol_make import util


def get_cleanup_patterns(config):
    """Returns and validates cleanup patterns from config."""
    patterns = config.get("sinol_cleanup_patterns", [])

    if not isinstance(patterns, list):
        util.exit_with_error(
            "sinol_cleanup_patterns must be a list."
        )

    for pattern in patterns:
        if not isinstance(pattern, str) or not pattern:
            util.exit_with_error(
                "All sinol_cleanup_patterns must be non-empty strings."
            )

        if os.path.isabs(pattern):
            util.exit_with_error(
                f"Cleanup pattern must be relative: {pattern}"
            )

        if ".." in pattern.split("/"):
            util.exit_with_error(
                f"Cleanup pattern cannot contain '..': {pattern}"
            )

        if "**" in pattern:
            util.exit_with_error(
                f"Cleanup pattern '**' is not supported: {pattern}"
            )

        if pattern in ("*", "*/"):
            util.exit_with_error(
                f"Cleanup pattern '{pattern}' is not allowed."
            )

        if pattern == "/":
            util.exit_with_error(
                "Cleanup pattern '/' is not allowed."
            )

    return patterns


def matches_cleanup_pattern(relative_path, pattern, is_dir):
    """
    Checks whether a path matches a cleanup pattern.

    Patterns ending with '/' match directories only.
    Other patterns match files only.

    Patterns without '/' match names at any level.
    Patterns with '/' match paths relative to the package root.
    """
    directory_only = pattern.endswith("/")

    if directory_only != is_dir:
        return False

    if directory_only:
        pattern = pattern[:-1]

    relative_path = relative_path.replace(os.sep, "/")

    if "/" not in pattern:
        name = relative_path.rsplit("/", 1)[-1]
        return fnmatch.fnmatchcase(name, pattern)

    path_parts = relative_path.split("/")
    pattern_parts = pattern.split("/")

    if len(path_parts) != len(pattern_parts):
        return False

    return all(
        fnmatch.fnmatchcase(path_part, pattern_part)
        for path_part, pattern_part in zip(path_parts, pattern_parts)
    )


def find_cleanup_paths(root_dir, patterns, excluded_dirs=None):
    """Returns files and directories matching cleanup patterns."""
    result = []
    excluded_dirs = set(excluded_dirs or [])

    for current_dir, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [
            name for name in dirs
            if name not in excluded_dirs
        ]
        for name in list(dirs):
            path = os.path.join(current_dir, name)
            relative_path = os.path.relpath(path, root_dir)

            if any(
                matches_cleanup_pattern(
                    relative_path,
                    pattern,
                    is_dir=True,
                )
                for pattern in patterns
            ):
                result.append(path)

                # Do not descend into a directory which will be removed.
                dirs.remove(name)

        for name in files:
            path = os.path.join(current_dir, name)
            relative_path = os.path.relpath(path, root_dir)

            if any(
                matches_cleanup_pattern(
                    relative_path,
                    pattern,
                    is_dir=False,
                )
                for pattern in patterns
            ):
                result.append(path)

    return result


def remove_cleanup_paths(root_dir, patterns, excluded_dirs=None):
    """Removes files and directories matching cleanup patterns."""
    cleanup_paths = find_cleanup_paths(root_dir, patterns, excluded_dirs)

    for path in cleanup_paths:
        if os.path.islink(path) or not os.path.isdir(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

    return len(cleanup_paths)
