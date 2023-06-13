import os
from pathlib import Path
import environ
from .base import *

env = environ.Env()
env_file_path = os.path.join(Path(__file__).resolve().parent, ".env")
environ.Env.read_env(env_file_path)

environment = env("ENV", default="development")

if environment == "production":
    from .production import *

else:
    from .development import *
