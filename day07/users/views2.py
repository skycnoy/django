import logging
import traceback
import datetime
from django.shortcuts import render, reverse, Http404, HttpResponseRedirect
from django.http import JsonResponse, QueryDict
from django.views.generic import View, ListView, TemplateView, DetailView
from django.db.models import Q, F
from django.conf import settings
from users.form import UserLoginForm, UserCreateForm, UserModefyForm
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from pure_pagination.mixins import PaginationMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import UserProfile
from django.contrib.auth import authenticate, login, logout

logger = logging.getLogger('UserProfile')


class IndexView(LoginRequiredMixin, View):
    """
    登录功能
    """
    # 用户没有通过时跳转的地址，默认是 settings.LOGIN_URL.
    # 在settings中设置LOGIN_URL='/accounts/login/'
    # login_url = '/login/'
    # redirect_field_name = 'redirect_to'
    redirect_field_name = None

    def get(self, request):
        # print(request.user)
        # print(request.user.is_authenticated)
        # if not request.user.is_authenticated:
        #     return HttpResponseRedirect(reverse("accounts:login"))
        return render(request, 'dashboard/index.html')

    def post(self, request):
        return render(request, 'dashboard/index.html')


class UserListJsView(PaginationMixin, LoginRequiredMixin, ListView):
    """
    1.用户列表，可搜索姓名手机号
    """

    template_name = 'users/userlist.html'
    model = UserProfile
    context_object_name = "users"
    paginate_by = 10

    # 用户没有通过时跳转的地址，默认是 settings.LOGIN_URL.
    # login_url = '/login/'
    # redirect_field_name = 'redirect_to'
    redirect_field_name = None

    # def get_queryset(self):
    #     """关键词搜索，姓名，手机号"""
    #     queryset = super(UserListJsView, self).get_queryset()
    #     self.keyword = self.request.GET.get("keyword", "").strip()
    #     if self.keyword:
    #         queryset = queryset.filter(Q(name__icontains=self.keyword) | Q(phone__icontains=self.keyword))
    #     return queryset

    # def get_context_data(self, **kwargs):
    #     """将关键字保持在搜索框内, 将过滤后的数据传给前端"""
    #     context = super(UserListJsView, self).get_context_data(**kwargs)
    #     context["users"] = UserProfile.objects.filter(**kwargs)
    #     return context



    def post(self, request):
        """
        创建用户: 此功能使用表单来操作数据
        """
        print("POST:", request.POST)
        try:
            userForm = UserCreateForm(request.POST)
            print(type(userForm))
        except:
            res = {"code": 3, "errmsg": "信息填写不完整"}
            return render(request, settings.JUMP_PAGE, res)

        if userForm.is_valid():
            try:
                if request.POST.get('agree') == "on":
                    userForm.save()
                    res = {"code": 0, "msg": "用户创建成功"}
                    # 用户没有勾选同意按钮
                else:
                    res = {"code": 3, "errmsg": "信息填写不完整"}
            except:
                logger.error("create user error: %s" % traceback.format_exc())
                res = {"code": 1, "errmsg": "用户创建失败"}
        else:
            # 获取表单数据
            print(userForm.errors)
            # print(userForm.errors.as_json())
            res = {"code": 2, "errmsg": userForm.errors}
        return render(request, settings.JUMP_PAGE, res)


class UserAddJsView(LoginRequiredMixin, TemplateView):
    # 用户没有通过时跳转的地址，默认是 settings.LOGIN_URL.
    # login_url = '/login/'
    # redirect_field_name = 'redirect_to'
    redirect_field_name = None
    template_name = 'users/useradd.html'


class UserDelJsView(LoginRequiredMixin, TemplateView):
    # 用户没有通过时跳转的地址，默认是 settings.LOGIN_URL.
    # login_url = '/login/'
    # redirect_field_name = 'redirect_to'
    redirect_field_name = None
    template_name = 'users/userdel.html'

    def post(self, request, **kwargs):
        # 先获取前端传过来的主键
        pk=kwargs['pk']
        # 如果主键不存在，报用户不存在
        print(request.POST.get('comment'))
        if not pk:
            res = {"code": 3, "errmsg": "用户不存在"}
            return render(request, settings.JUMP_PAGE, res)
        else:
            if request.POST.get('comment') == "我确认":
                try:
                    UserProfile.objects.filter(pk=pk).delete()
                    res = {"code": 0, "msg": "用户删除成功"}
                except:
                    logger.error("delete user error %s" % traceback.format_exc())
                    res = {"code": 1, "errmsg": "用户删除异常"}
            else:
                res = {"code": 2, "errmsg": "用户输入内容不满足要求，删除取消！"}
        return render(request, settings.JUMP_PAGE, res)


