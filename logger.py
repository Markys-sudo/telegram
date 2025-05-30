# logger.py
import logging
import sys
from config import LOG_FILE

LOG_FILE = LOG_FILE

LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'

# Основна конфігурація логів
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Головний логер
logger = logging.getLogger("bot")

# Окремі логери
gpt_logger = logging.getLogger("gpt")
quiz_logger = logging.getLogger("quiz")
dialog_logger = logging.getLogger("dialog")
util_logger = logging.getLogger("util")

# Вимкнення зайвого шуму
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.ext._application").setLevel(logging.WARNING)
logging.getLogger("telegram.bot").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)
