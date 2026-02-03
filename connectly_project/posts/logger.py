import logging


class LoggerSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger = logging.getLogger("connectly.posts")
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            cls._instance.logger = logger
        return cls._instance

    @classmethod
    def get_logger(cls):
        return cls().logger
