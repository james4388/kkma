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
        categories = ((None, '0. None'), )
        for index, option in enumerate(Example.CATEGORY_CHOICES):
            new_option = ((option[0], str(index + 1) + '. ' + option[1]), )
            categories += new_option
        self.fields['category'].choices = categories