from dotenv import load_dotenv
import os
import logging
import sys

def log_begin():
    load_dotenv()
    out_handler = logging.StreamHandler(sys.stdout)
    out_handler.setLevel(logging.DEBUG)
    out_handler.addFilter(lambda x: x.levelno <= logging.WARNING)
    err_handler = logging.StreamHandler(sys.stderr)
    err_handler.setLevel(logging.ERROR)

    logging.basicConfig(level=logging.INFO, handlers=[out_handler, err_handler], format=os.getenv("LOG_FORMAT").replace("\\t", "\t"))  # type: ignore
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("uvicorn.error").name = "uvicorn"
