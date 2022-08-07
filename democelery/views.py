from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from democelery.tasks import add

#使用delay调用shared_task任务之一的add
def ab(request):
    result=add.delay(666,888) #返回任务id
    return HttpResponse(result)