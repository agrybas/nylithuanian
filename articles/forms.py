#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Article, ArticleComment

class ArticleForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

class AddArticleForm(ArticleForm):   
    class Meta:
        model = Article
        exclude = ('is_approved',)


class AddArticleCommentForm(ArticleForm):
    class Meta:
        model = ArticleComment
