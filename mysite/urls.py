"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path,include #include为新添加内容,进行路由分发
from . import views

from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [


    path('admin/', admin.site.urls),
    path('',views.index,name='index'),  #首页
    #表示之匹配 index 开头，并且index结尾的路径，等同上一个，使用re_path写法
    # re_path(r'^index/$', views.index, name='index'),#只有re_path可使用正则
    path('tt',views.tt,name='tt'),
    path('hello/<int:age>/<name>/', views.hello, {'key': "val"}), #路由参数传递示例，将int,age,key直接给后端
    #这里使用路由分发
    # 如果使用命名空间有问题:原因在app下的url.py要加app_name='';或者必须将include第⼀个参数设置为元组类型
    # 路由分发作用当一个项目中包含多个app，每个app中都有命名相同的标识符时，例如index，能够使每次访问都能得到想要的结果（访问指定变量）
    # path('firstapp/',include('firstapp.urls',namespace='firstapp')),
    path('firstapp/',include(('firstapp.urls','firstapp'),namespace='firstapp')), #这里使用元组来应对命名空间,测试用
    path('camera/',include('camera.urls',namespace='camera')), #测试用

    path('users/',include('users.urls',namespace='users')),
    path('blog/',include(('blog.urls','blog'),namespace='blog')),
    re_path('mdeditor/', include('mdeditor.urls')),
    path('comment/',include(('comment.urls','comment'),namespace='comment')),
    path('democelery/',include(('democelery.urls','democelery'),namespace='democelery')),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) #这是配置上传的文件路径
