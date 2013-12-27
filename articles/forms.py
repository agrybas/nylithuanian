#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Article, ArticleComment

class AddArticleForm(ModelForm):
    error_css_class = 'error'
    class Meta:
        model = Article
        exclude = ('is_approved',)


class AddArticleCommentForm(ModelForm):
    class Meta:
        model = ArticleComment
