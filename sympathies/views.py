#encoding=utf-8
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from forms import AddSympathyForm, AddSympathyCommentForm
from models import Sympathy, SympathyComment
from django.core.exceptions import PermissionDenied
from django.utils import timezone

class SympathyListView(ListView):
    model = Sympathy
    paginate_by = 10
    queryset = Sympathy.objects.order_by('-create_date')
                                    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(SympathyListView, self).get_context_data(**kwargs)

class SympathyCreateView(CreateView):
    form_class = AddSympathyForm
    model = Sympathy
    success_url = '../'
    template_name = 'sympathies/sympathy_create.html'
    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(SympathyCreateView, self).get_context_data(**kwargs)
    
    def get_initial(self):
        initial = super(SympathyCreateView, self).get_initial()
        initial = initial.copy() # copy the dictionary so we don't accidentally change a mutable dict
        initial['first_name'] = self.request.user.first_name
        initial['last_name'] = self.request.user.last_name
        return initial
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.modify_date = form.instance.create_date = timezone.now()
        return super(SympathyCreateView, self).form_valid(form)
    
class SympathyDetailView(DetailView):
    model = Sympathy
    
    def get_context_data(self, **kwargs):
        kwargs['comment_count'] = SympathyComment.objects.filter(sympathy=self.kwargs['pk']).count()
        kwargs['active_tab'] = self.kwargs['active_tab']
#        kwargs['attachment_count'] = GreetingAttachment.objects.filter(sympathy=self.kwargs['pk']).count()
        return super(SympathyDetailView, self).get_context_data(**kwargs)
    
class SympathyCommentCreateView(CreateView):
    form_class = AddSympathyCommentForm
    model = SympathyComment
    template_name = 'sympathy_comments/comment_create.html'
    success_url = '.'
    
    def get_context_data(self, **kwargs):
        kwargs['comment_list'] = SympathyComment.objects.filter(sympathy=self.kwargs['pk']).order_by('-create_date')
        kwargs['sympathy'] = Sympathy.objects.get(id=self.kwargs['pk'])
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(SympathyCommentCreateView, self).get_context_data(**kwargs)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.sympathy_id = self.kwargs['pk']
        form.instance.create_date = timezone.now()
        return super(SympathyCommentCreateView, self).form_valid(form)
    
    
class UserOwnedObjectMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        obj = super(UserOwnedObjectMixin, self).get_object(queryset)
        if self.request.user.is_staff:
            return obj
        if obj.user_id != self.request.user.id:
            raise PermissionDenied
        return obj
    
    
class SympathyUpdateView(UpdateView, UserOwnedObjectMixin):
    model = Sympathy
    form_class = AddSympathyForm
    success_url = '../'
    template_name = 'sympathies/sympathy_edit.html'
    
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(SympathyCreateView, self).get_context_data(**kwargs)
    
    @method_decorator(login_required(login_url='/nariai/prisijungti'))
    #@method_decorator(user_passes_test(lambda u: u.is_staff, login_url='/stop'))
    def dispatch(self, *args, **kwargs):
        return super(SympathyUpdateView, self).dispatch(*args, **kwargs)