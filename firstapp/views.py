import csv
import os
import time

from celery import shared_task
from django.conf import settings
from django.core.cache import caches, cache
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import json
import redis
from django.urls import reverse
from django.db import connection
from django.views.decorators.cache import cache_page

from blog.models import Note #这里红色警告不是错

def firstapp_index(request):
    if request.method == 'GET':
        # print('url地址', request.get_full_path())
        # print(request.path_info)
        return render(request, 'firstapp/firstapp_index.html')


def testcontext(request):
    afterwords = '这是后端传递的测试消息'
    return render(request, 'firstapp/testcontext.html', context={'beforewords': afterwords})  # context格式为字典


def mycal(request):
    """
    计算器(模板的if标签{% if %}使用案例)
    :param request:
    :return:
    """
    if request.method == "GET":
        return render(request, 'firstapp/mycal.html')
    elif request.method == "POST":
        x = int(request.POST['x'])
        y = int(request.POST['y'])
        op = request.POST['op']
        result = 0
        if op == 'ad':
            result = x + y
            print(result)
        elif op == 'sub':
            result = x + y
        elif op == 'mul':
            result = x * y
        elif op == 'div':
            result = x / y
        # dic={'x':x,'y':y,'op':op}
        # 数据太多时直接使用python内置的locals()将函数里的变量封装为字典
        return render(request, 'firstapp/mycal.html',locals())

def sayhi():
    return 'hahaha'
class Apple():
    def pr(self):
        return 'apple'
def tem_filter(request):
    """模板过滤器，在变量输出时候对变量值进行处理从而改变输出显示
    {{变量|过滤器1：'参数值1'|过滤器2：'参数值2'...}}
    """
    dic={}
    dic['str']='hhh'
    dic['lst']=['a','b','c']
    dic['dict']={'a':1,'b':2}
    dic['func']=sayhi #传函数无括号
    dic['class_obj']=Apple()
    dic['script']='<script>alert(1111)</script>'
    return render(request,'firstapp/tem_filter.html',dic)


def testjson(request):
    json_obj1 = {
        "code": None,
        "data": None
    }
    json_obj1["code"] = "这是json数据1"
    json_obj1["data"] = "测试完成"

    # return HttpResponse(json.dumps(json_obj1))
    # {"code": "\u8fd9\u662fjson\u6570\u636e1", "data": "\u6d4b\u8bd5\u5b8c\u6210"}
    return HttpResponse(json.dumps(json_obj1,ensure_ascii=False),content_type="application/json,charset=utf-8")
    # {"code": "这是json数据1", "data": "测试完成"}

    # 如果不是字典对象，需要序列化来教将QuerySet变json字符串
    # from django.core import serializers
    # js_str = serializers.serialize('js', QuerySet)
    # return HttpResponse(js_str)
    #前端json序列化：json字符串=JSON.stringify(json对象)
    #前端反序列化：json对象=JSON.stringify(json字符串)


def testjsonresponse(request):
    json_obj2 = {
        "code": "这是json数据2",
        "data": "测试完成"
    }
    return JsonResponse(json_obj2,safe=False) #默认content_type="application/json,charset=utf-8"
    # safe=False用于序列化非字典结构对象，否则TyperError
    # {"code": "\u8fd9\u662fjson\u6570\u636e1", "data": "\u6d4b\u8bd5\u5b8c\u6210"}




def testajax(request):
    """
    在不重新加载页面的情况下，,xhr（ 异步对象）,对页面进行局部的刷新。
    这里是点击按钮发送ajax请求至后端来获取数据
    """
    if request.method == "POST":
        i3 = int(request.POST.get('i1')) + int(request.POST.get('i2'))
        print(i3)
        return HttpResponse(i3)
    return render(request,'firstapp/testajax.html')


def setcookies(request):
    """
    设置和修改cookie
    :param request:
    :return:
    """
    resp = HttpResponse('SET cookie is ok')
    resp.set_cookie('gly', 't', 500)  # 名，默认值，过期时间s
    return resp


def getcookies(request):
    # 测试获取cookies，实际服务端通过请求头得知，开发者工具请求头可以看到cookie所有的键值对
    value = request.COOKIES.get('gly', 't')
    return HttpResponse('获取的cookies是%s' % (value))


def delcookies(request):
    """
    删除cookie
    :param request:
    :return:
    """
    resp = HttpResponse('删除cookie-OK')  # 需要先实例化HttpResponse
    resp.delete_cookie('gly')  # 不能直接使用HttpResponse.set_cookie/delete_cookie,会报错缺少self
    return resp


def setsession(request):
    """
    设置session
    :param request:
    :return:
    """
    request.session['uname'] = 'gly3'
    request.session.set_expiry(86400)  # 设置过期时间或者在settings改
    return HttpResponse('set session is ok')


