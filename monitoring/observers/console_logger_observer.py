import os
from rich import pretty, inspect, console

from .logger_observer_interface import LoggerObserverInterface


class ConsoleLoggerObserver(LoggerObserverInterface):
    def __init__(
        self, identifier: str = os.urandom(4).hex(), identify: bool = False
    ) -> None:
        self.identifier = identifier
        self.identify = identify
        self.console = console.Console()
        self.console.print_inspect = inspect
        #pretty.install()

    def get_prefix(self) -> str:
        return f"[{self.identifier}] " if self.identify else ""

    def on_success(self, message: str) -> None:
        composed_success_message = f"{self.get_prefix()}{message}"
        self.console.print(composed_success_message, style="bold green")

    def on_info(self, message: str) -> None:
        composed_info_message = f"{self.get_prefix()}{message}"
        self.console.print(composed_info_message, style="bold cyan")

    def on_warning(self, message: str) -> None:
        composed_warning_message = f"{self.get_prefix()}⚠️ WARNING: {message}"
        self.console.print(composed_warning_message, style="bold yellow")

    def on_error(self, message: str, exception: Exception | None) -> None:
        composed_error_message = f"{self.get_prefix()}❌ ERROR: {message}"
        self.console.print(composed_error_message, style="bold red")
        if exception:
            self.console.print("Exception raised ⬇️", style="red")
            self.console.print_inspect(exception)

    def on_debug(self, message: str) -> None:
        composed_debug_message = f"{self.get_prefix()}{message}"
        self.console.print(composed_debug_message, style="bold bright_black")
