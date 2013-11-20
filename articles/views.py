#encoding=utf-8
from django.contrib.auth.decorators import login_required
from django.contrib.formtools.preview import FormPreview
from django.contrib.syndication.views import Feed
from django.core.exceptions import PermissionDenied
from django.core.mail import mail_admins
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.views.generic.detail import SingleObjectMixin


from forms import AddArticleForm, AddArticleCommentForm
from models import Article, ArticleComment
from users.models import UserProfile

import logging
import nylithuanian.settings

if nylithuanian.settings.DEBUG:
    logger = logging.getLogger('debug.' + __name__)
else:
    logger = logging.getLogger('production.' + __name__)

#@login_required(login_url='/prisijungti')
#def add_article(request):
#    
#    if request.method == 'POST':
#        form = AddArticleForm(request.POST)
#        if form.is_valid():
#            data = form.cleaned_data
#            Article.objects.create(title=data['title'], body=data['body'], summary=data['summary'],
#                                   publish_date=data['publish_date'], expiry_date=data['expiry_date'], user=request.user)
#            return HttpResponseRedirect('/straipsniai/ikelti-straipsni')
#    else:
#        form = AddArticleForm()
#        return render_to_response('add_article_form.html', {'form' : form},
#                              context_instance=RequestContext(request))
#    

#class ArticleCreateView(CreateView):
#    form_class = AddArticleForm
#    model = Article
#    success_url = '../'
#    template_name = 'articles/article_create.html'
#    
#    def get_initial(self):
#        initial = super(ArticleCreateView, self).get_initial()
#        initial = initial.copy() # copy the dictionary so we don't accidentally change a mutable dict
#        initial['first_name'] = self.request.user.first_name
#        initial['last_name'] = self.request.user.last_name
#        return initial
#    
#    def form_valid(self, form):
#        form.instance.user_id = self.request.user.id
#        form.instance.modify_date = form.instance.create_date = form.instance.publish_date = timezone.now()
#        return super(ArticleCreateView, self).form_valid(form)

class ArticleListView(ListView):
    model = Article
    paginate_by = 10
    queryset = Article.public.order_by('-publish_date')
    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(ArticleListView, self).get_context_data(**kwargs)

class ArticleDetailView(DetailView):
    model = Article
    
    def get_context_data(self, **kwargs):
        kwargs['comment_count'] = ArticleComment.objects.filter(article_id=self.kwargs['pk']).count()
        kwargs['active_tab'] = self.kwargs['active_tab']
        if self.request.user.is_active:
            kwargs['is_favorite'] = UserProfile.objects.filter(user_id=self.request.user.id).filter(favorite_articles__id=self.kwargs['pk']).exists()
#        kwargs['attachment_count'] = ArticleAttachment.objects.filter(event=self.kwargs['pk']).count()
        return super(ArticleDetailView, self).get_context_data(**kwargs)
    
class ArticleRssView(Feed):
    title = 'Naujausi straipsniai Niujorko lietuviams'
    link = '/renginiai/'
    description = 'Naujausi straipsniai apie Amerikos lietuvius. Straipsniai publikuojami www.nylithuanian.org ir Amerikos spaudoje.'
    
    def items(self):
        return Article.public.filter(external_link='').order_by('-publish_date')

    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        if len(item.body) <= 1000:
            return item.body
        return item.body[:1000].rsplit(' ', 1)[0] + '...'
        
class ArticleCommentCreateView(CreateView):
    form_class = AddArticleCommentForm
    model = ArticleComment
    template_name = 'article_comments/comment_create.html'
    success_url = '.'
    
    def get_context_data(self, **kwargs):
        kwargs['comment_list'] = ArticleComment.objects.filter(article=self.kwargs['pk']).order_by('-create_date')
        kwargs['article'] = Article.public.get(id=self.kwargs['pk'])
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(ArticleCommentCreateView, self).get_context_data(**kwargs)
    
    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        form.instance.article_id = self.kwargs['pk']
        form.instance.create_date = timezone.now()
        return super(ArticleCommentCreateView, self).form_valid(form)
    
    @method_decorator(login_required(login_url='/nariai/prisijungti'))
    def post(self, request, *args, **kwargs):
        return super(ArticleCommentCreateView, self).post(request, args, kwargs)

class UserOwnedObjectMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        obj = super(UserOwnedObjectMixin, self).get_object(queryset)
        if self.request.user.is_staff:
            return obj
        if obj.user_id != self.request.user.id:
            raise PermissionDenied
        return obj

