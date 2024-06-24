import logging


# class ErrorLogFilter(logging.Filter):
#     def filter(self, record):
#         return record.levelname in ('INFO', 'WARNING', 'ERROR')


class InfoWarningLogFilter(logging.Filter):
    def filter(self, record):
        return 'failed to fetch updates' not in record.msg.lower() and 'sleep for' not in record.msg.lower() and 'connection established' not in record.msg.lower()


class CriticalLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'CRITICAL'


class ErrLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == 'ERROR'
