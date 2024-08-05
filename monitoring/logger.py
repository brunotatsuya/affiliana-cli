from typing import List, Optional
from .constants import LogTypeEnum
from .observers import LoggerObserverInterface


class Logger:
    """
    Class that implements logging through the observer pattern.
    Supports logging of messages of type SUCCESS, INFO, WARNING, ERROR, and DEBUG.
    """

    def __init__(self):
        self._observers = {
            LogTypeEnum.SUCCESS: [],
            LogTypeEnum.INFO: [],
            LogTypeEnum.WARNING: [],
            LogTypeEnum.ERROR: [],
            LogTypeEnum.DEBUG: [],
        }

    def __check_log_type(self, log_type: any) -> None:
        """
        Checks if a provided log type is valid.

        Args:
            log_type (any): The log type to be checked.

        Raises:
            ValueError: If the log type is not valid.
        """
        if log_type not in LogTypeEnum.__members__.values():
            raise ValueError(f"Invalid log type: {log_type.value}")

    def subscribe(
        self, observer: LoggerObserverInterface, to_types: List[LogTypeEnum]
    ) -> None:
        """
        Subscribes an observer for a specific log types.

        Args:
            observer (LoggerObserverInterface): The observer to be subscribed.
            to_types (List[LogTypeEnum]): The log types to subscribe the observer for.

        Raises:
            ValueError: If any of the provided log types is invalid.
        """
        [self.__check_log_type(log_type) for log_type in to_types]

        for log_type in to_types:
            if observer not in self._observers[log_type]:
                if not hasattr(observer, f"on_{log_type.value.lower()}"):
                    raise AttributeError(
                        f"Observer {observer} does not have the method on_{log_type.value.lower()}"
                    )
                self._observers[log_type].append(observer)

    def unsubscribe(
        self, observer: LoggerObserverInterface, to_types: List[LogTypeEnum]
    ) -> None:
        """
        Unsubscribes an observer from receiving log updates for the specified log types.

        Args:
            observer (LoggerObserverInterface): The observer to unsubscribe.
            to_types (List[LogTypeEnum]): The list of log types to unsubscribe the observer from.
        """
        [self.__check_log_type(log_type) for log_type in to_types]

        for log_type in to_types:
            if observer in self._observers[log_type]:
                self._observers[log_type].remove(observer)

    def notify(
        self, message: str, log_type: LogTypeEnum, exception: Optional[Exception] = None
    ) -> None:
        """
        Notify the observers of a log.

        Args:
            message (str): The message to be logged.
            log_type (LogTypeEnum): The type of the log.
            exception (Exception, optional): The exception that might have been raised on an error log.

        Raises:
            ValueError: If the log type is not valid.
        """
        self.__check_log_type(log_type)

        for observer in self._observers[log_type]:
            params = (
                (message, exception) if log_type == LogTypeEnum.ERROR else (message,)
            )
            getattr(observer, f"on_{log_type.value.lower()}")(*params)
