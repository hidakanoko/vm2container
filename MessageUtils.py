# -*- coding: utf-8 -*-


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
