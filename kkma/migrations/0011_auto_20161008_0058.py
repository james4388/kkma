# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-08 07:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kkma', '0010_auto_20160925_2311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phrase',
            name='phrase',
            field=models.CharField(max_length=300, unique=True),
        ),
    ]