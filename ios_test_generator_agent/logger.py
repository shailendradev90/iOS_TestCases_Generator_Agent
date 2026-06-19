"""Logging configuration for the iOS Test Generator Agent."""

from __future__ import annotations

import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

# Global console for rich output
console = Console()


class AgentLogger:
    """Centralized logging for the iOS Test Generator Agent."""

    _instance: AgentLogger | None = None
    _initialized: bool = False

    def __new__(cls) -> AgentLogger:
        """Singleton pattern to ensure one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the logger (only once)."""
        if not self._initialized:
            self.logger = logging.getLogger("ios_test_generator_agent")
            self.logger.setLevel(logging.INFO)
            self._initialized = True

    def setup(
        self,
        level: int = logging.INFO,
        log_file: Path | None = None,
        verbose: bool = False,
    ) -> None:
        """Configure logging handlers and formatters.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path to write logs to
            verbose: If True, set level to DEBUG
        """
        # Clear existing handlers
        self.logger.handlers.clear()

        # Set level
        if verbose:
            level = logging.DEBUG
        self.logger.setLevel(level)

        # Console handler with Rich formatting
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=verbose,
        )
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            "%(message)s",
            datefmt="[%X]",
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler (if specified)
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, **kwargs)


# Global logger instance
logger = AgentLogger()


def get_logger() -> AgentLogger:
    """Get the global logger instance."""
    return logger


def setup_logging(
    level: int = logging.INFO,
    log_file: Path | None = None,
    verbose: bool = False,
) -> None:
    """Setup logging configuration.

    Args:
        level: Logging level
        log_file: Optional file path to write logs to
        verbose: If True, enable verbose logging
    """
    logger.setup(level=level, log_file=log_file, verbose=verbose)

# Made with Bob
