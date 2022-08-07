# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/7/19 16:50
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : forms.py
# @Software: PyCharm
from django import forms
from django.contrib.contenttypes.models import ContentType
from ckeditor.widgets import CKEditorWidget
from django.db.models import ObjectDoesNotExist
from django.http import request

from .models import Comment

#
# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['article','comment_author','comment_content','pre_comment']