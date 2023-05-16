import os

def get_simple_package_path():
    """Get path to simple package (/tests/abc)"""
    return os.path.join(os.path.dirname(__file__), "abc")
