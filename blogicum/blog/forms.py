from django import forms

from .models import Comment, Post, User


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ['author', 'is_published']
        widgets = {'pub_date': forms.DateTimeInput(
            format='%d-%m-%Y',
            attrs={'type': 'date'}
        )
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
