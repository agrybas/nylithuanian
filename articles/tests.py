#encoding=utf-8
from django.test import TestCase
from django.utils import unittest
from django.test.client import Client
from django.contrib.auth.models import User

from .forms import AddArticleForm

class IntegrationTestSuite(TestCase):
    def setUp(self):
        self.client = Client()
        
    def tearDown(self):
        pass
        
    def test_ArticlesListView(self):
        response = self.client.get('/straipsniai/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['active_tab'], 'straipsniai')
        self.assertTemplateUsed(response, 'articles/article_list.html')
        self.assertTrue(len(response.context_data['object_list']) <= 10)
        
    def test_ArticlesCreateView_WithLogin(self):\
#         self.client.login(username="algirdas", password="234wer234") # TODO: doesn't log user in, have to use the line below
        self.user = User.objects.create_user(username="algirdas", password="234wer234")
        self.client.post('/nariai/prisijungti/', {'username': 'algirdas', 'password': '234wer234'})
        response = self.client.get('/straipsniai/pateikti/')
        self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.context_data['active_tab'], 'straipsniai')
        self.assertTemplateUsed(response, 'articles/article_create.html')
        
    def test_ArticlesCreateView_NoLogin(self):
        response = self.client.get('/straipsniai/pateikti/')
        self.assertRedirects(response, '/nariai/prisijungti?next=/straipsniai/pateikti/', target_status_code=301) # TODO: why target_status_code = 200 doesn't work?
        
    def test_ArticlesCreateView_SubmitValidForm(self):
        self.user = User.objects.create_user(username="algirdas", password="234wer234")
        self.client.post('/nariai/prisijungti/', {'username': 'algirdas', 'password': '234wer234'})
        response = self.client.post('/straipsniai/pateikti/', {
                                                              'title': 'Some title',
                                                              'body': 'Body text',
                                                              })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/article_preview.html')

    
    def test_ArticlesCreateView_SubmitEmptyForm(self):
        self.user = User.objects.create_user(username="algirdas", password="234wer234")
        self.client.post('/nariai/prisijungti/', {'username': 'algirdas', 'password': '234wer234'})
        response = self.client.post('/straipsniai/pateikti/', {})
        self.assertFormError(response, 'form', 'title', u'Šis laukas yra privalomas.')
        self.assertFormError(response, 'form', 'body', u'Šis laukas yra privalomas.')
            
class UnitTestSuite(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_AddArticleForm_Empty(self):
        form_data = {}
        form = AddArticleForm(form_data)
        self.assertEqual(form.is_valid(), False)
        
    def test_AddArticleForm_Valid(self):
        form_data = {'title': 'some title', 'body': 'body text'}
        form = AddArticleForm(form_data)
        self.assertEqual(form.is_valid(), True)
        
    def test_AddArticleForm_LongTitle(self):
        form_data = {'title': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse vehicula laoreet nunc vitae scelerisque. Cras ut sollicitudin neque, a euismod metus. Fusce mauris est, ornare in quam at, adipiscing pretium orci. Vestibulum quis lectus a tellus nullam.', 'body': 'body text'}
        form = AddArticleForm(form_data)
        self.assertEqual(form.is_valid(), False)
        
    def test_AddArticleForm_LongFirstName(self):
        form_data = {
                     'title': 'some title',
                     'body': 'body text',
                     'first_name': 'Lorem ipsum dolor sit volutpat.',
                     }                     
        form = AddArticleForm(form_data)
        self.assertEqual(form.is_valid(), False)
 
    def test_AddArticleForm_LongLastName(self):
        form_data = {
                     'title': 'some title',
                     'body': 'body text',
                     'last_name': 'Lorem ipsum dolor sit volutpat.',
                     }                     
        form = AddArticleForm(form_data)
        self.assertEqual(form.is_valid(), False)
        
    def test_AddArticleForm_LongOrganizationTitle(self):
        form_data = {
                     'title': 'some title',
                     'body': 'body text',
                     'organization_title': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce feugiat tincidunt interdum massa nunc.',
                     }                     
        form = AddArticleForm(form_data)
        self.assertEqual(form.is_valid(), False)
        
    def test_AddArticleForm_LongSignature(self):
        form_data = {
                     'title': 'some title',
                     'body': 'body text',
                     'signature': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. In adipiscing, mauris vel dictum pulvinar, diam tellus dignissim metus, non posuere dolor eros nec dui. Praesent risus quam, varius nec odio id, vestibulum convallis diam. Suspendisse convallis amet.',
                     }                     
        form = AddArticleForm(form_data)
        self.assertEqual(form.is_valid(), False)
        
    def test_AddArticleForm_LongPhoneNumber(self):
        form_data = {
                     'title': 'some title',
                     'body': 'body text',
                     'phone_number': '+000-1111-22222-33333',
                     }                     
        form = AddArticleForm(form_data)
        self.assertEqual(form.is_valid(), False)
        
    def test_AddArticleForm_InvalidPhoneNumber(self):
        form_data = {
                     'title': 'some title',
                     'body': 'body text',
                     'phone_number': 'asdf',
                     }                     
        form = AddArticleForm(form_data)
        self.assertEqual(form.is_valid(), False)
        
    def test_AddArticleForm_InvalidEmailAddress(self):
        form_data = {
                     'title': 'some title',
                     'body': 'body text',
                     'email_address': 'asdf',
                     }                     
        form = AddArticleForm(form_data)
        self.assertEqual(form.is_valid(), False)
                
    def test_AddArticleForm_InvalidPublishDate(self):
        form_data = {
                     'title': 'some title',
                     'body': 'body text',
                     }                     
        form = AddArticleForm(form_data)
        self.assertEqual(form.is_valid(), False)