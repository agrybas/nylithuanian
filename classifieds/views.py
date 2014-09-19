#encoding=utf-8
from django.core.exceptions import PermissionDenied
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from models import Classified, ClassifiedCategory, ClassifiedSubCategory
from forms import AddClassifiedForm

class ClassifiedView(object):
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(ClassifiedView, self).get_context_data(**kwargs)


class ClassifiedCreateView(ClassifiedView, CreateView):
    model = Classified
    form_class = AddClassifiedForm
    template_name = 'classifieds/classified_create.html'
#    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'events/attachments'))
    success_url = 'aciu'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ClassifiedCreateView, self).form_valid(form)
    

class ClassifiedCategoriesListView(ClassifiedView, ListView):
    model = ClassifiedCategory
    template_name = 'classifieds/classifiedcategory_list.html'
      

class ClassifiedsListView(ClassifiedView, ListView):
    model = Classified
#    queryset = Classified.objects.filter(category=self.kwargs['pk'])
    paginate_by = 5
    template_name = 'classifieds/classified_list.html'

    def get_queryset(self):
        return Classified.public.filter(category=self.kwargs['pk'])
        
    def get_context_data(self, **kwargs):
        kwargs['active_tab'] = self.kwargs['active_tab']
        category = ClassifiedSubCategory.objects.get(id=self.kwargs['pk'])
        return super(ClassifiedsListView, self).get_context_data(**kwargs)


class ClassifiedDetailView(ClassifiedView, DetailView):
    model = Classified
    template_name = 'classifieds/classified_detail.html'

    def get_queryset(self):
        return Classified.public.all()
    

class UserOwnedObjectMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        obj = super(UserOwnedObjectMixin, self).get_object(queryset)
        if self.request.user.is_staff:
            return obj
        if obj.user_id != self.request.user.id:
            raise PermissionDenied
        return obj
    

class ClassifiedUpdateView(UserOwnedObjectMixin, UpdateView):
    model = Classified
    template_name = 'classifieds/classified_edit.html'
    