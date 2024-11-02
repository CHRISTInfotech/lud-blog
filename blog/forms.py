from django import forms 
from .models import Post, Comment, Category
from ckeditor.widgets import CKEditorWidget

choices = Category.objects.all().values_list('name','name')

choice_list = []

for item in choices:
    choice_list.append(item)


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(attrs={'rows': 5}))
    
    class Meta:
        model = Post
        fields = ('title','category','content')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'category': forms.Select(choices=choice_list,attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class PostUpdateForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Post
        fields = ('title','category','content') 
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(choices=choice_list,attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label='', widget=forms.TextInput(attrs={'placeholder': 'Add comment here....'}))

    class Meta:
        model = Comment
        fields = ('content',)

