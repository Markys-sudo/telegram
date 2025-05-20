from dotenv import load_dotenv
import os

load_dotenv()
TOKEN_TG = os.getenv('TOKEN_TG')
TOKEN_GPT= os.getenv('TOKEN_GPT')
PROXY_GPT = os.getenv('PROXY_GPT')