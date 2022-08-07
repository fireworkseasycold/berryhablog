# Generated by Django 3.2.14 on 2022-07-22 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Face_img',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pic_name', models.CharField(max_length=128, null=True, verbose_name='图名')),
                ('face_url', models.ImageField(max_length=128, upload_to='uface', verbose_name='上传后图片存放的路径')),
                ('uploaded_time', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('face_encoding', models.CharField(default=None, max_length=128, null=True, verbose_name='人脸编码')),
                ('user', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.usersdata')),
            ],
            options={
                'verbose_name': '面部图片',
                'verbose_name_plural': '用户面部图片',
                'db_table': 'face_pic',
                'ordering': ['pic_name'],
            },
        ),
    ]
