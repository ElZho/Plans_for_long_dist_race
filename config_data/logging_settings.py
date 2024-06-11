import sys

from filters.log_filters import DebugWarningLogFilter, CriticalLogFilter, ErrLogFilter, ErrorLogFilter

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
            '()': ErrorLogFilter,
        },
        'debug_warning_filter': {
            '()': DebugWarningLogFilter,
        },
        'errlogfilter': {'()': ErrLogFilter}

    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default'
        },
        'stderr': {
            'class': 'logging.StreamHandler',
        },
        'stdout': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'formatter_2',
            'filters': ['debug_warning_filter'],
            'stream': sys.stdout
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
            },
    'loggers': {
        'database.methods': {
            'level': 'ERROR',
            'handlers': ['error_file', 'critical_file']
        },
        'database.models': {
            'level': 'ERROR',
            'handlers': ['error_file', 'critical_file']
        },
        'handlers.users_handlers': {
            'level': 'ERROR',
            'handlers': ['critical_file']
        },
        'handlers.authorized_users_handlers': {
            'level': 'ERROR',
            'handlers': ['error_file', 'critical_file', 'stdout']
        },
        # 'handlers.other_handlers': {
        #     'level': 'INFO',
        #     'handlers': ['error_file', 'critical_file']
        # },
        # 'handlers.admin_handlers': {
        #     'level': 'INFO',
        #     'handlers': ['error_file', 'critical_file']
        # },
        # 'services.calculations': {
        #     'level': 'INFO',
        #     'handlers': ['error_file', 'critical_file']
        # },
        # 'services.planing': {
        #     'level': 'INFO',
        #     'handlers': ['error_file', 'critical_file']
        # },
        'services.services': {
            'level': 'INFO',
            'handlers': ['error_file', 'critical_file', 'stdout']
        },
    },
    'root': {
        'level': 'INFO',
        'formatter': 'default',
        'propagate': False,
        'handlers': ['default', 'error_file']
    }

}
