import logging.config


def init_logger():
    logging_settings = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '[%(levelname)s][%(asctime)s] : %(message)s',
                'datefmt': '%d-%m-%Y %H:%M:%S'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'INFO',
            },
        }
    }
    logging.config.dictConfig(logging_settings)
