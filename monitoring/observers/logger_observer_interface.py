from abc import ABC, abstractmethod
from typing import Optional


class LoggerObserverInterface(ABC):
    @abstractmethod
    def on_success(self, message: str) -> None:
        """
        Method to be called when a success log is received.
        Should be implemented by the extending class.

        Args:
            message (str): The log message.
        """
        ...

    @abstractmethod
    def on_info(self, message: str) -> None:
        """
        Method to be called when an info log is received.
        Should be implemented by the extending class.

        Args:
            message (str): The log message.
        """
        ...

    @abstractmethod
    def on_warning(self, message: str) -> None:
        """
        Method to be called when a warning log is received.
        Should be implemented by the extending class.

        Args:
            message (str): The log message.
        """
        ...

    @abstractmethod
    def on_error(self, message: str, exception: Optional[Exception]) -> None:
        """
        Method to be called when an error log is received.
        Should be implemented by the extending class.

        Args:
            message (str): The log message.
            exception (Exception, optional): The exception that might have been raised.
        """
        ...

    @abstractmethod
    def on_debug(self, message: str) -> None:
        """
        Method to be called when a debug log is received.
        Should be implemented by the extending class.

        Args:
            message (str): The log message.
        """
        ...
