# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/7/18 13:16
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : urls.py
# @Software: PyCharm
from django.urls import path,re_path

from . import views

# app_name='firstapp' #使用二级路由必须项

urlpatterns = [
    path('firstapp_index/', views.firstapp_index,name='fir1'),
    path('mycal/',views.mycal),
    path('tem_filter',views.tem_filter),
    path('testjson/', views.testjson),
    path('testjsonresponse/', views.testjsonresponse),
    path('testajax/', views.testajax),
    path('testcontext/', views.testcontext),
    path('setcookies/', views.setcookies),
    path('getcookies/', views.getcookies),
    path('delcookies/', views.delcookies),
    path('setsession/', views.setsession),
    path('getsession/', views.getsession),
    path('delsession/', views.delsession),
    path('url_test/',views.url_test),
    # path('url_test2/<str:p1>/<int:p2>/', views.url_test2,name='t2'),
    # re_path(r'url_test2/(\w+)/(\d+)/', views.url_test2,name='t2'),
    re_path(r'url_test2/(?P<p1>\w+)/(?P<p2>\d+)/', views.url_test2,name='t2'),
    path('url_test3/',views.url_test3),
    path('test_pymsql/', views.test_pymsql),
    path('test_redis/',views.test_redis), #普通redis
    path('test_djredis/',views.test_djredis), #django_redis
    path('test_page/',views.test_page,name='test_page'),  #测试分页
    path('make_csv/',views.make_csv),  #写入csv
    path('test_upload/',views.test_upload),  #上传文件测试
    path('test_qqemail/',views.test_qqemail),  #测试发邮件
    path('show_bootstrap/<int:number>/', views.show_bootstrap),
    path('testmylog/', views.testmylog), #自定义log测试
    path('testcache1',views.testcache1), #装饰器整体缓存
    path('testcache2',views.testcache2)  #局部缓存
]
#注意实际访问是127.0.0.1：8000/firstapp/first_index，一级路由加二级