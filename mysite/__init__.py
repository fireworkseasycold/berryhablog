from __future__ import absolute_import, unicode_literals
import pymysql
pymysql.install_as_MySQLdb() # 在settings.py同目录下的__init__.py中增加pymsql代码

# coding:utf-8


# 引入celery实例对象,确保项目启动时即加载Celery实例
from .celery import app as celery_app

__all__ = ('celery_app',)