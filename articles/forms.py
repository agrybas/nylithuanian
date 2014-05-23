#encoding=utf-8
from django.forms import ModelForm, Textarea, TextInput
from models import Article, ArticleComment
from django.template.loader import get_template
from django.template import Context
from django.core.mail import mail_admins

class ArticleForm(ModelForm):
    error_css_class = 'error'
    required_css_class = 'required'

class AddArticleForm(ArticleForm):   
    class Meta:
        model = Article
        exclude = ('is_approved',)
        
    def save(self):
 
        article = super(AddArticleForm, self).save()
        
        # inform admins about the pending article
        plainText = get_template('emails/new_article.txt')
        htmlText = get_template('emails/new_article.html')
        subject = u'Naujas straipsnis'
        c = Context({
                 'article' : article,
                 })
    
        mail_admins(subject=subject, message=plainText.render(c), html_message=htmlText.render(c))
        
        return article


class AddArticleCommentForm(ArticleForm):
    class Meta:
        model = ArticleComment
