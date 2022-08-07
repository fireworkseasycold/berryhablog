from django.db import models

# Create your models here.
from django.urls import reverse
from django.utils import timezone
from mdeditor.fields import MDTextField
from taggit.managers import TaggableManager
#
# class Tag(models.Model):
#     name=models.CharField(max_length=50,verbose_name='标签名',unique=True)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         db_table='tag'
#         verbose_name = '标签表'
#         verbose_name_plural = verbose_name



class Note(models.Model): #(默认的数据库表名appname_classname,blog_note)
    """博客表"""
    objects = models.Manager()
    title = models.CharField('标题', max_length=100)
    desc=models.CharField('简介',max_length=256,default='暂无简介')
    # content = models.TextField('内容')
    content = MDTextField(verbose_name='正文')  # TextField修改为MDTextField
    note_img = models.ImageField(upload_to='uploads/blog/%Y/%m/%d', verbose_name='文章配图', default='uploads/blog/blog.jpeg')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)
    click_num=models.IntegerField(default=0,verbose_name='点击量')
    love_num=models.IntegerField(default=0,verbose_name='点赞量')
    # tag = models.ManyToManyField(to=Tag,verbose_name='标签',blank=True)  #blank用于表单的认证,默认False,true填写表单时允许为空
    # 文章标签
    tags = TaggableManager(blank=True)
    #多对多关系自动生成的关系表 note_tag,也可以指定through='',mysql里note表没有这个字段tag,从note需要note.tag.all()来拿
    user = models.ForeignKey('users.Usersdata', on_delete=models.CASCADE) #一对多

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.title  # print时候会显示为这个内容

    # 新增一个get_absolute_url函数，重定向到详情页
    def get_absolute_url(self):
        return reverse('blog:note_detail', args=[self.id])  #这里id黄色不用管


    class Meta:
        db_table='note'
        verbose_name = '文章表'
        verbose_name_plural = verbose_name


