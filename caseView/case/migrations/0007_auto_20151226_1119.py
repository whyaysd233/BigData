# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-26 03:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0006_auto_20151226_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='isTarget',
            field=models.BooleanField(verbose_name='\u5efa\u7b51\u8150\u8d25'),
        ),
    ]
