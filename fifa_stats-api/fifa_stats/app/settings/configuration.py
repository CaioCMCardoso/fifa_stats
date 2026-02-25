import logging
import sys
from fifa_stats.app.utils import env


class Configuration:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, probe: bool = False):
        self.APP_NAME = "map-fifa-stats"
        self.ENV = env.get(str, "ENV", default="DES")
        self.DEBUG = env.get(bool, "DEBUG", default=False)
        self.TESTING = env.get(bool, "TESTING", default=False)

        # onde fica o CSV
        self.CSV_PATH = env.get(str, "CSV_PATH", default="./data/player_stats.csv")

        self.LOGFILE_PATH = env.get(str, "LOGFILE_PATH", "file.log")
        self.LOG_LEVEL = "ERROR" if probe else env.get(str, "LOG_LEVEL", "INFO")

        self._LOGGER = None
        self._init_logger()

    def _init_logger(self):
        if self._LOGGER is not None:
            return

        logger = logging.getLogger(self.APP_NAME)
        logger.setLevel(self.LOG_LEVEL)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(self.LOG_LEVEL)
        ch.setFormatter(formatter)

        file_handler = logging.FileHandler(filename=self.LOGFILE_PATH)
        file_handler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(ch)
            logger.addHandler(file_handler)

        self._LOGGER = logger

    def get_logger(self):
        if self._LOGGER is None:
            self._init_logger()
        return self._LOGGER