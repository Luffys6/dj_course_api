# encoding: utf-8
'''
@author: dbj
@file: serializers.py
@time: 2021/4/1 11:46
@desc:
'''

from django import forms
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Course


# class CourseForm(forms.ModelForm):
#     class Meta:
#         model = Course
#         fields = ('name', 'introduction', 'teacher', 'price')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.username')  # 外键字段 只读

    class Meta:
        model = Course  # 写法和上面的CourseForm类似
        fields = '__all__'
        depth = 2



# class CourseSerializer(serializers.HyperlinkedModelSerializer):
#     teacher = serializers.ReadOnlyField(source='teacher.username')
#
#     class Meta:
#         model = Course
#         # url是默认值，可在settings.py中设置URL_FIELD_NAME使全局生效
#         fields = ('id', 'url', 'name', 'introduction', 'teacher', 'price', 'created_at', 'updated_at')