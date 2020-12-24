import logging


def mute_root_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.CRITICAL)
    for _handler in root_logger.handlers:
        root_logger.removeHandler(_handler)


def configure_logging(logger_name: str) -> logging.Logger:
    debug = 1
    if isinstance(debug, str) and debug.isdigit():
        debug = int(debug)

    LEVELS = {
        True: logging.DEBUG,
        False: logging.WARNING,
    }

    FORMATS = {
        0: "{asctime} | {name}.{levelname} | {module}.{funcName} | {message}",
        1: "{asctime} | {name}.{levelname}\n| {pathname}:{lineno}\n| {message}\n",
    }

    lvl = LEVELS[debug]
    fmt = FORMATS[debug]

    mute_root_logger()

    logger = logging.getLogger(logger_name)
    logger.setLevel(lvl)

    handler = logging.StreamHandler()
    handler.setLevel(lvl)

    formatter = logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S", style="{")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
