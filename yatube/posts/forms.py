from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta(UserCreationForm.Meta):
        # модель с которой будет связана создаваемая форма
        model = Post
        # укажем какие полня должны быть видны в форме и в каком порядке
        fields = ('text','group', 'image')

class CommentForm(forms.ModelForm):
    class Meta(UserCreationForm.Meta):
        model = Comment
        fields = ('text',)
