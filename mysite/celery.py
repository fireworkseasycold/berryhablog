from __future__ import absolute_import, unicode_literals #从未来导入绝对导入，这样我们的 celery.py模块就不会与库发生冲突：必须第一行
import os
from celery import Celery


#https://docs.celeryq.dev/en/latest/django/first-steps-with-django.html#using-celery-with-django
#中文手册https://www.celerycn.io/
# 指定Django默认配置文件模块
from mysite import settings


#设置默认DJANGO_SETTINGS_MODULEcelery命令行程序的环境变量


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# 为我们的项目mysite创建一个Celery实例。这里不指定broker中间容易出现错误。
app = Celery('mysite', broker='redis://127.0.0.1:6379/1',backend='redis://127.0.0.1:6379/1')  #raise errorredis.exceptions.AuthenticationError: Authentication required.



# 这里指定从django的settings.py里读取celery配置
app.config_from_object('django.conf:settings')


# 加载所有 settings下的app中包含的 tasks,自动从所有已注册的django app中加载任务
app.autodiscover_tasks()
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# 用于测试的异步任务
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
