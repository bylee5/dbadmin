# Create your models here.
from django import forms
from .models import *

# Create your models here.

class ServerListForm(forms.Form):
    svr = forms.CharField(max_length=30)
    job_info_name = forms.CharField(max_length=150)
    use_yn = forms.IntegerField()

#class PostForm(forms.ModelForm):

#    class Meta:
#        model = Post
#        fields = ('title', 'text',)