def getsession(request):
    """
    获取session
    :param request:
    :return:
    """
    value = request.session['uname']
    return HttpResponse('session value is %s' % (value))


"""
session存在django_session表，默认不删除：执行python manage.py clearsessions删除过期session
"""


def delsession(request):
    """
    删除session
    :param request:
    :return:
    """
    # 方法1 清除session数据，在存储中删除session的整条数据
    print('开始删除session')
    request.session.flush()
    # 方法2 删除session中的指定键及值，在存储中只删除某个键及对应的值。
    # del request.session['uname']
    try:
        value = request.session['uname']
    except Exception as e:
        res = HttpResponse('session已经删除： %s' % (e))
        return res
    return HttpResponse('session删除失败')


def url_test(request):
    """
    模板中使用url反向解析,不带参数，优点在于路由变化后模板视图不需要跟着改
    :param request:
    :return:
    """
    return render(request, 'firstapp/url_test.html')


def url_test2(request,  p1, p2):
    """
    url传参
    测试 127.0.0.1:8000/firstapp/url_test2/p1/p2
    假如输入127.0.0.1:8000/firstapp/url_test2/ttt/666
    :param request:
    :param age:
    :return:
    """
    # p1,p2不需要用GET.get, 或者POST.get的方式获取,直接用就可以了
    return HttpResponse("url带参数测试success:{},{}".format(p1, p2))


def url_test3(request):
    """
    视图中使用url反向解析
    302跳转
    """
    # reverse('别名',args=[],kwargs={})
    # 不带参数跳转index http://127.0.0.1:8000/index
    # url=reverse('index')
    # 关键字传参 http://127.0.0.1:8000/firstapp/url_test2/1/
    url = reverse('firstapp:t2', kwargs={"age": 1})
    return HttpResponseRedirect(url)

def test_pymsql(request):
    """ 引入PyMySQL模块
    创建连接对象
    使用连接对象创建游标对象
    准备需要使用的sql语句
    使用游标对象执行sql语句(如果是数据修改的操作, 会返回受影响的行数)
    如果执行语句是查询操作, 需要使用游标对象获取查询结果
    关闭游标对象
    关闭连接对象
    可参考http://www.zzvips.com/article/201157.html
    """
    # 创建一个连接对象
    # with connection.cursor() as cur:
    #     cur.execute('执行SQL语句')
    # 创建一个游标对象 ---> 游标对象是通过连接对象去创建的
    cur = connection.cursor()
    # 准备sql语句
    #查
    my_sql_example = "select * from users;"
    # 执行sql语句  ----> 通过游标对象去执行sql
    cur.execute(my_sql_example)
    # 查看sql语句的执行结果  ---> 通过游标对象去查看
    # cur.fetchone()  # 取第一条
    data = cur.fetchall()  # 查看全部

    connection.commit()
    # 关闭游标和连接对象
    cur.close()
    connection.close()
    return HttpResponse(data)

def test_redis(request):
    """测试redis,来源pip install redis；这是方式1，使用redis
    django默认不支持redis缓存，只能用django-redis.py
    参考http://t.zoukankan.com/wsongl-p-14463782.html"""
    # POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, password='123456', max_connections=1000, db=0)
    # conn = redis.Redis(connection_pool=POOL)
    ip='127.0.0.1'
    password = '123456'
    db=0 #指定数据库
    #创建数据库连接对象
    #我们在连接/花费外界资源的时候一定要注意使用try
    try:

        rs=redis.Redis(host=ip,port=6379,password=password,db=db)  #如果连接的是云服务器也可以不指定IP和端口
        # 操作string
        # 添加set key value
        #str
        rs.set('name', 'itcast')
        rs.set('l1', '666')
        k=rs.keys('*') #字节串b'name'
        print(k) #[b'name', b'l1']
        # list
        # rs.lpush('tlist','p','v','a') #从左插入key'tlist'
        # print(rs.lrange('tlist',0,-1))#[b'a', b'v', b'p']，最后插入的在左侧头部n-》【n,n2,n1】
        # rs.linsert('tlist','before','v','g')
        # print(rs.lrange('tlist', 0, -1)) #[b'a', b'g', b'v', b'p']
        # rs.flushall()#清空所有
        return HttpResponse('redis ok')
    except Exception as e:
        return HttpResponse('redis失效')


def test_djredis(request):
    """settings需要配置redis缓存
    参考http://t.zoukankan.com/wsongl-p-14463782.html
    https://zhuanlan.zhihu.com/p/415541680
    """
    from django.core.cache import cache
    cache.set('key', "python的任意对象", 5)  # 5秒之后删除

    from django_redis import get_redis_connection
    conn = get_redis_connection('default')
    res = conn.get('name')
    print(res)
    return HttpResponse(res)



