# berryhablog



[berryha.com](http://101.34.15.153)

### 前后端不分离

环境管理：anaconda
conda create xxxx python=3.6/3.7

pip install django2.2-3.2.14 mdeditor redis(windows项目下有安装包) django-cors-headers pymsql modwsgi celery等等

如果需要modwisgi其他版本的，请自行apache编译生成，步骤可以在我的博客或者我的其他项目中找到whl



### app

users blog comment

其余camera和firstapp为测试，请先在settings内删除

简单使用了redis作为cache数据库缓存并缓存了页面和查询集数据，使用celery执行异步任务

包含登录注册头像修改信息重置密码注销，博客增删改查排序，文章标签，文章评论和回复等功能

可以优化的点：不分离的话使用TemplateView，或者前端重写ajax并使用JsonResponse替换HttpResponse



### 数据

mysql   

项目下包含我迁移数据库的说明文件 数据库的导入导出.txt，使用了django的导入导出和mysql的导入导出

含有原先本地电脑的部分数据库数据

可以优化：根据实际精简model字段长度





### 部署：

腾讯云轻量服务器 windowsserver2012

动静分离

1.静态static/media  ->nginx（自行配置）

2.后端django-> apache（自行配置）

3.nginx->apache

未采用虚拟主机，有需要自己配置

具体参考本项目下的配置文件

如果需要linux部署的，安装uwsgi,替换modwsgi即可，本次是因为ubuntu虚拟机反应10s以上不得以使用windows。

补充了虚拟主机配置

例参考 berryha.com在文章详情页选择gly2的博客

[树莓博客网](thhp://101.34.15.153)

或者我的csdn   fireworkseasycold

本博客后续会进行优化，但更大可能是使用drf重写

欢迎来信留言qq.com 1476094297@qq.com

另外：欢迎小伙伴提供苏州python的后端工作机会

