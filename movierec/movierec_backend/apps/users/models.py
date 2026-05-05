from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """自定义用户模型，暂时继承 AbstractUser，不新增字段。"""

    def __str__(self):
        return self.username
