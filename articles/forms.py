#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Article, ArticleComment

class AddArticleForm(ModelForm):
    error_css_class = 'error'
    class Meta:
        model = Article
        widgets = {
            'title' : TextInput(attrs={'size' : 100}),
            'body' : Textarea(attrs={'cols' : 100, 'rows' : 20}),
        }
        exclude = ('is_approved',)


class AddArticleCommentForm(ModelForm):
    class Meta:
        model = ArticleComment
        widgets = {
                   'body' : Textarea(attrs={'cols' : 100, 'rows' : 10}),
                   }
