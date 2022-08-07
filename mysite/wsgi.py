"""
WSGI config for mysite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application
# sys.path.append('C:/Apache24/htdocs/mysite')  #如提示无法导入wsgi，可按照示例增加此路径

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

application = get_wsgi_application()
