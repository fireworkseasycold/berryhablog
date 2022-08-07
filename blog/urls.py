# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/7/3 13:07
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : urls.py
# @Software: PyCharm
from django.urls import path
from . import views

# app_name="blog" #参看主路由分发是否需要

urlpatterns=[
    path('note_index',views.note_index,name='note_index'), #显示所有博客，可以根据？指定
    path('detail/<int:id>',views.note_detail,name='note_detail'),
    path('add',views.add_note,name='add_note'),
    path('delete/<int:id>',views.delete_note,name='delete_note'),
    path('update/<int:id>',views.update_note,name='update_note'),
    # path('searchtag/<int:id>',views.searchtag,name='search_tag'),
]