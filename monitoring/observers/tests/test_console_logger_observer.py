import pytest
from unittest.mock import MagicMock

from monitoring.observers.console_logger_observer import ConsoleLoggerObserver


class TestConsoleLoggerObserver:
    @pytest.fixture
    def observer(self):
        obs = ConsoleLoggerObserver("1234", True)
        obs.console = MagicMock()
        return obs

    def test_should_return_a_prefix_with_the_identifier_when_identify_is_true(
        self, observer: ConsoleLoggerObserver
    ):
        assert observer.get_prefix() == "[1234] "

    def test_should_return_an_empty_prefix_when_identify_is_false(
        self, observer: ConsoleLoggerObserver
    ):
        observer.identify = False
        assert observer.get_prefix() == ""

    def test_should_print_a_success_message_with_the_prefix(
        self, observer: ConsoleLoggerObserver
    ):
        message = "Success message"
        observer.on_success(message)
        observer.console.print.assert_called_once_with(
            "[1234] Success message", style="bold green"
        )

    def test_should_print_an_info_message_with_the_prefix(
        self, observer: ConsoleLoggerObserver
    ):
        message = "Info message"
        observer.on_info(message)
        observer.console.print.assert_called_once_with(
            "[1234] Info message", style="bold cyan"
        )

    def test_should_print_a_warning_message_with_the_prefix(
        self, observer: ConsoleLoggerObserver
    ):
        message = "Warning message"
        observer.on_warning(message)
        observer.console.print.assert_called_once_with(
            "[1234] ⚠️ WARNING: Warning message", style="bold yellow"
        )

    def test_should_print_an_error_message_with_the_prefix_and_no_exception(
        self, observer: ConsoleLoggerObserver
    ):
        message = "Error message no exception"
        observer.on_error(message, None)
        observer.console.print.assert_called_with(
            "[1234] ❌ ERROR: Error message no exception", style="bold red"
        )

    def test_should_print_an_error_message_with_the_prefix_and_exception(
        self, observer: ConsoleLoggerObserver
    ):
        message = "Error message with exception"
        exception = Exception("An exception")

        observer.on_error(message, exception)

        observer.console.print.calls_args_list == [
            (
                ("[1234] ❌ ERROR: Error message with exception",),
                {"style": "bold red"},
            ),
            (("Exception raised ⬇️",), {"style": "red"}),
        ]

        observer.console.print_inspect.assert_called_once_with(exception)

    def test_should_print_a_debug_message_with_the_prefix(
        self, observer: ConsoleLoggerObserver
    ):
        message = "Debug message"
        observer.on_debug(message)
        observer.console.print.assert_called_once_with(
            "[1234] Debug message", style="bold bright_black"
        )
