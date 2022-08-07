import hashlib
import os
import random
import re
import string

from django import forms
from django.db.models import Q
from django.forms import Form, fields, ModelForm
from django.http import HttpResponseRedirect  # HttpResponseRedirect仅可以接收url作为参数传入。
from django.shortcuts import render, HttpResponse, redirect  # redirect可以接收model、view或者url作为参数传入，并返回HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.core import mail

from mysite import settings
from mysite.settings import EMAIL_HOST_USER
from . import models
# from .models import Usersdata #或者写成这样
from tools.my_tool import *  # 这里红色不是错误（标记源根即可解决），tools为项目下与各app包同级别的自建包
from .tasks import send_pwd_email
from blog.models import Note
from camera.models import Face_img


# Create your views here.
class Login(View):
    def get(self, request):
        if request.session.get('userinfo', False):
            return HttpResponseRedirect(reverse('index'))  # 302跳转，使用reverse别名写法
        # 检查Cookies
        userinfo = request.COOKIES.get('userinfo')
        # print(userinfo)
        if userinfo:
            # 回写session
            request.session['userinfo'] = userinfo
            return HttpResponseRedirect(reverse('index'))  # 302跳转，使用reverse别名写法
            # return HttpResponse('已登录2')
        return render(request, 'users/login.html')  # 登陆失败重新渲染登录页面

    def post(self, request):
        useroremail = request.POST['useroremail']
        password = request.POST['password']
        pattern = r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'
        # 使用re库的match方法校验传入的邮箱参数是否合理,是否与表达式匹配
        if re.match(pattern, useroremail) is not None:
            # 是邮箱
            try:
                user = models.Usersdata.objects.get(email=useroremail)
            except Exception as e:
                # print(e)
                # 使用django messages
                messages.error(request, "对不起，您的邮箱地址有误")
                return render(request, 'users/login.html')
        else:
            # 是用户名
            try:
                user = models.Usersdata.objects.get(username=useroremail)
            except Exception as e:
                messages.error(request, "对不起，您的用户名有误")
                return render(request, 'users/login.html')
        # 比对密码
        m = hashlib.md5()
        m.update(password.encode())
        if m.hexdigest() != user.password:
            messages.error(request, "对不起，密码验证失败，请重新输入")
            return render(request, 'users/login.html')
        # session记录会话状态
        request.session['userinfo'] = {"username": user.username, "uid": user.id}
        # print({"uid": user.id})
        # resp = HttpResponseRedirect('/index')
        resp=HttpResponseRedirect(reverse('index'))
        # 如果打勾-则于客户端存cookie【username,uid】,时间3天,cookie是长期数据
        if 'remember' in request.POST:  # 具体看开发者工具网络-载荷里的表单数据有没有remember
            resp.set_cookie('userinfo', {"username": user.username, "uid": user.id}, 3600 * 24 * 3)
        # messages.success(request, "欢迎您")
        return resp


