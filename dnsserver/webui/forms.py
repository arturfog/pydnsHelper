from django import forms

from .models import Host

class PostForm(forms.ModelForm):

    class Meta:
        model = Host
        fields = ('url', 'ip',)
