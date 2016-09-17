# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.html import format_html, mark_safe

from django.db.models import F

import re


class Phrase(models.Model):
    phrase = models.TextField(unique=True)
    count = models.IntegerField(default=1)
    
    class Meta:
        ordering = ('-count',)
    
    def __unicode__(self):
        return self.phrase


class Example(models.Model):
    FILE_DETAIL = 'http://kkma.snu.ac.kr/statistic?submenu=filedetail&fileId={0}'
    VIEW_CONTEXT = 'http://kkma.snu.ac.kr/search?submenu=VIEW_CONTEXT&fileId={0}&partId={1}&sentId={2}'
    JKB = 'JKB'
    WORD_TYPE_CHOICES = (
        (JKB, 'JKB'),
        ('JKS', 'JKS'),
        ('NNG', 'NNG'),
        ('NNB', 'NNB'),
        ('UNT', 'UNT'),
        ('JKC', 'JKC'),
        ('MAG', 'MAG'),
    )
    WRITING = 'W'
    SPOKEN = 'S'
    WS_TYPE_CHOICES = (
        (WRITING, '문어'),
        (SPOKEN, '구어'),
    )
    CATEGORY_CHOICES = (
        ('처소', '처소'),
        ('출발점', '출발점'),
        ('출처', '출처'),
        ('근거', '근거'),
        ('비교의 기준', '비교의 기준'),
        ('주어임', '주어임'),
        ('기타', '기타')
    )

    word_type = models.CharField(verbose_name='품사', max_length=5, db_index=True,
                                 choices=WORD_TYPE_CHOICES, default=JKB,
                                 help_text='Word type')
    ws_type = models.CharField(verbose_name='문어/구어', max_length=1, db_index=True,
                               choices=WS_TYPE_CHOICES, default=WRITING,
                               help_text='Writing or Spoken')
    morpheme = models.CharField(verbose_name='형태소', max_length=255, db_index=True,
                                help_text='Keyword')
    index = models.PositiveIntegerField(null=True, blank=True, help_text='Search Index')
    content = models.TextField(null=True, blank=True)
    detail = models.TextField(null=True, blank=True)
    field_id = models.IntegerField(null=True, blank=True, default=0)
    part_id = models.IntegerField(null=True, blank=True, default=0)
    sent_id = models.IntegerField(null=True, blank=True, default=0)
    
    viewed = models.BooleanField(default=False)
    note = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, db_index=True, choices=CATEGORY_CHOICES,
                                null=True, blank=True)
    modified_on = models.DateTimeField(null=True, blank=True, auto_now=True)
    phrase_collected = models.BooleanField(default=False)
    
    phrases = models.ManyToManyField(Phrase, related_name='examples')
                                
    '''class Meta:
        ordering = ['morpheme', 'ws_type', 'index']'''
        
    def __unicode__(self):
        return self.content
    
    
    def get_file_detail_url(self):
        return self.FILE_DETAIL.format(self.field_id)
        
    def get_view_context(self):
        return self.VIEW_CONTEXT.format(self.field_id, self.part_id, self.sent_id)

    def detail_link(self):
        return format_html('<a href="{}" target="_blank">&lt;출처: 포구, 형태 의미 분석 전자파일&gt;</a>', self.get_file_detail_url())
    
    def context_link(self):
        return format_html('<a href="{}" target="_blank">[주변 문장 보기]</a>', self.get_view_context())
        
    def _content(self):
        return mark_safe(self.content.replace('span>','b>'))
    _content.short_description = 'Content'
    
    def _detail(self):
        return mark_safe(self.detail)
    _detail.short_description = 'Detail'
    
    def _index(self):
        return self.index
    _index.short_description = '#'
    
    @classmethod
    def collect_bold_content(cls):
        pattern = re.compile('\\<b\\>([^<]*)\\<\\/b\\>')
        for example in cls.objects.filter(phrase_collected=False):
            # Clean up
            content = example.content
            content = content.replace('\n', '').replace('\t', '').replace('\r', '')
            content = content.replace('&#13;', '').replace('span>','b>')
            example.content = content
            example.phrase_collected = True
            example.save()
            
            if content:
                matches = pattern.findall(content)
                for phrase in matches:
                    phrase_obj, created = Phrase.objects.get_or_create(phrase=phrase.strip())
                    if not created:
                        phrase_obj.count = F('count') + 1
                        phrase_obj.save()
                    example.phrases.add(phrase_obj)
