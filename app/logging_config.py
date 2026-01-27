import logging
import os
from logging.handlers import RotatingFileHandler

def configure_logging(log_dir: str, level: str = "INFO"):
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(level.upper())

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Rotating file
    fh = RotatingFileHandler(os.path.join(log_dir, "app.log"), maxBytes=2_000_000, backupCount=5)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
