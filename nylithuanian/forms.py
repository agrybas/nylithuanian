#encoding=utf-8
from django.forms import Form, CharField, Textarea

class SendEmailForm(Form):
    message = CharField(label="Naujienlaiškio tekstas", widget=Textarea)