class UserModJsView(LoginRequiredMixin, DetailView):
    """
    更新用户信息
    1.基于原信息修改，密码必须修改
    """
    model = UserProfile
    template_name = 'users/usermod.html'
    context_object_name = "user"
    # 用户没有通过时跳转的地址，默认是 settings.LOGIN_URL.
    # login_url = '/login/'
    # redirect_field_name = 'redirect_to'
    redirect_field_name = None

    def post(self, request, **kwargs):
        print(request.POST, kwargs)
        pk = kwargs["pk"]
        user = UserProfile.objects.get(pk=pk)
        userForm = UserModefyForm(request.POST, instance=user)
        if not pk:
            res = {"code": 1, "errmsg": "用户不存在"}
            return render(request, settings.JUMP_PAGE, res)
        else:
            try:
                print("userForm2:", userForm)
                if userForm.is_valid():
                    # 修改完后必须得勾选确认按钮，此功能应该在前端校验
                    if request.POST.get('agree') == "on":
                        userForm.save()
                        res = {"code": 0, "msg": "用户信息更新成功"}
                    else:
                        res = {"code": 4, "errmsg": "信息填写不完整"}
                else:
                    # 获取表单的数据，便于排错
                    print(userForm.errors)
                    print(userForm.errors.as_json())
                    res = {"code": 2, "errmsg": userForm.errors}
            except:
                # 获取更新操作的错误信息
                logger.error("modefy user error %s"% traceback.format_exc())
                res = {"code": 3, "errmsg": "用户信息更新失败"}
        return render(request, settings.JUMP_PAGE, res)

    # def post(self, request, **kwargs):
    #     pk = kwargs['pk']
    #     if not pk:
    #         res = {"code": 1, "errmsg": "用户不存在"}
    #     else:
    #         try:
    #             data = request.POST.dict()
    #             print("data:", data)
    #             if data["agree"] == "on":
    #                 data = data.pop('agree').pop('confirm_password')
    #                 User.objects.filter(pk=pk).update(**data)
    #                 res = {"code": 0, "errmsg": "用户信息更新成功"}
    #             else:
    #                 res = {"code": 2 , "errmsg": "用户取消更新操作"}
    #         except:
    #             logger.error("更新过程出现异常%s" % traceback.format_exc())
    #             res = {"code": 3, "errmsg": "更新异常"}
    #     return render(request, settings.JUMP_PAGE, res)


class UserInfoJsView(LoginRequiredMixin, DetailView):
    template_name = 'users/userinfo.html'
    model = UserProfile
    context_object_name = "user"
    # 用户没有通过时跳转的地址，默认是 settings.LOGIN_URL.
    # login_url = '/login/'
    # redirect_field_name = 'redirect_to'
    redirect_field_name = None

    def get(self, request, **kwargs):
        print("POST:", request.POST)
        pk = kwargs["pk"]
        user = UserProfile.objects.filter(pk=pk)
        return render(request, 'users/userinfo.html', {"user": user})


def page_not_found(request, exception, template_name='404.html'):
    return render(request, template_name)

# class IndexJsView(DetailView):
#     template_name = 'dashboard/index.html'
#     model = UserProfile
#     context_object_name = "user"
#     #
#     # def post(self, request, **kwargs):
#     #     print("POST:", request.POST)
#     #     pk = kwargs["pk"]
#     #     user = UserProfile.objects.filter(pk=pk)
#     #     return render(request, 'dashboard/index.html')

# class TestListView(PaginationMixin, ListView):
#     # Important, this tells the ListView class we are paginating
#     template_name = 'users/userlist.html'
#
#     model = UserProfile
#     context_object_name = "users"
#     paginate_by = 3
#     # Replace it for your model or use the queryset attribute instead
# class UserLoginJsView(View):
#     """
#     登录验证：
#     from django.contrib.auth.mixins import LoginRequiredMixin
#     from django.contrib.auth import authenticate, login, logout
#     """
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return render(request, 'dashboard/login.html')
#
#     def post(self, request):
#         print("POST:", request.POST)
#         login_form = UserLoginForm(request.POST)
#         print("form:", login_form)
#         ret = dict(login_form=login_form)
#         print("ret:", ret)
#         if login_form.is_valid():
#             username_input = request.POST["username"]
#             password_input = request.POST["password"]
#             data = UserProfile.objects.filter(username=username_input, password=password_input)
#             if data:
#                 ret["msg"] = "登录成功"
#                 data_list = list(data.values())
#                 pk = data_list[0]["id"]
#                 user = UserProfile.objects.filter(pk=pk)
#                 print("user:", user)
#                 return render(request, 'dashboard/index.html', {"user": user})
#             else:
#                 ret["errmsg"] = "账号或密码错误"
#         else:
#             print(login_form.errors)
#             ret["errmsg"] = "账号和密码不能为空"
#         return render(request, 'dashboard/login.html', ret)
#
#
#     """
#     使用Django自带的auth模块来校验登录
#     """
#     # def post(self, request, **kwargs):
#     #     print("POST:", request.POST)
#     #     # 此处先获取用户登录表单
#     #     login_form = UserLoginForm(request.POST)
#     #     # 将表单内容字典化，以便得会加入其它字段
#     #     ret = dict(login_form=login_form)
#     #     if login_form.is_valid():
#     #         # 获取用户输入的用户名和密码
#     #         name_input = request.POST["name"]
#     #         password_input = request.POST["password"]
#     #         user = authenticate(name=name_input, password=password_input)
#     #         if user is not None:
#     #             login(request, user)
#     #             return render(request, 'dashboard/index.html')
#     #         else:
#     #             ret["errmsg"] = "用户名或密码错误"
#     #     else:
#     #         ret["errmsg"] = "用户名或密码不能为空"
#     #     return render(request, 'dashboard/login.html', ret)
