# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-14 11:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_ap_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='wlc',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
