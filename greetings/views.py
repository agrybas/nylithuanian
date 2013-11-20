#encoding=utf-8
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from forms import AddGreetingForm, AddGreetingCommentForm
from models import Greeting, GreetingComment
from django.core.exceptions import PermissionDenied
from django.utils import timezone

class GreetingListView(ListView):
    model = Greeting
    paginate_by = 10
    queryset = Greeting.objects.order_by('-create_date')
                                                                    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(GreetingListView, self).get_context_data(**kwargs)


class GreetingCreateView(CreateView):
    form_class = AddGreetingForm
    model = Greeting
    success_url = '../'
    template_name = 'greetings/greeting_create.html'
    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(GreetingCreateView, self).get_context_data(**kwargs)
    
    def get_initial(self):
        initial = super(GreetingCreateView, self).get_initial()
        initial = initial.copy() # copy the dictionary so we don't accidentally change a mutable dict
        initial['first_name'] = self.request.user.first_name
        initial['last_name'] = self.request.user.last_name
        return initial
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.modify_date = form.instance.create_date = timezone.now()
        return super(GreetingCreateView, self).form_valid(form)

class GreetingDetailView(DetailView):
    model = Greeting
    
    def get_context_data(self, **kwargs):
        kwargs['comment_count'] = GreetingComment.objects.filter(greeting=self.kwargs['pk']).count()
        kwargs['active_tab'] = self.kwargs['active_tab']
#        kwargs['attachment_count'] = GreetingAttachment.objects.filter(greeting=self.kwargs['pk']).count()
        return super(GreetingDetailView, self).get_context_data(**kwargs)

class GreetingCommentCreateView(CreateView):
    form_class = AddGreetingCommentForm
    model = GreetingComment
    template_name = 'greeting_comments/comment_create.html'
    success_url = '.'
    
    def get_context_data(self, **kwargs):
        kwargs['comment_list'] = GreetingComment.objects.filter(greeting=self.kwargs['pk']).order_by('-create_date')
        kwargs['greeting'] = Greeting.objects.get(id=self.kwargs['pk'])
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(GreetingCommentCreateView, self).get_context_data(**kwargs)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.greeting_id = self.kwargs['pk']
        form.instance.create_date = timezone.now()
        return super(GreetingCommentCreateView, self).form_valid(form)
    
    
class UserOwnedObjectMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        obj = super(UserOwnedObjectMixin, self).get_object(queryset)
        if self.request.user.is_staff:
            return obj
        if obj.user_id != self.request.user.id:
            raise PermissionDenied
        return obj
    
    
class GreetingUpdateView(UpdateView, UserOwnedObjectMixin):
    model = Greeting
    form_class = AddGreetingForm
    success_url = '../'
    template_name = 'greetings/greeting_edit.html'
    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(GreetingUpdateView, self).get_context_data(**kwargs)
    
    @method_decorator(login_required(login_url='/nariai/prisijungti'))
    #@method_decorator(user_passes_test(lambda u: u.is_staff, login_url='/stop'))
    def dispatch(self, *args, **kwargs):
        return super(GreetingUpdateView, self).dispatch(*args, **kwargs)