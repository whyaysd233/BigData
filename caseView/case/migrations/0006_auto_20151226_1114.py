# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-26 03:14
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0005_auto_20151226_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='isTarget',
            field=models.BooleanField(default=datetime.datetime(2015, 12, 26, 3, 14, 9, 571000, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='case',
            name='title',
            field=models.CharField(max_length=20, verbose_name='Title'),
        ),
    ]
