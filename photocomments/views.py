from django.views.generic import CreateView
from django.utils import timezone
from .models import PhotoComment
from photologue.models import Photo

class CommentCreateView(CreateView):
    form_class = AddPhotoCommentForm
    model = PhotoComment
    template_name = 'comment_create.html'
    success_url = '.'
    
    def get_context_data(self, **kwargs):
        kwargs['comment_list'] = PhotoComment.objects.filter(photo=self.kwargs['pk']).order_by('-create_date')
        kwargs['photo'] = Photo.objects.get(id=self.kwargs['pk'])
        kwargs['active_tab'] = self.kwargs['active_tab']
        return super(CommentCreateView, self).get_context_data(**kwargs)
    
    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        form.instance.photo_id = self.kwargs['pk']
        form.instance.create_date = timezone.now()
        return super(CommentCreateView, self).form_valid(form)