def test_page(request):
    """
    分页测试,带?...查询字符串
    :param request:  #http://127.0.0.1:8000/test_page/?page=xxx
    :return:
    """

    bks=['a','b','c','d','e'] #需要分页的数据
    paginator=Paginator(bks,2)  #每页两条

    cur_page=request.GET.get('page',1) #得到擦查询字符串page,没有则1
    page=paginator.page(cur_page)  #每页的数据(只不过这里是分页分出的两条)

    return render(request,'firstapp/test_page.html',locals())

def make_csv(request):
    """下载文件 text/csv"""
    #http://127.0.0.1:8000/firstapp/make_csv?page=xxx
    #分页
    all_aiticles = Note.objects.all()
    # for i in all_aiticles:
    #     print(i)
    #初始化paginator 对象
    paginator = Paginator(all_aiticles, 3)
    #初始化 具体页码的 page 对象
    page_num = request.GET.get('page',1)
    c_page = paginator.page(page_num)

    #更改响应头的Content-Type,浏览器遇到如下响应头.弹出另存框
    response = HttpResponse(content_type='text/csv')
    # 通过 User-Agent 判断客户端系统，然后设置带 BOM 的编码 ,没有则csv打开乱码 https://blog.csdn.net/q965844841qq/article/details/119065251
    response.charset = 'utf-8' if "Windows" in request.headers.get('User-Agent') else 'utf-8'
    #添加 另存为 响应头
    response['Content-Disposition'] = 'attachment;filename="all_aiticles.csv"'
    #初始化 csv writer
    writer = csv.writer(response)
    #写表头
    writer.writerow(['id', 'title']) #取两个字段
    #写具体内容
    for b in c_page:  #写入分页的当前页内容
        writer.writerow([b.id, b.title])
        print(b.id, b.title)
    return response



def test_upload(request):
    if request.method=='GET':
        return render(request,'firstapp/test_upload.html')
    elif request.method=='POST':
        # 处理上传文件
        my_file=request.FILES['myfile']

        # 生成文件路径
        filename=os.path.join(settings.MEDIA_ROOT,my_file.name)
        with open(filename,'wb') as f:
            data=my_file.file.read()
            f.write(data)
        return HttpResponse('接收成功 文件为%s'%(my_file.name))
# 成功后可在http://127.0.0.1:8000/settings.MEDIA_ROOT/my_file.name打开文件 ,需要先配置media路由

from django.core import mail
def test_qqemail(request):
    mail.send_mail(
        subject="邮箱测试",  # 题目
        message="邮箱测试发送内容",  # 消息内容
        from_email="1476094297@qq.com",  # 发送者[当前配置邮箱]
        recipient_list=['1476094297@qq.com'],  # 接收者邮件列表
    )
    return HttpResponse('发送成功')

def show_bootstrap(request,number):
    """
    http://localhost:8000/firstapp/show_bootstrap/任意整数/
    :param request:
    :param number:
    :return:
    """
    html="firstapp/bootstrap{}.html".format(number)
    return render(request,html)

from mysite.settings import LOGGING #LOGGING红色警告不管他
import logging

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('django.request')

def testmylog(request):
    """自定义日志,参考https://www.dusaiphoto.com/article/68/"""
    # do something
    logger.warning('这是自定义日志测试!')
    # do something else
    return HttpResponse('这是自定义日志测试')

#使用个整体缓存，后续有使用协商缓存
@cache_page(15) #发现15秒后才改变
def testcache1(request):
    t=time.time()
    return HttpResponse(t)



def testcache2(request):
    # 局部缓存引入cache对象的两种方式，差别在s
    # 方式1使用caches['CACHE配置key']导入具体对象
    # cache1 = caches['myalias1']
    # cache2 = caches['myalias2']
    # 方式2相当于直接引入CACHES配置项中的default项(只有default)
    # content = cache.get('index_data')
    # articles = Note.objects.all()[:6]
    # 在django manage.py shell 里测试很方便
    # cache.set(key,value,timeout) #存
    # cache.get(key) #取
    #cache.add(key,value) #存，只在key不存在时候生效，返回True/False
    # cache.get_or_set(key,value,timeout)#如果没有则set，返回值value
    # cache.set_many(dict,timeout)#批量存，返回插入不成功的key数组
    # cache.get_many(key_list) #批量取
    # cache.delete(key) #删除 返回None
    # cache.delete_many(key_list) #批量删除 返回None

    cache.set('tcache2', 'tcache2', 30)
    if cache.get('tcache2'):
        t=cache.get('tcache2')
    else:
        t='缓存无'

    return HttpResponse(t)





