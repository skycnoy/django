import logging
import traceback

from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView

from hello.form import UserModelForm, UserUpdateModelForm
from hello.models import User

logger = logging.getLogger("devops")


class UserListFormView(ListView):
    """
    1.用户列表：支持搜索
    """
    model = User
    template_name = 'hello/userlist.html'
    context_object_name = "users"
    keyword = ""
    print("hello world=============")

    def get_queryset(self):
        queryset = super(UserListFormView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            # Q模块实现多条件搜索过滤
            queryset = queryset.filter(Q(name__icontains=self.keyword)) | (Q(phone__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(UserListFormView, self).get_context_data(**kwargs)
        # context["keyword"] = self.keyword
        context["users"] = User.objects.filter(**kwargs)
        return context

    """
    用户创建
    """

    def post(self, request):
        userForm = UserModelForm(request.POST)
        if userForm.is_valid():
            try:
                # 方案一：手动入库
                # print(userForm.cleaned_data)
                # data = userForm.cleaned_data
                # self.model.objects.create(**data)
                # 方案二：调用源码自带的save方法入库
                userForm.save()
                res = {"code": 0, "result": "添加用户成功"}
            except:
                logger.error("create user error: %s" % traceback.format_exc())
                res = {"code": 1, "errmsg": "添加用户失败"}
        else:
            # 获取自定义表单错误的两种方式
            print(userForm.errors)
            print(userForm.errors.as_json())
            res = {"code": 1, "errmsg": userForm.errors}
        return render(request, settings.JUMP_PAGE, res)


class UserAddFormView(TemplateView):
    """
    用户添加GET请求返回一个页面
    """
    template_name = 'hello/useradd.html'


class UserDetailFormView(DetailView):
    """
    用户详情
    """
    model = User
    template_name = 'hello/usermod.html'
    context_object_name = "user"

    """
    更新用户信息
    """

    def post(self, request, **kwargs):
        pk = kwargs.get('pk')
        # 方案一： 表单验证后，手动入库
        # userForm = UserUpdateModelForm(request.POST)

        # 方案二： 调用源码中针对更新操作的save方法入库
        user = self.model.objects.get(pk=pk)
        userForm = UserUpdateModelForm(request.POST, instance=user)
        if userForm.is_valid():
            try:
                # 方案一： 拿到form中的数据，手动入库
                # data = userForm.cleaned_data
                # data.pop('confirm_password')
                # self.model.objects.filter(pk=pk).update(**data)

                # 方案二：通过modelform验证过的数据和save方法入库
                print(userForm.cleaned_data)
                userForm.save()
                res = {"code": 0, "msg": "更新用户成功"}
            except:
                res = {"code": 1, "errmsg": "用户更新失败"}
                logger.error("update user error %s " % traceback.format_exc())
        else:
            # 获取所有的表单错误
            print(userForm.errors)
            res = {"code": 1, "errmsg": userForm.errors}
        return render(request, settings.JUMP_PAGE, res)

    """
    删除用户：delete method 浏览器无法复现，使用curl测试，或postman
    curl -X DELETE "http://IP:PORT/hello/userdetailformview/2/"        
    """
class UserDelFormView(TemplateView):
    template_name = 'hello/userdel.html'

    def post(self, request, **kwargs):
        pk = kwargs.get('pk')

        try:
            # self.model.objects.filter(pk=pk).delete()
            if request.POST.get('delete') == "True":
                # self.get_object().delete()
                User.objects.filter(pk=pk).delete()
                res = {"code": 0, "msg": "用户删除成功"}
            elif request.POST.get('delete') == "False":
                res = {"code": 2, "errmsg": "用户取消删除操作"}
        except:
            logger.error("delete user error %s " % traceback.format_exc())
            res = {"code": 1, "msg": "用户删除失败"}
        return render(request, settings.JUMP_PAGE, res)
