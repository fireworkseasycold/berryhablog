# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2022/7/28 21:41
# @Author : firworkseasycold
# @Email : 1476094297@qq.com
# @File : tasks.py
# @Software: PyCharm

#任务函数
import re
import time

from celery import shared_task
from django.core import mail

from mysite.settings import EMAIL_HOST_USER

@shared_task
def send_pwd_email(ran_str_pwd='',to_email=''):
    subject = "密码重置邮件"
    message="用户您好，您的新随机登录密码是: {} ,请按照大小写输入空格间的6位内容进行登录".format(ran_str_pwd)
    receiver=[to_email]
    sender=EMAIL_HOST_USER
    mail.send_mail(
    subject=subject,  # 题目
    message=message,  # 消息内容
    from_email=sender,  # 发送者[当前配置邮箱]
    recipient_list=receiver,  # 接收者邮件列表
    )

#https://www.celerycn.io/ru-men/celery-chu-ci-shi-yong
#http://www.zzvips.com/article/193441.html
#运行celery:http://www.zzvips.com/article/193441.html
#完整命令celery worker --help
#开发和测试环境下启动django服务后需要命令行 --loglevel=info代表 -l INFO
# celery -A mysite worker -l INFO -P eventlet
# 关闭后会退出
#生产环境下使用守护进程
#https://docs.celeryq.dev/en/latest/getting-started/next-steps.html#next-steps
# 您需要在后台运行 worker，在daemonization tutorial：https://docs.celeryq.dev/en/latest/userguide/daemonizing.html#daemonizing中有详细描述。
#守护程序脚本使用celery multi命令在后台启动一个或多个 worker：
# celery multi start w1 -A mysite worker -l INFO -P eventlet --logfile = celerylog.log --pidfile = celerypid.pid
# 停止stop替换start;stopwait 以确保在退出之前完成所有当前正在执行的任务