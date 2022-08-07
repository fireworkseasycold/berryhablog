# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/4/17 17:43
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : urls.py
# @Software: PyCharm
from django.urls import path

from . import views

app_name='users' #使用二级路由必须项

urlpatterns=[
    path('register/',views.Register.as_view(),name='reg'),#注册，增加用户 cbv开发模式
    path("login/", views.Login.as_view(),name='login'),  #登录，cbv开发模式
    path("usersinfo/",views.Usersinfo.as_view(),name='usersinfo'),  #用户个人信息查看和修改

    path('logout/',views.logout,name='islogout'), #登出
    path('delete/<int:id>',views.delete_user,name='delete_user') ,#注销用户
    path('pwd_reset',views.Reset_passwords.as_view(),name='pwd_reset'), #邮件重置密码
    path('contact',views.Contactgly.as_view(),name='contact'), #留言
    path('introduce',views.introduce,name='introduce'), #问题介绍


    # path('register/',views.register,name='reg'),#注册，增加用户
    # path('reg/',views.reg), #注册的第二个写法测试用
    # path('login/',views.login,name='login'), #登录 #fbv开发模式


    # path('usersinfo/',views.usersinfo,name='usersinfo'),
    # path('list/',views.list,name='userslist'), #所有用户列表
    # path('delete/',views.delete_user,name='delete_user'), #删除用户
    path('test_form/',views.test_form), #测试form组件
]