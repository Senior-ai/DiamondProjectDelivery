from aiogram.utils.i18n import I18n
from fastapi import FastAPI
from openai import AsyncOpenAI

from .config import BOT_TOKEN, LOCALES_DIR, DEFAULT_LOCALE, I18N_DOMAIN, OPENAI_API_KEY

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

i18n: I18n = I18n(path=LOCALES_DIR.absolute(), default_locale=DEFAULT_LOCALE, domain=I18N_DOMAIN)
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

fastapi_instance = FastAPI()
