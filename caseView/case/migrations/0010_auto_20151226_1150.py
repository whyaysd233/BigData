# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-26 03:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case', '0009_auto_20151226_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='content',
            field=models.TextField(blank=True),
        ),
    ]
