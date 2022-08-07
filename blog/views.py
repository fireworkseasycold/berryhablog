import json
import re

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
import markdown
from django.views.generic import CreateView, DetailView


from tools.my_tool import * #这里红色不是错误（标记源根即可解决），tools为项目下与各app包同级别的自建包

from users.models import Usersdata
from comment.models import Comment
from .models import Note
from .forms import NoteForm
# Create your views here.

#博客主页不需要登录
def note_index(request):
    """使用分页后为/note_index>page=n
    展示所有用户所有所有博客（显示摘要）-和分页方法结合
    优化整合,添加不同排序组,click_num和update_time,根据get的查询条件,返回不同排序的对象数组,默认最新
    进一步增加搜索文章逻辑
    """
    if cache.get('all_article_list'):
        article_list=cache.get('all_article_list')
    else:
        article_list = Note.objects.all()
        cache.set('all_article_list',article_list,20)
    search=request.GET.get('search')
    order = request.GET.get('order')
    tag = request.GET.get('tag')
    user = request.GET.get('user') #这里前端给的是用户id，比较快

    # print(request.GET)
    if user and user != 'None':  #ValueError: Field 'id' expected a number but got 'None'.
        # print('使用用户')
        if cache.get(user):
            article_list = cache.get(user)
        else:
            article_list=article_list.filter(user=user)
            cache.set(user,article_list,20)
    if search:
        # print('使用了搜索')
        # 使用 Q对象进行联合搜素;icontains是不区分大小写的包含，中间用两个下划线隔开
        #给查询设置缓存
        if cache.get(search):
            article_list=cache.get(search)
        else:
            article_list = article_list.filter(Q(title__icontains=search) | Q(content__icontains=search))
            cache.set(search, article_list, 20)
    else:
        # 将search参数重置为空
        search='' #如果用户没有搜索操作，则search = request.GET.get('search')会使得search = None，而这个值传递到模板中会错误地转换成"None"字符串！等同于用户在搜索“None”关键字，这明显是错误的
    if order=='click_num':
        # print('点击排序')
        article_list = article_list.order_by("-click_num")
    else:
        # print('时间排序')
        article_list=article_list.order_by("-update_time") #获取所有查询到的数据 ,最好带排序,否则可能如下报错
    if tag and tag != 'None':
        # print('使用了标签')
        if cache.get(tag):
            article_list=cache.get(tag)
        else:
            article_list = article_list.filter(tags__name__in=[tag])
            cache.set(tag,article_list,20)
    # print(articles_list)
    #UnorderedObjectListWarning: Paginationmay yield inconsistent resultswith an unordered object_list:<class 'blog.models.Note'> QuerySet.
    # 分页 每页9条
    paginator = Paginator(article_list, 9) #这里才发数据
    # print('当前对象的总个数是:', paginator.count)
    # print('当前对象的面码范围是:', paginator.page_range)
    # print('总页数是：', paginator.num_pages)
    # print('每页最大个数:', paginator.per_page)
    # 获取url的页码
    cur_page = request.GET.get('page', 1)  #得到擦查询字符串page,没有则1
    # 得到默认的当前页
    articles = paginator.page(cur_page) #负责具体一页内容

    #把新变量order也传递到模板中？因为文章需要翻页,order给模板一个标识，提醒模板下一页应该如何排序;增加查询关键字search和内容
    content={'articles':articles,'order':order,'search':search,'user':user,}
    return render(request,'blog/note_index.html',content)



