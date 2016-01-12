# coding=utf-8
from django.contrib import admin
from models import Case


class CaseAdmin(admin.ModelAdmin):
    """定义admin页面数据显示的形式
    """
    # 指定在列表页面显示那些字段
    list_display  = ['title','isTarget','class1','class2','class3','topic']
    # 指定在详情页面显示那些信息
    fields = ('id','title','time','court','symbol','isTarget','topic','class1','class2','class3','content','words')
    # 指定那些字段是只读的
    # readonly_fields = ('id','title','time','content','words','court','symbol')
    readonly_fields = ('id','title','time','content','words','court','symbol','isTarget','topic','class1','class2','class3')

    # 指定那些字段可以使用网页右侧的过滤器进行筛选
    list_filter = ['isTarget','class1','class2',]
    # 指定那些字段可以使用搜索栏搜索
    search_fields = ['title','class1','class2','class3','topic']

admin.site.register(Case,CaseAdmin)
admin.site.disable_action('delete_selected')