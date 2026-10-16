import logging

logger = logging.getLogger("menu")

if __name__ == "__main__":  # test
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(name)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("測試menu中")
