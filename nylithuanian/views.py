from django.views.generic import TemplateView
from events.models import Event
from articles.models import Article
from announcements.models import Announcement
from users.models import SiteUser
from greetings.models import Greeting
from sympathies.models import Sympathy
from classifieds.models import Classified
from django.utils import timezone
import settings

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['DEBUG'] = settings.DEBUG
        context['upcoming_events'] = Event.public.filter(start_date__gte=timezone.now()).order_by('start_date')
        context['articles'] = Article.public.filter(publish_date__lte=timezone.now()).order_by('-publish_date')[:3]
        context['announcements'] = Announcement.public.order_by('-create_date')[:3]
        context['classifieds'] = Classified.public.order_by('-create_date')[:5]
#        context['user_count'] = SiteUser.objects.filter(is_active=True).count()
        return context
    
