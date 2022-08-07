# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/4/23 23:34
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : urls.py
# @Software: PyCharm
from django.urls import path

from . import  views

app_name='camerea' #使用二级路由必须项,或者不写此处改为路由分发时使用元组

urlpatterns=[
    path('index/',views.index,name='isloghome'), #这是登录后的主页
    path('show_all_img',views.show_all_img), #查看所有图片数据
    path('show_a_img',views.show_a_img), #查看一个图片数据
    path('upload_img',views.upload_img,name='upload_img'), #上传或者修改图片数据
    path('delete_img',views.delete_img), #删除图片数据
    path('camera',views.camera,name='face_rec'), #人脸识别
]