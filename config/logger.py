import inject

from monitoring import Logger, LogTypeEnum, ConsoleLoggerObserver


def setup_logger():
    """
    Sets up the logger by subscribing observers to the log types.
    Each observer may log the messages in its own way.
    """
    logger = inject.instance(Logger)
    console_logger_observer = inject.instance(ConsoleLoggerObserver)

    # Subscribing the console logger observer to all log types
    logger.subscribe(
        console_logger_observer,
        [
            LogTypeEnum.SUCCESS,
            LogTypeEnum.INFO,
            LogTypeEnum.WARNING,
            LogTypeEnum.ERROR,
            LogTypeEnum.DEBUG,
        ],
    )
