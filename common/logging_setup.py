"""Unified console logging: [INFO] name: message / [ERROR] name: message."""
import logging
import sys


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure root logger for console. Format: "[LEVEL] name: message".
    Use for flow: start, message received, OpenAI request, DB write, responses, errors.
    Returns logger for the given name.
    """
    root = logging.getLogger()
    if root.handlers:
        return logging.getLogger(name)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(level)
    return logging.getLogger(name)
