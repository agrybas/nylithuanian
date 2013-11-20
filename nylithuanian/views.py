from django.views.generic import TemplateView
from events.models import Event
from articles.models import Article
from users.models import UserProfile
from greetings.models import Greeting
from sympathies.models import Sympathy
from django.utils import timezone

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['upcoming_events'] = Event.approved.filter(start_date__gte=timezone.now()).order_by('start_date')
        context['past_events'] = Event.approved.filter(start_date__lt=timezone.now()).order_by('-start_date')[:5]
        context['articles'] = Article.objects.filter(is_approved=True).filter(publish_date__lte=timezone.now()).order_by('-publish_date')[:5]
        context['new_users'] = UserProfile.objects.filter(user__is_active=True).order_by('-user__date_joined')[:5]
        context['greetings'] = Greeting.objects.order_by('-create_date')[:5]
        context['sympathies'] = Sympathy.objects.order_by('-create_date')[:5]
        return context
    
