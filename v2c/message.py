# -*- coding: utf-8 -*-

import sys
import threading
import time


class ConsoleLogger:
    _logger_instance = None

    @staticmethod
    def get_instance():
        if ConsoleLogger._logger_instance is None:
            ConsoleLogger._logger_instance = ConsoleLogger()
        return ConsoleLogger._logger_instance

    def info(self, message):
        self._print_log('INFO: ' + message)

    def warn(self, message):
        self._print_log('WARN: ' + message)

    def error(self, message):
        self._print_log('ERROR: ' + message)

    def debug(self, message):
        self._print_log('DEBUG: ' + message)

    def _print_log(self, message):
        print(message)


class PrintProgressThread(threading.Thread):
    def __init__(self):
        super(PrintProgressThread, self).__init__()
        self.stop_event = threading.Event()
        self.setDaemon(True)
        self._start_message = 'Thread running...'
        self._end_message = '\ndone!'

    def run(self):
        while not self.stop_event.is_set():
            for cursor in '\\|/-':
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
