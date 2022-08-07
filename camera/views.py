import os

import cv2
import face_recognition
import redis
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import Face_img
import numpy as np
import pyttsx3
# Create your views here.

from tools.my_tool import *

def index(request):
    """
    登陆后的页面
    :param request:
    :return:
    """
    return render(request,'camera/index.html')



def show_all_img(request):
    """
    查：后端获取Face_img图片数据库的所有数据并渲染给前端展示
    :param request:
    :return:
    """
    # face_imgs = Face_img.get_all() #从数据库中取出所有的图片路径
    face_imgs = Face_img.objects.all()
    face_imgs = Face_img.objects.raw('select * from face_pic') #模型管理器的原生raw方法来执行select语句进行数据查询
    # print(face_imgs)
    context = {
        'fontend_face_imgs': face_imgs,
    }#使用fontend_face_imgs作为前后端约定好的参数名，模板HTML中for循环遍历的是上下⽂context的key
    # print(context['fontend_face_imgs'])
    return render(request, 'camera/show_all_img.html', context=context)


def show_a_img(request):
    """
    后端获取Face_img图片数据库的第一个数据并渲染给前端展示（测试用）
    :param request:
    :return:
    """

    # face_imgs = Face_img.get_all()[0] #从数据库中取出所有的图片路径
    face_imgs = Face_img.objects.all()
    afterwords = '这是后端传递的测试消息'
    if face_imgs:
        a_img = face_imgs[0]
        context = {
            'beforewords': afterwords,
            'fontend_a_img': a_img,
            'fontend_face_imgs': face_imgs,
        }
        print(context['beforewords'],context['fontend_face_imgs'],context['fontend_a_img'])
        return render(request, 'camera/show_a_img.html', context=context)
    else:
        return HttpResponse('未找到任何图片')

# def upload_img(request):
#     """传统文件上传写入方案，需要对文件重名进行处理，经过测试不会自动新建表里uploadto对应的文件夹"""
#     if request.method == 'GET':
#         return render(request, 'camera/upload_img.html')
#     elif request.method=='POST':
#         #上传和写入图片
#         a_file=request.FILES.get('pic_u') # 获取前端上传的文件,FILES的key对应页面的file的name=’pic_u‘，如果没有文件，则默认为None
#         if not a_file:
#             return HttpResponse("no imgs for upload...")
#         # print("a_file.file是个对象，上传文件名为：",a_file.name,"对象为：",a_file.file)
#
#         if not os.path.exists(settings.MEDIA_ROOT):
#             os.makedirs(settings.MEDIA_ROOT)
#
#         file = os.path.join(settings.MEDIA_ROOT, a_file.name)
#         with open(file,'wb') as f:
#             for chunk in a_file.chunks():  # 分块写入文件
#                 a_file.write(chunk)
#             f.close()
#         # with open(filename, 'wb') as f:
#         #     data=a_file.read() #a_file.file是文件字节流数据
#         #     f.write(data)
#
#         # orm
#         picname = request.POST['pic_n']
#         # img = Face_img()
#         # img.pic_name=picname
#         # img.face_url = file
#         # img.save()
#         img = Face_img(pic_name=picname,face_url=file) #创建数据模型对象
#         img.save()
#         #此方法upload_to自动创建子目录失效，见数据库pic_name=第二
#         return  HttpResponse("成功接收，文件名："+a_file.name)

@check_login
def upload_img(request):
    """django的上传写入方案,会自动对重名文件重命名"""
    if request.method == 'GET':
        return render(request, 'camera/upload_img.html')
    elif request.method=='POST':
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        userinfo = request.session.get('userinfo', False)
        uid = userinfo.get('uid', False)  # 拿出session里存的主键
        #上传和写入图片
        # file_name=request.POST['pic_n'] #对应html被注释的普通文本框
        a_file=request.FILES.get('pic_u') # 获取前端上传的文件,FILES的key对应页面的file的name=’pic_u‘，如果没有文件，则默认为None
        # a_file=request.FILES['pic_u']
        # print("上传文件名为：",a_file.name,"尺寸：",a_file.size,"文件类型：",a_file.content_type,"文件字节流数据:",a_file.file)
        #orm
        try:
            # 修改
            face_img = Face_img.objects.get(user_id=uid)

            # 先删除存储的原先上传后被存储在media的文件
            # 生成文件路径
            path = os.path.join(settings.MEDIA_ROOT,str(face_img.face_url))
            try:
                # print(path)
                os.remove(path)
            except Exception as e:
                print('存储中没有找到要删除的图片')
            face_img.pic_name=a_file.name
            face_img.face_url=a_file
            try:
                face_img.save()
            except Exception as e:
                return HttpResponse('修改失败')

            #这是批量修改
            # face_img=Face_img.objects.filter(user_id=uid)
            # face_img.update(pic_name=a_file.name, face_url=a_file)
            # return HttpResponse('修改成功')
            context = {'fontend_face_img': face_img}
            return render(request, 'camera/show_my_img.html', context)
        except Exception as e:
            print("""获取图片对象失败""")
            print(e.__class__.__name__)  # 错误类型
            print(e)  # 错误明细
            #创建
            # face_img = Face_img()
            # face_img.pic_name=a_file.name
            # face_img.face_url=a_file
            # face_img.user_id=uid
            # face_img.save()
            #新建用户如果上传图片重名,则face_url自动改名
            face_img=Face_img.objects.create(pic_name=a_file.name,face_url=a_file,user_id=uid)
            # return  HttpResponse("成功接收文件"+a_file.name)

            #因为redirect不能直接传数据到templates,所以使用render来加载刚上传的图片
            context={'fontend_face_img':face_img}
            # print(context['fontend_face_img'])
            return render(request, 'camera/show_my_img.html',context)