class Register(View):
    """
    注册
    """

    def get(self, request):
        # print('正在访问')
        return render(request, 'users/register.html')

    def post(self, request):
        # print('正在注册')
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        # 1两个密码要保持一致
        if password1 != password2:
            messages.error(request, '两次输入的密码不一致，请重新输入')
            return render(request, 'users/register.html')

        # 优化：密码加盐-哈希算法，给明文，计算出定长的值，一般用md5;应用于密码处理和文件完整性校验
        m = hashlib.md5()
        m.update(password1.encode())  # 传参数必须是字节串，而不能是字符串，所以需要encode
        password_m = m.hexdigest()  # 十六进制数据字符串值
        # password_m=m.digest()#返回二进制数据字符串值
        # 2.邮箱格式是否正确（如果可以建议由前端判断）
        pattern = r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'
        # 使用re库的match方法校验传入的邮箱参数是否合理,是否与表达式匹配
        if re.match(pattern, email) is None:
            # 不是邮箱
            messages.error(request, "对不起，您的邮箱格式有误,请重新输入")
            return render(request, 'users/register.html')

        # 3.当前用户名是否可用 需要orm操作查询
        old_users = models.Usersdata.objects.filter(username=username)
        old_email = models.Usersdata.objects.filter(email=email)
        if old_users:
            messages.error(request, '用户名已注册')
            return render(request, 'users/register.html')
        if old_email:
            messages.error(request, '邮箱已被使用')
            return render(request, 'users/register.html')
        # 4.插入数据【明文处理密码-实际应用需要加密】
        # models.Usersdata.objects.create(username=username,password=password1,email=email)
        # models.Usersdata.objects.create(username=username, password=password_m, email=email)  # 优化：密码使用哈希值
        # 优化 插入问题 解决并发1062报错-使用try
        try:
            user = models.Usersdata.objects.create(username=username, password=password_m, email=email)  # 优化：密码使用哈希值
        except Exception as e:
            # 有可能报错，重复插入（唯一索引并发写入问题）：需要使用redis消息队列进行优化
            # print('--create user error %s' % (e))  # 开发时打印后台查看报错
            # return HttpResponse('注册失败')
            messages.error(request, '系统繁忙，请重新尝试')
            return render(request, 'users/register.html')

        # 优化：注册免登录一天 存入session,服务端，保持会话登录状态一天
        # request.session['username']=username #存入session
        # request.session['uid']=user.id #因为主键查询比唯一索引快，所以可以session可以多存个id来用于查询
        request.session['userinfo'] = {"username": username, "uid": user.id}
        # print(user.id)
        # 修改session存储时间，默认14天 在settings设SESSION_COOKIE_AGE = 86400

        url = reverse('index')
        # print(url) #/index/
        resp = HttpResponseRedirect(url)
        if 'remember' in request.POST:  # 具体看开发者工具网络-载荷里的表单数据有没有remember
            resp.set_cookie('userinfo', {"username": user.username, "uid": user.id}, 3600 * 24 * 3)
        messages.success(request, '登录成功')
        return resp  # 302跳转，使用reverse别名写法

@check_login
def logout(request):
    """
    退出登录
    :param request:
    :return:
    """
    # 删除session
    if 'userinfo' in request.session:
        del request.session['userinfo']
        request.session.flush()  # 删除一条记录包括(session_key session_data expire_date)三个字段
    # 删除cookies
    resp = HttpResponseRedirect('/users/login')  # 302跳转到登录页面
    if 'userinfo' in request.COOKIES:
        resp.delete_cookie('userinfo')
    return resp


@check_login
def delete_user(request,id):
    """注销用户,这里使用get,如果防止csrf攻击,请用post"""
    user = models.Usersdata.objects.get(id=id)  # 获取要删除的对象(id从usersinfo拿到)
    # 从session获取获取当前登录的用户
    uid = request.session.get('userinfo', False).get('uid', False)  # 获取当前登录的用户id
    user_ses = models.Usersdata.objects.get(id=uid)  # 获取当前登录用户对象，这个写法接着delete，可能会报错
    # 判断登录用户和待删除是否一个人
    if user_ses==user:

        logout(request)
        user.delete()
        messages.success(request, "用户已成功注销")
        return HttpResponseRedirect('users:login')
    else:
        return HttpResponse('你没有权限注销用户')


# @check_login
# def usersinfo(request):
#     '''
#     	查看更新修改用户信息
#     	通过POST方法提交表单，修改用户信息
#     	GET方法进入用户信息页面
#     '''
#     # 获取用户对象数据
#     uid = request.session.get('userinfo', False).get('uid', False) #获取当前登录的用户id
#     user = models.Usersdata.objects.get(id=uid)  # 获取当前用户所有信息
#     face_img = Face_img.objects.get(user_id=uid) #获取身份验证图片
#     # 判断用户是否为POST提交表单数据
#     if request.method == "POST":
#         # 获取表单数据
#         username = request.POST['username']  #如果为空会报错MultiValueDictKeyError
#         username = request.POST.get('username','这是我设置的默认值')  #两者等价如果为空不会报错
#         sex = request.POST['sex']
#         email = request.POST['email']
#         password = request.POST['password']
#         # 当前修改的用户名和邮箱是否可用 需要orm操作查询
#         old_users = models.Usersdata.objects.filter(username=username)
#         old_email = models.Usersdata.objects.filter(email=email)
#         if old_users:
#             return HttpResponse('用户名已注册')
#         if old_email:
#             return HttpResponse('邮箱已使用')
#         # 优化：密码加盐-哈希算法，给明文，计算出定长的值，一般用md5;应用于密码处理和文件完整性校验
#         m = hashlib.md5()
#         m.update(password.encode())  # 传参数必须是字节串，而不能是字符串，所以需要encode
#         password_m = m.hexdigest()  # 十六进制数据字符串值
#         # password_m=m.digest()#二进制数据字符串值
#
#         try:
#             #执行保存
#             user.username=username
#             user.sex=sex
#             user.password=password_m
#             user.username=username
#             user.save()
#             # 完成后返回到usersinfo页面
#             # return redirect("user:usersinfo")
#             return HttpResponse('用户信息更新成功')
#         except Exception as e:
#             # 如果数据不合法，返回错误信息
#             return HttpResponse("修改个人信息失败，请重新尝试！或联系管理员")
#     # 如果用户GET请求获取数据
#     else:
#         content = {"user": user, "fontend_face_img":face_img}
#         return render(request, 'users/usersinfo.html', context=content)


