import re
from django import newforms as forms
from django.newforms.widgets import TextInput, PasswordInput, HiddenInput, MultipleHiddenInput, CheckboxInput, Select, SelectMultiple,Textarea,NullBooleanSelect
from django.newforms import ValidationError

from rcache.models import *

class CommentaryForm(forms.Form):
    user = forms.IntegerField(widget=HiddenInput)
    entry = forms.IntegerField(widget=HiddenInput)
    title = forms.CharField(max_length=255,widget=Textarea)
    summary = forms.CharField(required=False,widget=Textarea) 
    
class FolioForm(forms.Form):
    user = forms.IntegerField(widget=HiddenInput)
    folio_name = forms.CharField(max_length=255)
    description = forms.CharField(widget=Textarea)
    
