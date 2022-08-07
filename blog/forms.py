# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/7/17 10:51
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : forms.py
# @Software: PyCharm
from django import forms
from django.db import models

from .models import Note

# 自定义写文章的表单类
class NoteForm(forms.ModelForm):
    #这里写自定义字段
    class Meta:
        # 指明数据模型来源
        model = Note
        #定义表单包含的字段
        fields = ('title','note_img','tags','content')
        #如果所有
        # fields="__all__"
        #排除字段
        # exclude=["desc"]

    # def xxx(self):
    #     raise ('用 raise 手动引发的异常')



