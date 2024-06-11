import logging


class ErrorLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname in ('INFO', 'WARNING', 'ERROR')


class DebugWarningLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname in ('INFO', 'WARNING')


class CriticalLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'CRITICAL'


class ErrLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'ERROR'
