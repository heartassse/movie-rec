from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserMeSerializer, AdminUserSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """用户注册"""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})


class CurrentUserView(APIView):
    """返回当前登录用户信息（用于前端判断是否为管理员）。"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ser = UserMeSerializer(request.user)
        return Response(ser.data)
    
    def put(self, request, *args, **kwargs):
        """更新当前用户信息"""
        user = request.user
        data = request.data
        
        # 更新用户名
        if 'username' in data:
            username = data['username'].strip()
            if username and username != user.username:
                # 检查用户名是否已存在
                if User.objects.filter(username=username).exclude(id=user.id).exists():
                    return Response({'username': ['该用户名已被使用']}, status=400)
                user.username = username
        
        # 更新邮箱
        if 'email' in data:
            user.email = data['email'].strip() if data['email'] else ''
        
        # 更新密码
        if 'password' in data and data['password']:
            password = data['password']
            if len(password) < 8:
                return Response({'password': ['密码至少需要8位字符']}, status=400)
            user.set_password(password)
        
        user.save()
        
        ser = UserMeSerializer(user)
        return Response(ser.data)


class AdminUserViewSet(viewsets.ModelViewSet):
    """管理员管理用户的接口，仅管理员可用。

    支持增删改查：/api/auth/admin/users/
    """

    queryset = User.objects.all().order_by("id")
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAdminUser]
