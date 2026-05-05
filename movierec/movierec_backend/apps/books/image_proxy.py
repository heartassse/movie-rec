"""
图片代理视图：解决豆瓣等网站的防盗链问题
"""
import requests
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def image_proxy(request):
    """图片代理接口：绕过防盗链限制
    
    参数：
    - url: 图片URL（必需）
    
    使用示例：
    /api/books/image-proxy/?url=https://img3.doubanio.com/view/subject/l/public/s1234567.jpg
    """
    
    image_url = request.GET.get('url')
    if not image_url:
        return Response({"detail": "url parameter is required"}, status=400)
    
    # 安全检查：只允许特定域名
    allowed_domains = [
        'doubanio.com',
        'douban.com',
        'img3.doubanio.com',
        'img1.doubanio.com',
        'img2.doubanio.com',
        'img9.doubanio.com',
    ]
    
    if not any(domain in image_url for domain in allowed_domains):
        return Response({"detail": "Domain not allowed"}, status=403)
    
    try:
        # 设置请求头，伪装成正常浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://book.douban.com/',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        }
        
        # 请求图片
        response = requests.get(image_url, headers=headers, timeout=10, stream=True)
        
        if response.status_code != 200:
            return Response({"detail": "Failed to fetch image"}, status=response.status_code)
        
        # 检查返回的内容类型
        content_type = response.headers.get('Content-Type', '')
        
        # 如果返回的不是图片，说明URL失效或被拦截
        if not content_type.startswith('image/'):
            return Response({
                "detail": "URL返回的不是图片（可能已失效）",
                "content_type": content_type,
                "content_length": len(response.content)
            }, status=404)
        
        # 返回图片数据
        django_response = HttpResponse(response.content, content_type=content_type)
        
        # 设置缓存头（减少重复请求）
        django_response['Cache-Control'] = 'public, max-age=86400'  # 缓存1天
        
        return django_response
        
    except requests.Timeout:
        return Response({"detail": "Request timeout"}, status=504)
    except requests.RequestException as e:
        return Response({"detail": f"Request failed: {str(e)}"}, status=502)
    except Exception as e:
        return Response({"detail": f"Server error: {str(e)}"}, status=500)
