from django import forms
from django.conf import settings

from .models import Example


class ExampleImportForm(forms.ModelForm):
    class Meta:
        model = Example
        fields = ['word_type', 'ws_type', 'morpheme',
                  'index', 'content', 'detail', 'field_id',
                  'part_id', 'sent_id']
                  

class FlashcardForm(forms.ModelForm):
    category = forms.ChoiceField(widget=forms.RadioSelect)

    class Meta:
        model = Example
        fields = ['category']
        
    def __init__(self, *args, **kwargs):
        super(FlashcardForm, self).__init__(*args, **kwargs)
        categories = Example.CATEGORY_CHOICES[:]
        categories += (('None', None), )
        self.fields['category'].choices = categories