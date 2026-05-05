from .base import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ["your-domain.com"]
CORS_ALLOWED_ORIGINS = ["https://your-frontend-domain.com"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_DB", "movierec_prod"),
        "USER": os.getenv("MYSQL_USER", "movierec"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", "securepassword"),
        "HOST": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "PORT": os.getenv("MYSQL_PORT", "3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}