# 要在CBV视图中使用我们上面的check_login装饰器，有以下三种方式：
#
# 都要先导入这个方法： from django.utils.decorators import method_decorator
#
# 1. 加在CBV视图的get或post方法上
#
# 2. 加在dispatch方法上
#
# 3. 直接加在视图类上，但method_decorator必须传 name 关键字参数（如果get方法和post方法都需要登录校验的话就写两个装饰器。）

class Usersinfo(View):
    @method_decorator(check_login, name="get")
    # @check_login #在cbv模式下这么写装饰器不生效会有Usersinfo的object没有session报错
    def get(self, request):
        # 查看用户数据
        uid = request.session.get('userinfo', False).get('uid', False)  # 获取当前登录的用户id
        usersdata = models.Usersdata.objects.get(id=uid)  # 获取当前用户所有信息
        content = {"usersdata": usersdata}
        return render(request, 'users/usersinfo.html', context=content)

    @method_decorator(check_login, name="post")
    def post(self, request):
        # 修改用户数据(不包括头像，我设置的跳转至图片上传）
        uid = request.session.get('userinfo', False).get('uid', False)  # 获取当前登录的用户id
        usersdata = models.Usersdata.objects.get(id=uid)  # 获取当前用户所有信息
        # face_img = Face_img.objects.get(user_id=uid)  # 获取身份验证图片
        # 获取表单数据
        # username = request.POST['username']  # 如果为空会报错MultiValueDictKeyError
        username = request.POST.get('username', '这是我设置的默认值')  # 和上面两者等价如果为空不会报错
        sex = request.POST['sex']
        email = request.POST['email']
        password = request.POST['password']
        profile = request.POST['profile']
        tx=request.FILES.get('tx')  #图片上传为type=file
        # 当前修改的用户名和邮箱是否被其他人使用 需要orm操作查询（本人不算），使用q查询，与逻辑 ,使用~ 操作符取反
        old_users = models.Usersdata.objects.filter(Q(username=username) & ~ Q(id = uid))
        old_email = models.Usersdata.objects.filter(Q(email=email) & ~ Q(id = uid))
        if old_users:
            return HttpResponse('用户名已注册')
        if old_email:
            return HttpResponse('邮箱已使用')
        # 优化：密码加盐-哈希算法，给明文，计算出定长的值，一般用md5;应用于密码处理和文件完整性校验
        m = hashlib.md5()
        m.update(password.encode())  # 传参数必须是字节串，而不能是字符串，所以需要encode
        password_m = m.hexdigest()  # 十六进制数据字符串值,m.digest()#二进制数据字符串值
        try:
            # 先删除存储的图片
            # 生成原来的文件路径
            path = os.path.join(settings.MEDIA_ROOT, str(usersdata.tx))
            # print(path)
            if tx != None:
                usersdata.tx = tx
                try:
                    os.remove(path)
                except:
                    messages.error(request,'删除原来的头像图片文件失败，原先图片可能已丢失或不存在,将直接使用新图片')
            # 执行保存至数据库
            usersdata.username = username
            usersdata.sex = sex
            usersdata.password = password_m
            usersdata.username = username
            usersdata.profile = profile
            usersdata.save()
            # 完成后返回到usersinfo页面
            messages.success(request, "修改成功")
            #修改session
            del request.session['userinfo']
            request.session['userinfo'] = {"username": usersdata.username, "uid": usersdata.id}
            return redirect("users:usersinfo")
            # return HttpResponse('用户信息更新成功')
        except Exception as e:
            # 如果数据不合法，返回错误信息
            messages.error(request, "对不起，修改失败，错误原因:{}".format(e))
            # return HttpResponse("修改个人信息失败，请重新尝试！或联系管理员")
            return redirect("users:usersinfo")


