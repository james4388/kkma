# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.html import format_html, mark_safe

from django.db.models import F

import re


class Phrase(models.Model):
    phrase = models.CharField(max_length=255, db_index=True)
    count = models.IntegerField(default=0, verbose_name='Total Count')
    
    class Meta:
        ordering = ('-count',)
    
    def __unicode__(self):
        return self.phrase


class Example(models.Model):
    CATEGORY_CHOICES = (
        ('처소', '처소'),
		('추상 처소', '추상 처소'),
        ('출발점', '출발점'),
        ('출처', '출처'),
        ('근거', '근거'),
        ('비교의 기준', '비교의 기준'),
        ('주체임', '주체임'),
        ('기타', '기타'),
    )
    morpheme = models.CharField(verbose_name='형태소', max_length=255, db_index=True,
                                help_text='Keyword')  # 서 - 에서 Column C filename
    used_in = models.CharField(verbose_name='사용역', max_length=255, db_index=True,
                                help_text='Source of example')   # Column G sheet name     
    content = models.TextField(verbose_name='용례', null=True, blank=True)    # Column B

    prefix = models.CharField(verbose_name='선행요소', max_length=400, null=True, blank=True)   # Column E
    suffix = models.CharField(verbose_name='후행요소', max_length=400, null=True, blank=True)   # Column F
    category = models.CharField(verbose_name='의미', max_length=50, db_index=True,
                                choices=CATEGORY_CHOICES, null=True, blank=True) # D
    modified_on = models.DateTimeField(null=True, blank=True, auto_now=True)
    
    phrases = models.ManyToManyField(Phrase, related_name='examples')
                                
    '''class Meta:
        ordering = ['morpheme', ]'''
        
    def __unicode__(self):
        return self.content
    
