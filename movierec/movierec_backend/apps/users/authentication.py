"""
自定义认证类，允许无效token时匿名访问
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework import exceptions


class OptionalJWTAuthentication(JWTAuthentication):
    """
    可选的JWT认证类：如果token无效或缺失，允许匿名访问
    只有在token有效时才进行认证
    """
    
    def authenticate(self, request):
        """
        尝试进行JWT认证，如果失败则返回None（允许匿名访问）
        """
        try:
            # 尝试调用父类的认证方法
            return super().authenticate(request)
        except (InvalidToken, AuthenticationFailed, exceptions.AuthenticationFailed):
            # token无效或认证失败时，返回None允许匿名访问
            return None
        except Exception:
            # 其他异常也允许匿名访问
            return None
