# Create your models here.
from __future__ import unicode_literals
from django.db import models
from datetime import datetime

# Create your models here.

class Faq(models.Model):
    faq_id = models.CharField(max_length=16, default='0000000000000001')
    faq_type = models.CharField(max_length=10, default='999')
    faq_question = models.TextField(default='질문')
    faq_answer = models.TextField(default='답변')

    class Meta:
        db_table = u'testing_faq'

    def __str__(self):
        return self.faq_id

class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    title = models.CharField(max_length=50)
    content = models.TextField()
    read = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        db_table = u'testing_post'

    def __str__(self):
        return self.created