# class Reset_passwords(View):
#     #单线程的单步，会容易出问题
#     def get(self,request):
#         #进入重置密码页面
#         return render(request, 'users/reset_passwords.html')
#
#
#     def post(self,request):
#         useroremail = request.POST['useroremail']
#         pattern = r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'
#         # 使用re库的match方法校验传入的邮箱参数是否合理,是否与表达式匹配
#         if re.match(pattern, useroremail) is not None:
#             # 是邮箱
#             try:
#                 user = models.Usersdata.objects.get(email=useroremail)
#             except Exception as e:
#                 # 使用django messages
#                 messages.error(request, '对不起，该邮箱未注册，请重新输入')
#                 return render(request, 'users/reset_passwords.html')
#         else:
#             # 是用户名
#             try:
#                 user = models.Usersdata.objects.get(username=useroremail)
#             except Exception as e:
#                 messages.error(request, "对不起，该用户不存在，请重新输入")
#                 return render(request, 'users/reset_passwords.html')
#
#         # 从a-zA-Z0-9生成指定数量的随机字符，这里指定6位
#         ran_str_pwd=''.join(random.sample(string.ascii_letters + string.digits, 6))
#         # print(ran_str_pwd)
#         mail.send_mail(
#             subject="密码重置邮件",  # 题目
#             message="用户您好，您的新随机登录密码是: {} ,请按照大小写输入空格间的6位内容进行登录".format(ran_str_pwd),  # 消息内容
#             from_email=EMAIL_HOST_USER,  # 发送者[当前配置邮箱]
#             recipient_list=[user.email],  # 接收者邮件列表
#         )
#         # 修改数据库里的用户密码（存入是加盐的，操作如同注册时候）
#         m = hashlib.md5()  # 哈希盐md5
#         m.update(ran_str_pwd.encode())  # 传参数必须是字节串，而不能是字符串，所以需要encode
#         ran_str_pwd_m = m.hexdigest()
#         # print(ran_str_pwd_m)
#         try:
#             user.password = ran_str_pwd_m
#             user.save()
#             messages.success(request,'重置密码已发送您的邮箱，请查收')
#             return render(request, 'users/login.html')
#         except Exception as e:
#             messages.error(request, '抱歉，重置密码失败，请重新尝试或联系我们')
#             return render(request, 'users/reset_passwords.html')
class Reset_passwords(View):
    ##优化：使用异步，防止例如服务器负载较大，或者网络不好服务器进入等待状态，发生阻塞导致停止其他服务

    def get(self,request):
        #进入重置密码页面
        return render(request, 'users/reset_passwords.html')


    def post(self,request):
        useroremail = request.POST['useroremail']
        pattern = r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'
        # 使用re库的match方法校验传入的邮箱参数是否合理,是否与表达式匹配
        if re.match(pattern, useroremail) is not None:
            # 是邮箱
            try:
                user = models.Usersdata.objects.get(email=useroremail)
            except Exception as e:
                # 使用django messages
                messages.error(request, '对不起，该邮箱未注册，请重新输入')
                return render(request, 'users/reset_passwords.html')
        else:
            # 是用户名
            try:
                user = models.Usersdata.objects.get(username=useroremail)
            except Exception as e:
                messages.error(request, "对不起，该用户不存在，请重新输入")
                return render(request, 'users/reset_passwords.html')
        # 从a-zA-Z0-9生成指定数量的随机字符，这里指定6位
        ran_str_pwd=''.join(random.sample(string.ascii_letters + string.digits, 6))
        # print(ran_str_pwd)
        #异步发邮件
        send_pwd_email.delay(ran_str_pwd=ran_str_pwd,to_email=user.email)
        # 修改数据库里的用户密码（存入是加盐的，操作如同注册时候）
        m = hashlib.md5()  # 哈希盐md5
        m.update(ran_str_pwd.encode())  # 传参数必须是字节串，而不能是字符串，所以需要encode
        ran_str_pwd_m = m.hexdigest()
        # print(ran_str_pwd_m)
        try:
            user.password = ran_str_pwd_m
            user.save()
            messages.success(request,'重置密码成功，已发送至您的邮箱，请查收')
            return render(request, 'users/login.html')
        except Exception as e:
            messages.error(request, '抱歉，重置密码失败，请重新尝试或联系我们')
            return render(request, 'users/reset_passwords.html')





