import os
import logging.config
from src.main import main


CURRENT_WORK_DIR = os.path.dirname(os.path.abspath(__file__))


logging.config.fileConfig(os.path.join(CURRENT_WORK_DIR, "docker", "logging.conf"))


if __name__ == "__main__":
    main()
