
from rich import print
import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
        level="DEBUG" if DEBUG else "INFO",
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")

from rich.traceback import install
install()
