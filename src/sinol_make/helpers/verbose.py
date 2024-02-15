import logging
import shutil
import os

from sinol_make.helpers import paths


__verbose__ = False


def set_verbose(verbose: bool):
    global __verbose__
    __verbose__ = verbose
    shutil.rmtree(paths.get_cache_path('logs'), ignore_errors=True)
    os.makedirs(paths.get_cache_path('logs'), exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, filename=paths.get_cache_path('logs', 'sinol_make.log'), filemode='w',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def is_verbose():
    return __verbose__
