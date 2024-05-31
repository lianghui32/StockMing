from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from stock_all.utils.code import check_code
from io import BytesIO


def image_code(request):
    """ 生成图片验证码 """
    # 调用pillow函数,生成图片
    img, code_string = check_code()

    # 写入到自己的session中,以便于后续获取验证码再进行校验
    request.session['image_code'] = code_string
    # 给session设置 86400s 超时
    request.session.set_expiry(86400)

    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # 验证码校验
        user_input_code = request.POST['code']
        image_code = request.session.get('image_code', "")
        print("user_input_code={}, image_code={}".format(user_input_code, image_code))
        # 检查任何一个字段是否未填写（即等于None）
        if not all([username, password, user_input_code]):
            # 如果有字段未填写，返回错误信息
            error_message = '请确保所有字段都已填写。'

        elif len(username) < 2 or len(username) > 10:
            error_message = '用户名长度必须在2到10个字符之间'
        elif len(password) < 4 or len(password) > 20:
            error_message = '密码长度必须在4到20个字符之间'

        else:
            if image_code.upper() == user_input_code.upper():
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('/home')
                else:
                    error_message = '用户名或密码错误'
            else:
                error_message = '验证码错误'

        return render(request, 'registration/login.html', {'error_message': error_message})

    return render(request, 'registration/login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user_input_code = request.POST['code']
        image_code = request.session.get('image_code', "")
        print("user_input_code={}, image_code={}".format(user_input_code, image_code))
        # 检查任何一个字段是否未填写（即等于None）
        print('username:', username, 'password:', password, 'confirm_password:', confirm_password, 'user_input_code:',
              user_input_code)
        if not all([username, password, confirm_password, user_input_code]):
            # 如果有字段未填写，返回错误信息
            error_message = '请确保所有字段都已填写。'
            return render(request, 'registration/register.html', {'error_message': error_message})
        else:
            # 验证码校验
            if image_code.upper() == user_input_code.upper():
                # 用户名与密码长度验验证
                if len(username) < 2 or len(username) > 10:
                    error_message = '用户名长度必须在2到10个字符之间'
                elif len(password) < 4 or len(password) > 20:
                    error_message = '密码长度必须在4到20个字符之间'
                elif password != confirm_password:
                    error_message = '两次输入的密码不匹配'
                # 检查用户名是否已经存在
                elif User.objects.filter(username=username).exists():
                    error_message = '用户名已存在'
                else:
                    # 创建新用户
                    user = User.objects.create_user(username=username, password=password)
                    # login(request, user)  # 注册成功后自动登录
                    return redirect('/login/')  # 注册成功后重定向到登录页面
            else:
                error_message = '验证码错误'

        return render(request, 'registration/register.html', {'error_message': error_message})

    return render(request, 'registration/register.html')


def logout_view(request):
    logout(request)
    return redirect('/login')  # 退出登录后重定向到登录页面
