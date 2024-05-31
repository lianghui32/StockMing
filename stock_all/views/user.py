from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def user_view(request):
    user = request.user
    return render(request, 'user_view.html', {'user': user})


@login_required
def user_edit(request):
    user = request.user
    return render(request, 'user_edit.html', {'user': user})


@login_required
def user_save(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        return redirect('/user_view/')  # 保存后重定向到展示页面

    return redirect('/user_edit/')  # 非POST请求重定向到修改页面


@login_required
def change_password(request):
    error_message = None
    success_message = None
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        print(old_password, new_password, confirm_password)
        if not all([old_password, new_password, confirm_password]):
            error_message = '输入不完整，请重新输入。'
            print(error_message)
        else:
            if new_password != confirm_password:
                error_message = '两次新密码不一致，请重试。'
            elif not request.user.check_password(old_password):
                error_message = '原密码不正确，请重试。'
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)  # 更新会话中的认证信息
                success_message = '修改密码成功'
        return render(request, 'change_password.html',
                      {'error_message': error_message, 'success_message': success_message})
    else:
        return render(request, 'change_password.html')
