from django import forms
from django.forms import ModelForm, TextInput, EmailInput, Textarea
from .models  import Post, Comment, UserProfile

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

class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Comment your opinion...'
        })
    )

    class Meta:
        model = Comment
        fields = ['comment']

# class UserProfileForm(forms.ModelForm):
    # comment = forms.CharField(
    #     label='',
    #     widget=forms.Textarea(attrs={
    #         'rows': '3',
    #         'placeholder': '...'
    #     })
    # )

    # class Meta:
    #     model = UserProfile
    #     fields = ['name', 'bio', 'birth_date', 'locatoin', 'picture']
