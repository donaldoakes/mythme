import logging
from os import environ
from dotenv import load_dotenv

load_dotenv()

log_format = "%(asctime)s %(levelname)0s: %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

log_level = environ.get("MYTHME_LOG_LEVEL", "INFO")
if log_level == "TRACE":
    # all logging is at debug
    logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=date_format)
else:
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format)
level = logging.getLevelNamesMapping()[log_level]
logger = logging.getLogger("mythtv")
logger.setLevel(level)
if log_level != "TRACE":
    # httpx and azure http logging are very chatty at INFO level
    logging.getLogger("httpx").setLevel(logging.WARN)
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
        logging.WARN
    )
