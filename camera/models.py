from django.db import models

# Create your models here.

class Face_img(models.Model): #从表
    pic_name = models.CharField(max_length=128, verbose_name='图名', null=True)
    face_url=models.ImageField(upload_to="uface",max_length=128,verbose_name='上传后图片存放的路径')
    #如果upload_to这个子目录文件夹不存在则自动创建（必须使用django自带上传）
    # 如果在settings指定MEDIA_ROOT，可以不需要指定upload_to作为子目录名，他会自动的将文件上传到MEDIA_ROOT的目录下,如果都有，则MEDIA_ROOT+upload_to
    #不使用Face_img.objects.create的话，使用data.save插入upload_to自动创建子目录会失效
    uploaded_time=models.DateTimeField('上传时间',auto_now_add=True)
    updated_time=models.DateTimeField('更新时间',auto_now=True)

    # # 建立外键一对一，使用级联删除和修改
    #在django的ORM中定义ForeignKey时必需要传递的参数是to和on_delete，其他参数为选填，下面我们来解释一下这些参数：
# 　　　　to：需要传递被外键连接的主表模型作为值，如果连接时主表模型还没定义，建议使用主表模型类名加上""，这样就不会报错
# 　　　　on_delete:需要传递当主表中的一条数据删除时，从表中与这条数据相关联的数据要执行怎样的动作，注意这个参数定义的是主表上的一条数据删除时从表上与之关联的数据的动作(如果是从表上的这条数据删除则与主表上的数据无关)

    # 使用app_name.class_name的方式
    user = models.OneToOneField('users.Usersdata', on_delete=models.CASCADE,default=None,null=True)

    face_encoding=models.CharField(max_length=128,verbose_name="人脸编码",default=None,null=True)
    objects = models.Manager() #防止实例化时objects黄色警告和失败 Face_img.objects，想要用默认的管理器objects,这里要声明出来才可使用

    #使用__str__魔法函数修改默认在print和d'jang'oadmin中的每个数据的显示格式
    def __self__(self):
        return "图名:%s,图片:%s，用户：%s"%(self.pic_name,self.face_url,self.user)

    @classmethod #使用不需要实例化的类方法
    def get_all(cls):
        return cls.objects.all()



    class Meta:
        db_table='face_pic' #数据库里的表名
        ordering=['pic_name']  #以pic_正排序
        verbose_name = '面部图片'  # 指定模型类名字
        verbose_name_plural = '用户面部图片'  # 指定模型类名字（复数表时用）


