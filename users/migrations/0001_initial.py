# Generated by Django 3.2.14 on 2022-07-22 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Usersdata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=128, unique=True, verbose_name='用户名')),
                ('password', models.CharField(max_length=256, verbose_name='密码')),
                ('sex', models.CharField(choices=[('m', '男'), ('w', '女')], default='m', max_length=1, verbose_name='性别')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='邮箱')),
                ('ip', models.CharField(max_length=128, verbose_name='IP地址')),
                ('profile', models.CharField(default='该用户没有简介', max_length=50, verbose_name=' 简介')),
                ('tx', models.ImageField(default='uploads/tx/tx.jpeg', upload_to='uploads/tx/%Y/%m/%d', verbose_name='用户头像')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
                'db_table': 'users',
                'ordering': ['username'],
            },
        ),
    ]
