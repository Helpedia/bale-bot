import os
from pathlib import Path
import environ

env = environ.Env(DEBUG=(bool, True))
env_file_path = os.path.join(Path(__file__).resolve().parent, ".env")
environ.Env.read_env(env_file_path)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {"default": env.db(var="DEFAULT_DATABASE_URL")}

TOKEN = env("BALE_BOT_TOKEN")
BALE_BOT_BASE_URL = 'https://tapi.bale.ai/{token}/'.format(token=TOKEN)

WELCOME_MESSAGE = env("WELCOME_MESSAGE")
LEGAL_HOURS_FOR_MESSAGE_FORWARDING= env("LEGAL_HOURS_FOR_MESSAGE_FORWARDING")


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{name} {levelname} {asctime} {module} {lineno:d} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "bale_bot.log",
            "level": "DEBUG",
            "when": "midnight",
            "backupCount": 15,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "": {"level": "DEBUG", "handlers": ["file"]},
    },
}
