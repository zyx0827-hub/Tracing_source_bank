from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# 我的第一个django测试方法
def sayhello(request):
    return HttpResponse("hello django!")
# Create your views here.
# Create your views here.
def index(request):
    return render(request, 'index.html')