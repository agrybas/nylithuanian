from django.forms import ModelForm, Textarea
from .models import PhotoComment
from django.utils import timezone

class AddPhotoCommentForm(ModelForm):
    class Meta:
        model = PhotoComment
        widgets = {
            'body': Textarea(attrs={'cols': 100, 'rows': 10}),
        }

    def form_valid(self, form):
        form.instance.user = self.request.user.id
        form.instance.create_date = timezone.now()
        return super(AddPhotoCommentForm, self).form_valid(form)