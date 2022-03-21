import logging
from rich import print
from rich.logging import RichHandler

from rich.traceback import install
install()

format = "%(message)s"
logging.basicConfig(
                    level="INFO",
                    format=format, datefmt="[%X]",
                    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("pf")

handler = RichHandler(rich_tracebacks=True)
# handler.setLevel(levels[level])

format = logging.Formatter(format, datefmt="[%X]")
handler.setFormatter(format)

logger.addHandler(handler)
