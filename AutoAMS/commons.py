# -*- coding: utf-8 -*-
# Author:马海杰
# Email:mahaijie123@163.com

from django.shortcuts import render
from myauth.models import User,Group
from AutoAMS.settings import PERMISSIONS
import json,time,os,random
import commands

# status: 控制右上角提示框颜色，success添加成功(绿色)，warning为添加失败(橘黄色)，error红色
# 通过Session记录是否更新、添加成功
def mynotice(request,action='',status='',info=''):
    if action == "update":
        if status == "success":
            request.session["update"] = True
    elif action == "add":
        if status == "success":
            request.session["add"] = True

    else:
        if "add" in request.session:
            if request.session["add"]:
                status = "success"
                info = "恭喜您，添加成功！"
                request.session["add"] = False
        if "update" in request.session:
            if request.session["update"]:
                status = "success"
                info = "恭喜您，更新成功！"
                request.session["update"] = False

    return "toastr.%s('%s')"%(status,info)

# list转换为字符串（逗号间隔）
def list_to_str(list):
    if list:
        str = ",".join(list)
        return str
    else:
        return ""

# str(逗号间隔)转换为list
def str_to_list(str):
    if str:
        return str.split(',')
    else:
        return ""

# fping
def myping(ip):
    result = commands.getstatusoutput("fping -r 2 -t 200 %s"%(ip))
    if(result[0] == 0):
        return True
    else:
        result = commands.getstatusoutput("fping -r 2 -t 200 %s"%(ip))
        if(result[0] == 0):
            return True
        else:
            return False

# 装饰器函数（验证当前用户是否拥有view中的函数权限）
def permission_validate(func):
    def wrapper(request,*args, **kwargs):
        func_name = func.__name__ # 获取view中被装饰的函数名
        username = request.user.username

        # admin拥有所有权限
        if(username == 'admin'):
            return func(request,*args, **kwargs)

        user = User.objects.get(username = username)
        group = Group.objects.get(id = user.group_id)
        permissions = group.permissions

        permissions_list = str_to_list(permissions)
        # admin拥有所有权限
        if(func_name in permissions_list or username == 'admin'):
            return func(request,*args, **kwargs)
        else:
            return render(request,'common/NoAccess.html',{"info":PERMISSIONS[func_name]})

    return wrapper