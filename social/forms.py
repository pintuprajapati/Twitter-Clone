from django import forms
from django.forms import ModelForm, TextInput, EmailInput, Textarea
from .models  import Post

class PostForm(forms.ModelForm):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Write something interesting...'
        })
    )

    class Meta:
        model = Post
        fields = ['body']
        # widgets = {
        #     'body': forms.Textarea(
        #         attrs={'placeholder': 'Write Something Interesting', "rows": "5"}),
        # }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields["body"].widget = forms.TextInput(attrs={
    #         "rows": "5"
    #     })
