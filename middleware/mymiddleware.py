import re
import time

from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

class MyMW(MiddlewareMixin):
    def process_request(self,request):
        # 进入url主路由前 调用此方法
        #None正常返回
        #HttpResponse跳出django直接返回响应
        print('---MyMW process_request')
        return

    def process_view(self,request,callback,callback_args,callback_kwargs):
        # 通过主路由后 进入视图前 调用
        print('---MyMW process_view')

    def process_response(self,request,response):
        # 通过视图函数,响应给用户浏览器之前调用
        # 必须返回 HttpResponse对象
        print('---MyMW process_response')
        return response

class MyMW2(MiddlewareMixin):
    def process_request(self,request):
        # 进入url主路由前 调用此方法
        print('---MyMW2 process_request')

    def process_view(self,request,callback,callback_args,callback_kwargs):
        # 通过主路由后 进入视图函数前 调用
        print('---MyMW2 process_view')

    def process_response(self,request,response):
        # 通过视图函数,响应给用户浏览器之前调用
        # 必须返回 HttpResponse对象
        print('---MyMW2 process_response')
        return response


class VisitLimit(MiddlewareMixin):
    '''此中间件限制一个IP地址对应的总访问/test开头 的次数不能改过10次,超过后禁止使用'''
    visit_times = {}  # 此字典用于记录客户端IP地址有访问次数
    def process_request(self, request):
        ip_address =request.META['REMOTE_ADDR']  # 得到IP地址
        time_start = time.time() # 记录第一次开始时间
        #/test开头的地址都要限制
        if not re.match('^/test',request.path_info):
            return #return在不带参数的情况下默认返回None
        times =self.visit_times.get(ip_address, 0)
        print("IP:", ip_address, '已经访问过', times, '次!:')
        self.visit_times[ip_address] =times + 1
        if times < 10:
            return
        time_end = time.time()
        return HttpResponse('你已经访问过'+ str(times) + '次，您被禁止了')

#对使用 rest_framework 框架的项目来说，可以使用框架的设置来对api的访问频率进行限制settings的REST_FRAMEWORK
# 使用middleware中间件来限制IP频率
class OverTime(MiddlewareMixin):
    """
    限制访问频率
    """
    def process_request(self, request):
        # 获取客户端IP地址
        IP = request.META.get('REMOTE_ADDR')
        # 获取该IP地址的值，如果没有，给一个默认列表[]
        lis = request.session.get(IP, [])
        # 获取当前时间
        curr_time = time.time()
        # 判断操作次数是否小于3次
        if len(lis) < 3:
            # 如果小于3次,添加本次操作时间
            lis.append(curr_time)
            # 保存
            request.session[IP] = lis
        else:
            # 如果本次操作时间减去第一次操作时间小于2秒,则不让其继续操作
            if time.time() - lis[0] < 3:
                return HttpResponse('操作过于频繁,请稍后再试')
            else:
                # 如果大于2秒则交叉复制
                lis[0], lis[1], lis[2] = lis[1], lis[2], time.time()
                # 保存
                request.session[IP] = lis

    def process_response(self, request, response):
        return response






# 通过装饰器进行用户认证非常方便,但是在添加部分需要认证的功能时,就需要再次添加装饰器,
# 如果通过中间件来实现,就不需要再进行添加的操作.
#根据需要自行修改
class MyLogin(MiddlewareMixin):
    def process_request(self, request):
        LOGIN_URL = 'users/login/'
        # 获取当前页面的路由
        url = request.get_full_path()
        path = request.path
        print(path)
        # 通过session判断是否登录
        is_login = request.session.get('is_login')
        # 判断当前页面是否是login页面
        if not re.match(path, LOGIN_URL):
            if not is_login:
                # 如果没有登录，重定向到login页面
                return redirect('users/login/?next=%s' % url)

    def process_response(self, request, response):
        return response
