# coding=utf-8
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Case(models.Model):
    """用于表示一个案件，在此处定义每个案件的所有字段

    """
    id = models.CharField('ID',max_length=10,primary_key=True)
    title = models.CharField(u'标题',max_length=20)
    time = models.DateField(u'审判时间',blank=True,null=True)
    court = models.CharField(u'法院',max_length=20,blank=True,null=True)
    symbol = models.CharField(u'案件字号',max_length=20,blank=True,null=True)
    content = models.TextField(u'正文',blank=True,null=True)

    words = models.TextField(u'分词结果',blank=True,null=True)

    isTarget = models.BooleanField(u'是否建筑腐败',blank=True,default=False)

    topic = models.CharField(u'关键词',blank=True,max_length=200,null=True)
    class1 = models.CharField(u'行为主体',blank=True,max_length=30,null=True)
    class2 = models.CharField(u'行为环节',blank=True,max_length=30,null=True)
    class3 = models.CharField(u'行为方式',blank=True,max_length=30,null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'所有案例'
        verbose_name_plural = u'所有案例'