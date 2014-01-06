#encoding=utf-8
from django.db import models


    
# Reference model containing states of USA, keyed by their two-letter abbreviations
class State(models.Model):
    state_id = models.CharField(max_length = 2, primary_key = True)
    name = models.CharField(max_length = 20)
    
    class Meta:
        db_table = 'states'
        
    def __unicode__(self):
        return self.name
