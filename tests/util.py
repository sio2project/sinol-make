import os


def get_simple_package_path():
    """Get path to simple package (/tests/packages/abc)"""
    return os.path.join(os.path.dirname(__file__), "packages", "abc")


def get_verify_status_package_path():
    """
    Get path to package for veryfing status order (/test/packages/vso)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "vso")


def get_checker_package_path():
    """
    Get path to package for checker (/test/packages/chk)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "chk")
