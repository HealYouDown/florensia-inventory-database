import logging


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("root")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(levelname)s] %(message)s")

    # Stream handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)

    logger.addHandler(ch)

    # File handler
    fh = logging.FileHandler("log.txt")
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)

    logger.addHandler(fh)

    return logger
