# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/8/5 10:12
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : views.py
# @Software: PyCharm
import time

from celery import shared_task  #异步
from django.core.cache import caches,cache
from django.http import HttpResponse

from django.shortcuts import render,redirect


#ip端口 127.0.0.1:8000  实际http://localhost:8000/
# apache部署配置后 ip+自定义端口，nginx反向代理apache
from django.views.decorators.cache import cache_page

from blog.models import Note





#ip端口+index 127.0.0.1:8000/index


def index(request):
    """
    这是普通使用局部缓存加载使用模板的
    :param request:
    :return:
    """
    articles=cache.get('index')
    if articles:
        # print('使用缓存')
        return render(request, "homepage/index.html", locals()) #context must be a dict rather than QuerySet.
    else:
        articles = Note.objects.all()[:6]
        cache.set('index',articles,15)
        # print(locals())
        return render(request, "homepage/index.html", locals())





def tt(request):
    #样式测试
    return render(request,'base2.html')

#http://127.0.0.1:8000/hello/数字/任一文字
def hello(request, age, name, **kwargs):
    if kwargs['key']:
        print(kwargs['key'])
    return HttpResponse('%d岁的%s, 正在学习Django'%(age, name))




