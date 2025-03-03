import multiprocessing

from sinol_make.helpers import loggers


def init_worker(logging_enabled):
    loggers.set_worker_logging_enabled(logging_enabled)


def mp_pool(num_cpus):
    return multiprocessing.Pool(num_cpus, initializer=init_worker, initargs=(loggers.logging_enabled,))