#博客详情不需要登陆验证
def note_detail(request, id):
    """对应id的博客详情
    """
    # 取出相应的文章
    article = get_object_or_404(Note, id=id)
    # print(article.user.username)
    # print(article.user.profile)
    # print(article.tag)#多对多这样子拿不到数据
    # print(article.tag.all()) #这样才可以,后面还可以接values（）
    # print(tags)
    # for tag in tags:
    #     print('tag:',tag)
    # 多对多查询参考：https: // blog.csdn.net / qq_40199698 / article / details / 97827706

    # # 配置markdown，将Markdown语法书写的文章渲染为HTML文本
    # # 将markdown语法渲染成html样式，第一个参数是需要渲染的文章正文article.content；第二个参数载入了常用的语法扩展，
    # article.content = markdown.markdown(article.content,
    #                                     extensions=[
    #                                         # 包含 缩写、表格等常用扩展
    #                                         'markdown.extensions.extra',
    #                                         # 语法高亮扩展
    #                                         'markdown.extensions.codehilite',
    #                                         #加入了 toc 拓展后，就可以在文中插入目录了。方法是在书写Markdown文本时，在你想生成目录的地方插入[TOC]标记即可
    #                                         'markdown.extensions.toc',
    #                                     ])
    # #发现有一大堆<\p>
    # #注意：Django出于安全的考虑，会将输出的HTML代码进行转义，这使得article.content中渲染的HTML文本无法正常显示。
    # #解决：前端html在article.content后加上 | safe过滤器
    # # 管道符|是Django中过滤器的写法，而|safe就类似给article.body贴了一个标签，表示这一段字符不需要进行转义了。


    #浏览量:
    # 如果非作者本人点击,点击量+1
    # 过滤作者;
    if request.session.get('userinfo', False):
        userinfo = request.session.get('userinfo', False)
        username = userinfo.get('username', False)  # 拿出session里存的主键;
        #上面两句这么写会报'bool' object has no attribute 'get',需要一个错误处理,因为我这里没要求必须登录,所以try
        if username != article.user.username:
            #浏览量+1 指定了数据库只更新click_num字段，优化执行效率
            article.click_num+=1
            article.save(update_fields=['click_num'])


    #后续建立评论app功能后
    #取出文章评论
    comment_list = Comment.objects.filter(article_id=id)  #从数据库找出该文章的评论数据对象
    # print(comment_list.count)
    # print(comment_list)

    # 需要传递给模板的对象：文章后续添加评论,标签
    context = {'article': article,'comment_list':comment_list}

    # 载入模板，并返回context对象
    return render(request, 'blog/note_detail.html', context)
# 或者使用如下
# class ArticleDetailView(DetailView):
#     model = Note
#     template_name = 'note_detail.html

@check_login
def add_note(request):
    """
    添加博客
    :param request:
    :return:
    """
    if request.method=="GET":
        # 创建表单类实例
        note_post_form = NoteForm()
        # 赋值上下文
        context = {'note_post_form': note_post_form}  #这个不能少
        return render(request,'blog/add_note.html',context)

    elif request.method=='POST':
        # 将提交的数据赋值到表单实例中
        note_post_form = NoteForm(data=request.POST) #如果model表单有upload文件,需要带上files=request.FILES,没有会报错
        # 判断提交的数据是否满足模型的要求
        if  note_post_form.is_valid(): #如果表单有数据，且无错误，则返回True,否则 False.
            # 保存数据，但暂时不提交到数据库中
            new_note = note_post_form.save(commit=False)
            #确定是否作者本人操作
            userinfo=request.session.get('userinfo',False) #去看我存的格式
            uid=userinfo.get('uid',False) #拿出session里存的主键
            new_note.user=Usersdata.objects.get(id=uid)
            # 将新文章保存到数据库中
            new_note.save()
            # 新增代码，保存 tags 的多对多关系提交的表单使用了commit=False选项，则必须调用save_m2m()才能正确的保存标签，就像普通的多对多关系一样。
            note_post_form.save_m2m()
            #返回到文章详情页/或者在类里使用def get_absolute_url(self):return reverse('some_url', args=(self.id,))
            return redirect("blog:note_detail",id=new_note.id)
            # return redirect("blog:note_index")
        # 如果数据不合法，返回错误信息
        else:
            messages.error(request,'表单有误,请重新填写')
            return render(request,'blog/add_note.html')

# 也可以直接使用视图函数发布博客,并配置路由
class AddArticleView(CreateView):
    model = Note
    template_name = 'add_note.html'
    # 通过CreateView，可以获取到正在创建的对象
    # fields表单显示字段，后面在模板中可以直接使用
    fields = '__all__'

