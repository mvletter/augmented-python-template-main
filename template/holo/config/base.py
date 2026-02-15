import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


extra_settings = {}
if not os.environ.get("ENVIRONMENT"):  # local dev
    project_root = Path(__file__).parent.parent.parent

    env_dev = project_root / ".env.dev"
    env_dev_override = project_root / ".env.dev.override"

    env_files = (str(env_dev),)
    if env_dev_override.is_file():
        env_files += (str(env_dev_override),)
    extra_settings["env_file"] = env_files


class HoloSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", **extra_settings)
