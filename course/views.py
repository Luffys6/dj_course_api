from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from course.models import Course
from course.serializers import CourseSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics, viewsets
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token
from permissions import IsOwnerOrOnlyRead


@receiver(post_save, sender=settings.AUTH_USER_MODEL)  # Django信号机制
def generate_token(sender, instance=None, created=False, **kwargs):
    """
   创建用户时生成Token
   :param sender:
   :param instance:
   :param created: 默认不创建
   :param kwargs:
   :return:
   """
    if created:
        Token.objects.create(user=instance)


"""一、 函数式编程 Function Based View
        @api_view 装饰器
"""


@api_view(["GET", "POST"])
@authentication_classes((BasicAuthentication,))
@permission_classes((IsAuthenticated,))
def course_list(request):
    """
    获取所有课程信息或新增一个课程
    :param request:
    :return:
    """
    if request.method == 'GET':
        # 序列化多个对象 many=True
        s = CourseSerializer(instance=Course.objects.all(), many=True)
        return Response(data=s.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # 反序列化
        s = CourseSerializer(data=request.data)  # 部分更新用partial=True属性
        # 反序列化需要校验
        if s.is_valid():
            # 因为model设置的teacher是必须并只读的，这里直接设置当前用户
            s.save(teacher=request.user)
            return Response(data=s.data, status=status.HTTP_201_CREATED)
        return Response(s.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def course_details(request, pk):
    """
    获取、更新、删除一个课程
    :param request:
    :param pk: primary key 主键的意思
    :return:
    """
    try:
        # 因为可能查询不到，所以加上 try
        course = Course.objects.get(pk=pk)
    except Course.DoesNotExist:
        return Response(data={"msg": "没有此课程信息"}, status=status.HTTP_404_NOT_FOUND)
    else:
        if request.method == "GET":
            s = CourseSerializer(instance=course)
            return Response(data=s.data, status=status.HTTP_200_OK)
        if request.method == "PUT":
            # instance序列化查询到的对象
            # data 获取前端传来的数据
            s = CourseSerializer(instance=course, data=request.data)
            if s.is_valid():
                # 因为这是修改，teacher已经存在了，所以直接保存
                s.save()
                return Response(data=s.data, status=status.HTTP_200_OK)
            return Response(data=s.errors, status=status.HTTP_400_BAD_REQUEST)
        if request.method == "DELETE":
            course.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


""" 类视图编程 Class Based View """


class CourseList(APIView):
    """
    查询课程
    """
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """

        :param request:
        :return:
        """
        queryset = Course.objects.all()
        s = CourseSerializer(instance=queryset, many=True)
        return Response(s.data, status=status.HTTP_200_OK)

    """
    添加课程
    """

    def post(self, request):
        """

        :param request:
        :return:
        """
        s = CourseSerializer(data=request.data)  # 调接口传过来的数据
        if s.is_valid():
            s.save(teacher=self.request.user)
            # 分别是<class 'django.http.request.QueryDict'> <class 'rest_framework.utils.serializer_helpers.ReturnDict'>
            print(type(request.data), type(s.data))
            return Response(data=s.data, status=status.HTTP_201_CREATED)
        return Response(data=s.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDetail(APIView):

    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated, IsOwnerOrOnlyRead)
    """
    方便共用对象
    """
    def get_objects(self, pk):
        try:
            obj = Course.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            return obj
        except Course.DoesNotExist:
            return

    """
    查询课程
    """
    def get(self, request, pk):
        """
        :param request:
        :param pk:
        :return:
        """
        obj = self.get_objects(pk=pk)
        if not obj:
            return Response(data={"msg": "没有此课程信息"}, status=status.HTTP_404_NOT_FOUND)
        s = CourseSerializer(instance=obj)
        return Response(s.data, status=status.HTTP_200_OK)
    """
     修改课程
    """
    def put(self, request, pk):
        """
        :param request:
        :param pk:
        :return:
        """
        obj = self.get_objects(pk=pk)
        if not obj:
            return Response(data={"msg": "没有此课程信息"}, status=status.HTTP_404_NOT_FOUND)
        s = CourseSerializer(instance=obj, data=request.data)
        if s.is_valid():
            s.save()
            return Response(data=s.data, status=status.HTTP_200_OK)
        return Response(data=s.errors, status=status.HTTP_400_BAD_REQUEST)
    """
       删除课程
      """
    def delete(self, request, pk):
        """

        :param request:
        :param pk:
        :return:
        """
        obj = self.get_objects(pk=pk)
        if not obj:
            return Response(data={"msg": "没有此课程信息"}, status=status.HTTP_404_NOT_FOUND)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


"""通用类视图 GENERIC Class Based View"""


# 获取 添加
class GCourseList(generics.ListCreateAPIView):
    # queryset名字必须为这个
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


# 获取 修改 删除
class GCourseDetail(generics.RetrieveUpdateDestroyAPIView):
    # queryset名字必须为这个
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


"""四、 DRF的视图集viewsets"""


class CourseViewSets(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrOnlyRead)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)