@check_login
def update_note(request,id):
    '''
    	更新文章的视图函数
    	通过POST方法提交表单，更新
    	GET方法进入初始表单页面
    	id： 文章的id
    	'''
    # 获取需要修改的具体文章对象
    #文章的id会从detail页面里那里拿到
    article = Note.objects.get(id=id)

    # 过滤非作者的用户
    userinfo = request.session.get('userinfo', False)
    username = userinfo.get('username', False)  # 拿出session里存的主键
    # print(username)
    # print(article.user.username)
    if username != article.user.username:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    # 判断用户是否为POST提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        note_post_form = NoteForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if note_post_form.is_valid():
            # 将表单获取的新title、content写入article数据
            article.title = request.POST['title']
            article.content = request.POST['content']
            # article.tags = request.POST['tags'] #这样写无效
            #关键是多对多的标签要注意
            tags_post=request.POST['tags'] #拿到的是带,的字符串
            # print(type(tags_post))
            tags_list_post=tags_post.split(',')  #分割为list
            tags_list=[]
            for i in tags_list_post:
                try:
                    i=eval(i)  #去除每个tag的""  #这里是处理tag初始化表单时自动加上“”的bug
                except:
                    pass
                tags_list.append(i)
            # print(tags_list)
            try:
                # https://blog.csdn.net/alexander068/article/details/119724017
                #Django多对多数据增删改查 http: // t.zoukankan.com / 17vv - p - 11723372.html
                article.tags.set(tags_list) #注意参数是个标签组成的列表
                article.save()
               #返回我的所有博客地址
                return redirect("blog:note_detail",id=id)
                # return HttpResponse('更新成功')
            except Exception as e:
                # 如果保存失败，返回错误信息
                messages.error(request,'修改失败，请重新填写！')
                return redirect("blog:update_note",id=id)
        # 如果数据不合法，返回错误信息
        else:
            messages.error(request, '表单内容有误，请重新填写！')
            return redirect("blog:update_note",id=id)

    # 如果用户GET请求获取数据
    else:
        # 创建表单类实例,直接将article文章对象也传递进去，作为默认值,分为初始化与未初始化
        note_post_form = NoteForm()
        note_post_form.fields['title'].initial=article.title
        note_post_form.fields['content'].initial=article.content
        note_post_form.fields['tags'].initial=article.tags.all() #发现一个bug,这里每次初始化会自动多出来"",所以上面post创建时候需要eval()过滤掉字符串的“”
        # note_post_form=NoteForm(initial = {'Email':article.title})
        # 参考https://www.cnblogs.com/yehua-night/p/14645942.html
        # print(note_post_form)
        # note_post_form["content"].initial=article
        context = {'note_post_form':note_post_form}
        # 将响应返回到模板中
        return render(request, 'blog/update_note.html', context)

@check_login
def delete_note(request,id):
    # """删除对应id的博客
    # path('delete/<int:id>',views.delete_note,name='delete_note'),
    # """
    if request.method == 'POST':
        # 根据 id 获取需要删除的博客文章
        article = Note.objects.get(id=id)
        # 过滤非作者的用户
        userinfo = request.session.get('userinfo', False)
        username = userinfo.get('username', False)  # 拿出session里存的主键
        if username != article.user.username:
            return HttpResponse("抱歉，你无权删除这篇文章。")

        #这里前端使用layer弹窗防止意外删除
        #防止攻击,所以前端使用form发起post请求,带上csrf令牌来避免csrf攻击
        # 调用.delete()方法删除文章
        article.delete()
        # 完成删除后返回展示所有博客列表
        return redirect("blog:note_index")
    else:
        messages.error(request,'您的请求不安全,当前无法删除')
        return HttpResponse("仅允许post请求")





#测试用
def searchtag(request,id):
    #参考:https: // blog.csdn.net / tbluhongxuan / article / details / 110233042
    # 参考https://www.656463.com/wenda/zdjangozsyTaggableManagerjxm2mgx_581

    article= Note.objects.get(id=id)
    # print(article)
    # print(article.content)
    # print(article.tags.all()) #<QuerySet [<Tag: ts>]>返回一个查询集
    return HttpResponse('t')
    # 设置tags
    # article.tags.set('tag1', 'tag2')  # 设置标签,已有标签会被清理掉。
    # 您必须使用add()
    # 在ManyToMany字段中添加项目
    # Use get() instead of getlist() beacuse in request it is a string 'Python,Data Science' not array
#     obj=Note.objects.get(id=1)
#     tagslist = request.POST.get("tag")
#     # Use split to make it a list
#     tagslist = [str(r) for r in tagslist.split(',')]
#     ...
#     # use add to add item in ManyToMany field.
#     obj.tags.add(*tagslist)
#     obj.save()
#     return HttpResponse('增加成功')
# # tagslist=request.POST['tags']
# print(request.POST['tags'])
# tagslist = request.POST.get("tag")
# Use split to make it a list
# tagslist = [str(r) for r in tagslist.split(',')]
# 执行保存
# use add to add item in ManyToMany field.
# article.tags.add(*tagslist)
#删除
# article.tags.remove("a_tag")