class ArticleUpdateView(UpdateView, UserOwnedObjectMixin):
    model = Article
    form_class = AddArticleForm
    success_url = '../'
    template_name = 'articles/article_edit.html'
    
    @method_decorator(login_required(login_url='/nariai/prisijungti'))
    #@method_decorator(user_passes_test(lambda u: u.is_staff, login_url='/stop'))
    def dispatch(self, *args, **kwargs):
        return super(ArticleUpdateView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        kwargs['form'] = AddArticleForm(instance=Article.objects.get(id=self.kwargs['pk']))
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(ArticleUpdateView, self).get_context_data(**kwargs)
    
class AddArticlePreview(FormPreview):
    form_template = 'articles/article_create.html'
    preview_template = 'articles/article_preview.html'
    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(AddArticlePreview, self).get_context_data(**kwargs)
    
    @method_decorator(login_required(login_url='/nariai/prisijungti'))
    def done(self, request, cleaned_data):
        try:
            logger.info(u'Adding a new article "{0}" to database...'.format(cleaned_data['title']))
            
            reviewed_form = AddArticleForm(cleaned_data)
            logger.debug(u'title: {0}'.format(cleaned_data['title']))
            logger.debug(u'body: {0}'.format(cleaned_data['body'][:50]))
            logger.debug(u'first_name: {0}'.format(cleaned_data['first_name']))
            logger.debug(u'last_name: {0}'.format(cleaned_data['last_name']))
            logger.debug(u'organization_title: {0}'.format(cleaned_data['organization_title']))
            logger.debug(u'phone: {0}'.format(cleaned_data['phone_number']))
            logger.debug(u'email: {0}'.format(cleaned_data['email_address']))
            logger.debug(u'signature: {0}'.format(cleaned_data['signature']))
            logger.debug(u'publication_date: {0}'.format(cleaned_data['publish_date']))
            
            reviewed_form.instance.user = request.user
            logger.debug(u'User ID: {0}'.format(reviewed_form.instance.user.id))
            
            # already provided as default values in model definition
            #reviewed_form.instance.create_date = reviewed_form.instance.modify_date = timezone.now()
            #logger.debug(u'Date created: {0}'.format(reviewed_form.instance.create_date))
            #logger.debug(u'Date modified: {0}'.format(reviewed_form.instance.modify_date))
            
            reviewed_form.save()
            logger.info(u'Article has been added successfully.')
            
            # inform admins about the pending article
            plainText = get_template('emails/new_article.txt')
            htmlText = get_template('emails/new_article.html')
            subject = u'Naujas straipsnis'
            c = Context({
                     'article' : cleaned_data,
                     })
        
            mail_admins(subject=subject, message=plainText.render(c), html_message=htmlText.render(c))
            
            
            return render_to_response('articles/success.html', {
                                        'message' : 'Ačiū! Jūsų straipsnis buvo sėkmingai pateiktas. Svetainės administratoriai artimiausiu metu perskaitys Jūsų straipsnį ir nedelsiant paskelbs jį svetainėje. Jei kiltų neaiškumų, susisieksime su Jumis tiesiogiai.',
                                        }, context_instance=RequestContext(request))
        except:
            logger.exception('Exception thrown while adding a new article:')

def toggle_favorite(request, *args, **kwargs):
    try:
        article = Article.objects.get(id=kwargs['pk'])
        user = UserProfile.objects.get(user_id=request.user.id)
        
        # if article already marked as favorite
        if UserProfile.objects.filter(user_id=request.user.id).filter(favorite_articles__id=kwargs['pk']).exists():
            try:
                logger.info(u'User {0} is unmarking article "{1}" as favorite...'.format(request.user.username, article.title))
                user.favorite_articles.remove(article)
                logger.info('Article unmarked as favorite successfully.')
            except Exception:
                logger.exception(u'Exception thrown while unmarking article id={0} as favorite:'.format(kwargs['pk']))
                return render_to_response('articles/error.html', {
                                        'message' : 'Bandant pašalinti straipsnį iš favoritų, įvyko klaida. Apie tau jau pranešta svetainės administratoriams. Atsiprašome už nepatogumus.',
                                        }, context_instance=RequestContext(request))
        
        # if article is not marked as favorite yet
        else:
            try:
                logger.info(u'User {0} is marking article "{1}" as favorite...'.format(request.user.username, article.title))
                user.favorite_articles.add(article)
                logger.info('Article marked as favorite successfully.')
            except Exception:
                logger.exception(u'Exception thrown while marking article id={0} as favorite:'.format(kwargs['pk']))
                return render_to_response('articles/error.html', {
                                        'message' : 'Bandant pažymėti straipsnį favoritu, įvyko klaida. Apie tau jau pranešta svetainės administratoriams. Atsiprašome už nepatogumus.',
                                        }, context_instance=RequestContext(request))
    
        return HttpResponseRedirect('../')
    except Article.DoesNotExist:
        logger.exception(u'Exception thrown while toggling favorite status of article id={0}:'.format(kwargs['pk']))
        raise Http404
    except Exception:
        logger.exception(u'Exception thrown while toggling favorite status of article id={0}:'.format(kwargs['pk']))
        return render_to_response('articles/error.html', {
                                        'message' : 'Bandant pakeisti straipsnio favorito statusą, įvyko klaida. Apie tau jau pranešta svetainės administratoriams. Atsiprašome už nepatogumus.',
                                        }, context_instance=RequestContext(request))
        