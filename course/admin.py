from django.contrib import admin

# Register your models here.
import course
from .models import Course

admin.site.register(Course)


class CourseAdmin(admin.ModelAdmin):
    # 需要显示的字段
    list_display = ('name', 'introduction', 'teacher', 'price')
    # 需要过滤的字段
    search_fields = list_display
    # 过滤的字段
    list_filter = list_display
