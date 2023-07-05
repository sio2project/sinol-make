import os

def get_simple_package_path():
    """Get path to simple package (/tests/packages/abc)"""
    return os.path.join(os.path.dirname(__file__), "packages", "abc")

def get_verify_status_package_path():
    """
    Get path to package for veryfing status order (/test/packages/vso)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "vso")


def get_weak_compilation_flags_package_path():
    """
    Get path to package for testing weak compilation flags (/test/packages/wcf)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "wcf")
