# connectiva/logging_config.py

import logging
from typing import Optional, List

def setup_logging(
    log_to_stdout: bool = False,
    log_file: Optional[str] = None,
    custom_handlers: Optional[List[logging.Handler]] = None,
    log_level: str = "INFO"
):
    """
    Set up logging configuration.

    :param log_to_stdout: Flag to log to stdout if True.
    :param log_file: File path to save logs if provided.
    :param custom_handlers: List of custom logging handlers.
    :param log_level: Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    # Convert log level string to logging module level
    log_level = getattr(logging, log_level.upper(), logging.INFO)

    if custom_handlers:
        handlers = custom_handlers
    else:
        handlers = []

        if log_to_stdout:
            handlers.append(logging.StreamHandler())

        if log_file:
            handlers.append(logging.FileHandler(log_file))

        # If no handlers provided, use default StreamHandler
        if not handlers:
            handlers = [logging.StreamHandler()]

    # Configure logging with the specified handlers
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


