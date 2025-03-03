import multiprocessing
import os
import shutil
import sys
import logging
import logging.handlers

from sinol_make.helpers import paths


logger = None
logging_enabled = False


def use_logging(sm_version: str):
    global logger, logging_enabled
    logging_enabled = True
    if os.path.exists(paths.get_cache_path('logs')):
        shutil.rmtree(paths.get_cache_path('logs'))
    os.makedirs(paths.get_cache_path('logs'))

    file_handler = logging.FileHandler(paths.get_cache_path('logs', 'sinol-make.log'))
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)

    logger.debug(f'sinol-make version: {sm_version}')
    logger.debug(f'Python version: {sys.version}')
    logger.debug(f'Python path: {sys.executable}')
    logger.debug(f'Python version info: {sys.version_info}')
    logger.debug(f'System platform: {sys.platform}')
    logger.debug(f'Current working directory: {os.getcwd()}')


def set_worker_logging_enabled(value):
    global logging_enabled
    logging_enabled = value


def setup_worker_logger(name, id, dir=None):
    if not logging_enabled:
        return
    if dir:
        dir = paths.get_cache_path('logs', dir)
    else:
        dir = paths.get_cache_path('logs')
    if not os.path.exists(dir):
        os.makedirs(dir)
    file_handler = logging.handlers.RotatingFileHandler(os.path.join(dir, f'{name}-{str(id)}.log'))
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.DEBUG)
