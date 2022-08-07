from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db import models

# Create your models here.
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from blog.models import Note
from users.models import Usersdata

#这些是mdtt
#单级评论
class Comment(models.Model):
    article = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='评论文章'
    )
    comment_author  = models.ForeignKey(
        Usersdata,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='评论者'
    )
    comment_content  = models.TextField(verbose_name='评论内容')
    comment_time  = models.DateTimeField(auto_now_add=True,verbose_name='评论时间')
    pre_comment=models.ForeignKey('self',on_delete=models.DO_NOTHING,null=True,verbose_name='父评论id',blank=True)  #父级评论，如果没有父级则为空NULL, "self"表示外键关联自己)

    class Meta:
        db_table = 'comment_tb'
        verbose_name = '评论'
        verbose_name_plural = verbose_name

    # def __str__(self):
    #     return self.body[:20]

# # 替换 models.Model 为 MPTTModel
# class Comment(MPTTModel):
# # """一律1,0"""
#     article = models.ForeignKey(
#         Note,
#         on_delete=models.CASCADE,
#         related_name='comments'
#     )
#     user = models.ForeignKey(
#         Usersdata,
#         on_delete=models.CASCADE,
#         related_name='comments'
#     )
#     body = models.TextField()
#     created = models.DateTimeField(auto_now_add=True)
#
#
#     def __str__(self):
#         return self.body[:20]
#
#     # 新增，mptt树形结构
#     parent = TreeForeignKey(
#         'self',
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True,
#         related_name='children'
#     )
#
#     # 新增，记录二级评论回复给谁, str
#     reply_to = models.ForeignKey(
#         Usersdata,
#         null=True,
#         blank=True,
#         on_delete=models.CASCADE,
#         related_name='replyers'
#     )
#
#     # 替换 Meta 为 MPTTMeta
#     # class Meta:
#     #     ordering = ('created',)
#     class MPTTMeta:
#         order_insertion_by = ['created']

