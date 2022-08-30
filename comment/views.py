from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from blog.models import Note
from tools.my_tool import *
from users.models import Usersdata
# from .forms import CommentForm
from .models import Comment

# class Postcomment1(View):
# # 单级评论
#     @method_decorator(check_login, name="post")
#     def post(self,request,article_id):
#         article = get_object_or_404(Note, id=article_id)
#         # 和Model.objects.get()的功能基本是相同的,如果用户请求一个不存在的对象时,返回404
#         comment_form = CommentForm(request.POST)
#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.article = article
#             new_comment.user = request.user
#             new_comment.save()
#             #返回到一个适当的url中：即用户发送评论后，重新定向到文章详情页面
#             #其参数是一个Model对象时redirect会自动调用这个Model对象的get_absolute_url()方法,自行去model添加
#             return redirect(article)
#         else:
#             return HttpResponse("表单内容有误，请重新填写。")
#     @method_decorator(check_login, name="get")
#     def get(self,request):
#         return HttpResponse("发表评论仅接受POST请求。")
#
# class Postcomment(View):
#     #多级评论新增参数parent_comment_id
#     @method_decorator(check_login, name="post")
#     def post(self,request,article_id,parent_comment_id=None):
#         article = get_object_or_404(Note, id=article_id)
#         # 和Model.objects.get()的功能基本是相同的,如果用户请求一个不存在的对象时,返回404
#         comment_form = CommentForm(request.POST)
#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.article = article
#             new_comment.user = request.user
#
#             #二级回复
#             if parent_comment_id:
#                 parent_comment=Comment.objects.get(id=parent_comment_id)
#                 # 若回复层级超过二级，则转换为二级
#                 new_comment.parent_id = parent_comment.get_root().id
#                 # 被回复人
#                 new_comment.reply_to = parent_comment.user
#                 new_comment.save()
#                 return HttpResponse('200 OK')
#
#             new_comment.save()
#             #返回到一个适当的url中：即用户发送评论后，重新定向到文章详情页面
#             #其参数是一个Model对象时redirect会自动调用这个Model对象的get_absolute_url()方法,自行去model添加
#             return redirect(article)
#         else:
#             return HttpResponse("表单内容有误，请重新填写。")
#     @method_decorator(check_login, name="get")
#     def get(self,request,article_id,parent_comment_id=None):
#         article = get_object_or_404(Note, id=article_id)
#         comment_form = CommentForm()
#         context = {
#             'comment_form': comment_form,
#             'article_id': article_id,
#             'parent_comment_id': parent_comment_id
#         }
#         return render(request, 'comment/reply.html', context)
#
# @check_login
# # 新增参数 parent_comment_id
# def post_comment(request, article_id, parent_comment_id=None):
#     article = get_object_or_404(Note, id=article_id)
#
#     # 处理 POST 请求
#     if request.method == 'POST':
#         comment_form = CommentForm(request.POST)
#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.article = article
#             # new_comment.user = request.user  使用d'jango自带user才可
#             uid=request.session['userinfo'].get('uid')
#             user=Usersdata.objects.get(id=uid)
#             new_comment.user = user
#
#             # 二级回复
#             if parent_comment_id:
#                 parent_comment = Comment.objects.get(id=parent_comment_id)
#                 # 若回复层级超过二级，则转换为二级
#                 new_comment.parent_id = parent_comment.get_root().id
#                 # 被回复人
#                 new_comment.reply_to = parent_comment.user
#                 new_comment.save()
#                 return HttpResponse('200 OK')
#
#             new_comment.save()
#             return redirect(article)
#         else:
#             return HttpResponse("表单内容有误，请重新填写。")
#     # 处理 GET 请求
#     elif request.method == 'GET':
#         comment_form = CommentForm()
#         context = {
#             'comment_form': comment_form,
#             'article_id': article_id,
#             'parent_comment_id': parent_comment_id
#         }
#         return render(request, 'comment/reply.html', context)
#     # 处理其他请求
#     else:
#         return HttpResponse("仅接受GET/POST请求。")

@check_login
def comment_control(request):
    if request.method == 'POST':
        # if request.user.username:
        if request.session.get('userinfo', False):
            comment_content = request.POST.get('comment_content')
            article_id = request.POST.get('article_id')
            pid = request.POST.get('pid')
            print(f"pid:{pid}")
            # author_id = request.user.id  # 获取当前用户的ID
            author_id,author_name=request.session.get('userinfo',False).get('uid',False),request.session.get('userinfo',False).get('username',False)
            # author_id = request.session.userinfo.uid  # 获取当前用户的ID

            a_comment=Comment.objects.create(comment_content=comment_content, pre_comment_id=pid, article_id=article_id,
                                   comment_author_id=author_id)  # 将提交的数据保存到数据库中
            if pid:
                pre_comment_comment=Comment.objects.get(pk=pid).comment_content
            else:
                pre_comment_comment=None
            comment_count=len(Comment.objects.filter(article_id=article_id))  #获取当前文章的评论长度
            result={
                'id':a_comment.pk,
                'comment_content':a_comment.comment_content,
                'pre_comment_id':a_comment.pre_comment_id,
                'pre_comment_comment':pre_comment_comment,
                'article_id':a_comment.article_id,
                'comment_author_id':a_comment.comment_author_id,
                'comment_author_name':author_name,
                'comment_time':a_comment.comment_time,
                'comment_count':comment_count
            }
            print(result)

            # comment_list = list(
            #     Comment.objects.filter(article_id=article_id).values('id', 'comment_content', 'pre_comment_id', 'article_id', 'comment_author_id','comment_time')
            # )  # 以键值对的形式取出评论对象，并且转化为列表list类型article = list()
            # print(comment_list)  #这个写法取不到用户名，

            return JsonResponse(result)  # JsonResponse返回JSON字符串，自动序列化，如果不是字典类型，则需要添加safe参数为False

        else:
            # return redirect('/user_login/')
            return HttpResponse('请先登录')
    # 处理 GET 请求
    else:
        return HttpResponse('评论只接受post')