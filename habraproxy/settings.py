"""
Global settings for project.

May be just some literals, or path-related values.

All environment-based settings should be declared here too.
"""

import pathlib

from dotenv import load_dotenv  # type: ignore
from environs import Env

load_dotenv()

env = Env()
env.read_env()

BASE_DIR = pathlib.Path(__file__).resolve().parent
