# -*- coding: utf-8 -*-

import sys
import threading
import time
import logging


def configure_logger(log_level, message_format='%(levelname)s: %(message)s'):
    logging.basicConfig(level=log_level, format=message_format)


def info(msg, *args, **kwargs):
    logging.info(msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
    logging.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    logging.error(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    logging.debug(msg, *args, **kwargs)


class PrintProgressThread(threading.Thread):
    def __init__(self):
        super(PrintProgressThread, self).__init__()
        self.stop_event = threading.Event()
        self.setDaemon(True)
        self._start_message = 'Thread running...'
        self._end_message = '\ndone!'

    def run(self):
        while not self.stop_event.is_set():
            for cursor in ['*  ', ' * ', '  *']:
                sys.stdout.write(cursor + self._start_message)
                sys.stdout.flush()
                time.sleep(0.5)
                sys.stdout.write('\r')
        if self._end_message is not None:
            sys.stdout.write(self._end_message + '\n')

    def set_start_message(self, start_message):
        self._start_message = start_message

    def set_end_message(self, end_message):
        self._end_message = end_message

    def stop(self):
        self.stop_event.set()
