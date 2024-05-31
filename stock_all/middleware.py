# from django.http import HttpResponseRedirect
# from django.urls import reverse
#
#
# class AuthMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         excluded_paths = ['/image/code/', '/admin/', '/login/', '/register/']
#         if not request.user.is_authenticated and request.path not in [reverse('login'),
#                                                                       reverse(
#                                                                           'register')] and request.path not in excluded_paths:
#             return HttpResponseRedirect(reverse('login'))
#         response = self.get_response(request)
#         return response

from django.http import HttpResponseRedirect
from django.urls import reverse


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 使用reverse()函数获取URL路径
        excluded_paths = [
            reverse('image_code'),
            reverse('login'),
            reverse('register')
        ]
        if not request.user.is_authenticated and request.path not in excluded_paths:
            return HttpResponseRedirect(reverse('login'))
        response = self.get_response(request)
        return response
