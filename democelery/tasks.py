# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/7/28 3:15
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : task.py
# @Software: PyCharm
from democelery.models import Widget

from celery import shared_task


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task
def count_widgets():
    return Widget.objects.count()


@shared_task
def rename_widget(widget_id, name):
    w = Widget.objects.get(id=widget_id)
    w.name = name
    w.save()