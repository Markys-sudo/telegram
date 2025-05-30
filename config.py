from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
TOKEN_TG = os.getenv('TOKEN_TG')
TOKEN_GPT= os.getenv('TOKEN_GPT')
PROXY_GPT = os.getenv('PROXY_GPT')

LOG_FILE = f"logs/log_call_{datetime.now().strftime('%Y-%m-%d')}.log"