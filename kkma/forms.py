from django import forms
from django.conf import settings

from .models import Example


class ExampleImportForm(forms.ModelForm):
    class Meta:
        model = Example
        fields = ['morpheme', 'content', 'used_in', 'prefix', 'suffix', 'category']
                  

class FlashcardForm(forms.ModelForm):
    category = forms.ChoiceField(widget=forms.RadioSelect)
    
    class Meta:
        model = Example
        fields = ['category', 'prefix', 'suffix',]
        widgets = {
            'prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'suffix': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(FlashcardForm, self).__init__(*args, **kwargs)
        categories = ((None, '0. Not set'), )
        for index, option in enumerate(Example.CATEGORY_CHOICES):
            new_option = ((option[0], str(index + 1) + '. ' + option[1]), )
            categories += new_option
        self.fields['category'].choices = categories