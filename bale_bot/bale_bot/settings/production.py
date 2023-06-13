import os
from pathlib import Path
import environ

env = environ.Env(DEBUG=(bool, False))
env_file_path = os.path.join(Path(__file__).resolve().parent, ".env")
environ.Env.read_env(env_file_path)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": env.db(var="DEFAULT_DATABASE_URL"),
}

TOKEN = env("BALE_BOT_TOKEN")
BALE_BOT_BASE_URL = 'https://tapi.bale.ai/{token}/'.format(token=TOKEN)

WELCOME_MESSAGE = env("WELCOME_MESSAGE")
LEGAL_HOURS_FOR_MESSAGE_FORWARDING= env("LEGAL_HOURS_FOR_MESSAGE_FORWARDING")


# Logging

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
            "filename": "/var/log/bale_bot/bale_bot.log",
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


EMAIL_HOST = ""
EMAIL_PORT = 25
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

CORS_ALLOW_ALL_ORIGINS = True

SECURE_HSTS_SECONDS = 2592000  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['']
