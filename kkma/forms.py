from django import forms
from django.conf import settings

from .models import Example


class ExampleImportForm(forms.ModelForm):
    class Meta:
        model = Example
        fields = ['word_type', 'ws_type', 'morpheme',
                  'index', 'content', 'detail', 'field_id',
                  'part_id', 'sent_id']
