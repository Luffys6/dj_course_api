# encoding: utf-8"
'''
@author: dbj
@file: urls.py
@time: 2021/4/1 15:41
@desc:
'''
from django.urls import path, include
from course import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# prefix 相当于url前缀
router.register(prefix='viewsets', viewset=views.CourseViewSets)

urlpatterns = [
    # FBV
    path('fbv/list', views.course_list, name="fbv-list"),  # name 表示网页返回显示的路由地址
    path('fbv/details/<int:pk>', views.course_details, name="fbv-details"),
    # Class Based View
    path('cbv/list', views.CourseList.as_view(), name="cbv-list"),
    path('cbv/detail/<int:pk>', views.CourseDetail.as_view(), name="cbv-detail"),

    # Generic Class Based View
    path("gcbv/list", views.GCourseList.as_view(), name="gcbv-list"),
    path("gcbv/detail/<int:pk>", views.GCourseDetail.as_view(), name="gcbv-detail"),

    # DRF viewsets
    # path("viewsets", views.CourseViewSet.as_view(
    #     {"get": "list", "post": "create"}
    # ), name="viewsets-list"),
    # path("viewsets/<int:pk>", views.CourseViewSet.as_view(
    #     {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
    # ), name="viewsets-detail"),
    path("", include(router.urls)),


]