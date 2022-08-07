from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Usersdata(models.Model):
    """用户表"""
    #使用二元分组
    user_sex=(
        ('m','男'),
        ('w','女')
    )
    #第一个元素是要存入database的数据，第二个元素是admin的界面显示的数据。
    username = models.CharField(max_length=128, verbose_name='用户名',unique=True) #唯一
    password = models.CharField(max_length=256, verbose_name='密码')
    sex = models.CharField(max_length=1, choices=user_sex, verbose_name='性别', default='m')
    email = models.EmailField(verbose_name='邮箱', unique=True) #唯一
    ip = models.CharField(max_length=128, verbose_name='IP地址')
    profile = models.CharField(max_length=50, verbose_name=' 简介', default='该用户没有简介')
    tx=models.ImageField(upload_to='uploads/tx/%Y/%m/%d',verbose_name='用户头像',default='uploads/tx/tx.jpeg')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)


    objects = models.Manager()  #防止views里使用models.Usersdata.objects进行orm操作不提示并且报淡黄色

    #使用__str__魔法函数帮助djangoshell中人性化显示对象信息；
    # 使用方法python manage.py shell可以进行查看;
    # 或者登录djanngo后台表里查看每条数据的显示样式
    def __str__(self):
        return "用户:%s"%(self.username) #使用__str__方法修改print（此类的实例化对象）的默认输出



    class Meta: #忘记怎么用记得去查这个类的所有属性
        ordering=['username'] #按照人名升序排序
        # ordering=['-username'] #按照人名降序排序
        # ordering=['？username'] #按照人名随机排序
        db_table='users' #设置表名，比如改为uu，admin里表就叫uu
        #verbose_name指定在admin管理界面中显示中文；
        # verbose_name表示单数形式的显示，
        # verbose_name_plural表示复数形式的显示；
        # 中文的单数和复数一般不作区别。
        verbose_name='用户' #指定模型类名字
        verbose_name_plural=verbose_name #指定模型类名字（复数）

# class Usersdata(AbstractUser):
#     user_sex = (
#                 ('m','男'),
#                 ('w','女')
#             )
#     sex = models.CharField(max_length=1, choices=user_sex, verbose_name='性别', default='m')
