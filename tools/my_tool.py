# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/7/3 17:47
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : my_tool.py
# @Software: PyCharm

from django.http import HttpResponse, HttpResponseRedirect
from django.core import mail


def check_login(fn):
    """
    检查登录状态装饰器，可也用from django.contrib.auth.decorators import login_required为实现此效果的装饰器
    :param fn:
    :return:
    """
    def wrap(request,*args,**kwargs):
        if "userinfo" not in request.session:
            #再检查Cookies
            c_userinfo=request.COOKIES.get('userinfo')
            if not c_userinfo:
                return HttpResponseRedirect('/users/login')
            else:
                #回写session
                request.session['userinfo']=c_userinfo
        return fn(request,*args,**kwargs)
    return wrap

#登录验证例子，不使用
# def checkLogin(func):
#     def wrapper(request, *args, **kwargs):
#         userinfo = request.session.get('userinfo', False)
#         if userinfo:
#             username = userinfo.get("username", False) #参考dict.get(a,b);userinfo需要设置为dict，存在返回userinfo["username"],否则返回False
#             # print(username)
#             if username:
#                 return func(request, *args, **kwargs)
#         else:
#             return redirect('/users/login')
#     return wrapper