class Contactgly(View):
    """联系我们"""
    def get(self,request):
        return render(request, 'users/contact.html')


    def post(self,request):
        username = request.POST['username']
        email = request.POST['email']
        message=request.POST['message']

        pattern = r'^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'
        # 使用re库的match方法校验传入的邮箱参数是否合理,是否与表达式匹配
        if re.match(pattern, email) is not None:
            # 是邮箱
            try:
                user = models.Usersdata.objects.get(email=email)
            except Exception as e:
                # 使用django messages
                messages.error(request, '对不起，该邮箱未注册，请重新输入')
                return render(request, 'users/contact.html')
        try:
            #给管理员发送留言邮件
            mail.send_mail(
                subject="用户:{}的留言,".format(username),  # 题目
                message='留言内容:{},留言邮箱{}'.format(message,email),  # 消息内容
                from_email=EMAIL_HOST_USER,  # 发送者[当前配置邮箱]
                recipient_list=[EMAIL_HOST_USER],  # 接收者邮件列表
            )
            messages.success(request,'留言邮件发送成功,即将前往主页')
            return redirect('index')
        except Exception as e:
            messages.error(request, '抱歉,留言邮件发送失败,请重新尝试或联系我们')
            return render(request, 'users/contact.html')



def introduce(request):
    context= {'gly':'gly'}
    return render(request,'users/introduce.html',context=context)





# def list(request):
#     """
#     http:127.0.0.1:8000/user/delete/?uid=1
#     :param request:
#     :return:
#     """
#     users=models.Usersdata.objects.all()
#     return render(request,'users/users_list.html',locals())

# def delete_user(request):
#     """设计的url:
#     # http:127.0.0.1:8000/users/delete/?uid=1
#     # http:127.0.0.1:8000/users/delete/?uid=2
#     配置path('delete/',views.delete_user,name='delete_user'), #用户个人信息
#     直接使用request.GET.get从url中获取查询字符串内容
#     """
#     uid=request.GET.get('uid')
#     models.Usersdata.objects.filter(id=uid).delete()
#
#     return HttpResponse('删除成功示例')




# 使用d'jang'o组件form实现add用户，从而自动生成html里的标签，这是一种优化方法
class EmpForm(forms.Form):
    name = forms.CharField(min_length=4, label="姓名", error_messages={"min_length": "你太短了", "required": "该字段不能为空!"})
    age = forms.IntegerField(label="年龄")
    salary = forms.DecimalField(label="工资")


def test_form(request):
    if request.method == "GET":
        form = EmpForm()
        return render(request, "users/test_form.html", {"form": form})
    else:
        form = EmpForm(request.POST)
        if form.is_valid():  # 进行数据校验
            # 校验成功
            data = form.cleaned_data  # 校验成功的值，会放在cleaned_data里。
            data.pop('salary')  # 移除salary元素
            print(data)

            # models.Emp.objects.create(**data)
            return HttpResponse(
                'ok'
            )
            # return render(request, "add_emp.html", {"form": form})
        else:
            print(form.errors)  # 打印错误信息
            clean_errors = form.errors.get("__all__")
            print(222, clean_errors)
        return render(request, "add_emp.html", {"form": form, "clean_errors": clean_errors})


# 使用ModelForm组件,比form更好，不需要继续写字段了
# ModelForm适合增删改查,并且有其他功能
class EmpModelForm(ModelForm):
    #原来的字段不需要写了
    # 这里是自定义的字段
    xx = forms.DecimalField(label="工资")

    class Meta:
        model = models.Usersdata  # 等同于继承了Usersdata，不需要自己写字段了
        fields = ["username", "password", "sex", "xx"]  # 这里写要显示的的字段