@check_login
def delete_img(request):
    userinfo = request.session.get('userinfo', False)
    uid = userinfo.get('uid', False)  # 拿出session里存的主键
    try:
        face_img = Face_img.objects.get(user_id=uid)
        # 修改
        # face_img.pic_name=a_file.name
        # face_img.face_url=a_file.a_file
        # face_img.save()
        face_img.delete()
        return HttpResponse("删除图片")

    except Exception as e:
        print("""获取图片对象失败""")
        print(e.__class__.__name__)  # 错误类型
        print(e)  # 错误明细
        return HttpResponse("删除图片失败")









def camera(request):
    """带redis的视频人脸识别"""
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    red = redis.StrictRedis(host='localhost', port=6379, db=1,password='123456')

    camera = cv2.VideoCapture(0)
    while True:
        # 参数ret 为True 或者False,代表有没有读取到图片
        # 第二个参数frame表示截取到一帧的图片
        ret, frame = camera.read()
        # frame = cv2.imread(r'C:\Users\TIM\c.jpg')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = face_cascade.detectMultiScale(gray, 1.5, 3)
        for (x, y, w, h) in face:
            # 绘制矩形框，颜色值的顺序为BGR，即矩形的颜色为蓝色
            img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]
            # 在检测到的人脸区域内检测眼睛
            # eyes = eye_cascade.detectMultiScale(roi_gray)
            # for (ex, ey, ew, eh) in eyes:
            # cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        cv2.imshow('camera', frame)

        k = cv2.waitKey(1)
        if k == ord('s'):
            rgb_frame = frame[:, :, ::-1]

            # 获取画面中的所有人脸位置及人脸特征码

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            # 对获取的每个人脸进行识别比对
            flag = False
            for (top, right, bottom, left), face_encoding in list(zip(face_locations, face_encodings)):
                print(face_encoding)
                print(face_encoding.shape)

                # 对其中一个人脸的比对结果（可能比对中人脸库中多个人脸）
                # keys = red.keys()
                # for key in keys:
                #     image = face_recognition.load_image_file(red.get(key))
                #     face_encoding = face_recognition.face_encodings(image)[0]
                #     namelist = []
                #     namelist.append(key)
                #获取所有键，所有的键构成⼀个列表，如果没有键则返回空列表
                faces = red.keys()
                for face in faces:
                    image = face_recognition.load_image_file(red.get(face))
                    face_encodings = face_recognition.face_encodings(image)[0]
                    print(np.array(face_encodings).shape)
                    print([np.array(face_encodings)])
                    matches = face_recognition.compare_faces([np.array(list(face_encodings))],
                                                             face_encoding, tolerance=0.40)
                    print(matches)
                    if True in matches:
                        engine = pyttsx3.init()
                        engine.say('你好,{}'.format(face.decode('utf-8')))
                        engine.runAndWait()
                        flag = True
                        break
            if flag is False:
                engine = pyttsx3.init()
                engine.say('无法识别')
                engine.runAndWait()
        if k == ord('q'):
            break
    camera.release()
    return render(request, 'home.html')


def camera1(request):
    """不redis的视频人脸识别"""
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    red = redis.StrictRedis(host='localhost', port=6379, db=1,password='123456')

    camera = cv2.VideoCapture(0)
    while True:
        # 参数ret 为True 或者False,代表有没有读取到图片
        # 第二个参数frame表示截取到一帧的图片
        ret, frame = camera.read()
        # frame = cv2.imread(r'C:\Users\TIM\c.jpg')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = face_cascade.detectMultiScale(gray, 1.5, 3)
        for (x, y, w, h) in face:
            # 绘制矩形框，颜色值的顺序为BGR，即矩形的颜色为蓝色
            img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]
            # 在检测到的人脸区域内检测眼睛
            # eyes = eye_cascade.detectMultiScale(roi_gray)
            # for (ex, ey, ew, eh) in eyes:
            # cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        cv2.imshow('camera', frame)

        k = cv2.waitKey(1)
        if k == ord('s'):
            rgb_frame = frame[:, :, ::-1]

            # 获取画面中的所有人脸位置及人脸特征码

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            # 对获取的每个人脸进行识别比对
            flag = False
            for (top, right, bottom, left), face_encoding in list(zip(face_locations, face_encodings)):
                print(face_encoding)
                print(face_encoding.shape)

                # 对其中一个人脸的比对结果（可能比对中人脸库中多个人脸）
                # keys = red.keys()
                # for key in keys:
                #     image = face_recognition.load_image_file(red.get(key))
                #     face_encoding = face_recognition.face_encodings(image)[0]
                #     namelist = []
                #     namelist.append(key)
                faces = red.keys()
                for face in faces:
                    image = face_recognition.load_image_file(red.get(face))
                    face_encodings = face_recognition.face_encodings(image)[0]
                    print(np.array(face_encodings).shape)
                    print([np.array(face_encodings)])
                    matches = face_recognition.compare_faces([np.array(list(face_encodings))],
                                                             face_encoding, tolerance=0.40)
                    print(matches)
                    if True in matches:
                        engine = pyttsx3.init()
                        engine.say('你好,{}'.format(face.decode('utf-8')))
                        engine.runAndWait()
                        flag = True
                        break
            if flag is False:
                engine = pyttsx3.init()
                engine.say('无法识别')
                engine.runAndWait()
        if k == ord('q'):
            break
    camera.release()
    return render(request, 'home.html')