import sys

from filters.log_filters import CriticalLogFilter, ErrLogFilter, InfoWarningLogFilter

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '#%(levelname)-8s %(name)s:%(funcName)s - %(message)s'
        },
        'formatter_1': {
            'format': '[%(asctime)s] #%(levelname)-8s %(filename)s:'
                      '%(lineno)d - %(name)s:%(funcName)s - %(message)s'
        },
        'formatter_2': {
            'format': '#%(levelname)-8s [%(asctime)s] - %(filename)s:'
                      '%(lineno)d - %(name)s:%(funcName)s - %(message)s'
        },
        'formatter_3': {
            'format': '#%(levelname)-8s [%(asctime)s] - %(filename)s:'
                      '%(lineno)d - %(name)s:%(funcName)s - %(message)s'
        }
    },
    'filters': {
        'critical_filter': {
            '()': CriticalLogFilter,
        },
        'error_filter': {
            '()': ErrLogFilter,
        },
        'info_warning_filter': {
            '()': InfoWarningLogFilter,
        },
        # 'errlogfilter': {'()': ErrLogFilter}

    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default'
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': '../logs/error.log',
            'mode': 'w',
            'level': 'INFO',
            'formatter': 'formatter_1',
            # 'filters': ['debug_warning_filter', 'error_filter'],
            'encoding': 'utf-8'
        },
        'critical_file': {
            'class': 'logging.FileHandler',
            'filename': '../logs/critical_errors.log',
            'mode': 'w',
            'level': 'ERROR',
            'formatter': 'formatter_3',
            'filters': ['critical_filter'],
            'encoding': 'utf-8'
        },
        'info_file': {
            'class': 'logging.FileHandler',
            'filename': '../logs/info.log',
            'mode': 'w',
            'level': 'INFO',
            'formatter': 'formatter_1',
            'filters': ['info_warning_filter'],
            'encoding': 'utf-8'
        },
            },
    'loggers': {
        'database.methods': {
            'level': 'ERROR',
            'handlers': ['critical_file']
        },
        'database.models': {
            'level': 'ERROR',
            'handlers': ['critical_file']
        },
        'handlers.users_handlers': {
            'level': 'ERROR',
            'handlers': ['critical_file']
        },
        'handlers.authorized_user_handlers': {
            'level': 'ERROR',
            'handlers': ['critical_file']
        },
        'services.services': {
            'level': 'INFO',
            'handlers': ['critical_file']
        },
    },
    'root': {
        'level': 'INFO',
        'formatter': 'default',
        'propagate': False,
        'handlers': ['default', 'info_file']
    }

}
