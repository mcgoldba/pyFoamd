import logging
from rich import print
from rich.logging import RichHandler

from rich.traceback import install
install()

def richLogger(level="INFO"):

    levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "NOTSET": logging.NOTSET
    }

    format = "%(message)s"
    logging.basicConfig(
                        level=level,
                        format=format, datefmt="[%X]",
                        handlers=[RichHandler(rich_tracebacks=True)]
    )

    logger = logging.getLogger("pf")

    handler = RichHandler(rich_tracebacks=True)
    handler.setLevel(levels[level])

    format = logging.Formatter(format, datefmt="[%X]")
    handler.setFormatter(format)

    logger.addHandler(handler)
