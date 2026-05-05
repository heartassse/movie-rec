"""动态导入 dev / prod 设置。
DJANGO_ENV 环境变量可设为 'dev' 或 'prod'，默认 dev。"""
import importlib
import os

_env = os.getenv("DJANGO_ENV", "dev")
_settings_module = importlib.import_module(f".{_env}", package=__name__)

globals().update({k: v for k, v in vars(_settings_module).items() if k.isupper()})
