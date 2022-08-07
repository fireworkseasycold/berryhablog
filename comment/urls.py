# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/7/19 16:48
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : urls.py
# @Software: PyCharm
from django.urls import path

from . import views

urlpatterns = [
    path('comment_control/',views.comment_control,name='comment_control'),  #提交评论处理的路由
    # path('post_comment/<int:article_id>',views.Postcomment.as_view(),name='post_comment'), #处理单级别评论
    # path('post_comment/<int:article_id>/<int:parent_comment_id>',views.Postcomment.as_view(),name='comment_reply'),#处理多级别评论
    # 已有代码，处理一级回复
    # path('post_comment/<int:article_id>', views.post_comment, name='post_comment'),
    # # 新增代码，处理二级回复
    # path('post_comment/<int:article_id>/<int:parent_comment_id>', views.post_comment, name='comment_reply'),
    # #个path都使用了同一个视图函数，但是传入的参数却不一样多，仔细看。第一个path没有parent_comment_id参数，因此视图就使用了缺省值None，达到了区分评论层级的目的。
]