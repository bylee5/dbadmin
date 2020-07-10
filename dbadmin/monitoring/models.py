# Create your models here.
from __future__ import unicode_literals
from django.db import models
from datetime import datetime

# Create your models here.

class JobInfo(models.Model):
    job_info_seqno = models.AutoField(primary_key=True)
    job_info_name = models.CharField(max_length=150)
    job_info_detail = models.CharField(max_length=300, blank=True, null=True)
    job_info_note = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job_info'

class JobServerMap(models.Model):
    job_server_map_seqno = models.BigAutoField(primary_key=True)
    job_info_seqno = models.PositiveIntegerField()
    server_list_seqno = models.PositiveSmallIntegerField()
    use_yn = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'job_server_map'
        unique_together = (('job_info_seqno', 'server_list_seqno'),)

class ServerList(models.Model):
    server_list_seqno = models.SmallAutoField(primary_key=True)
    svr = models.CharField(max_length=30, blank=True, null=True)
    usg = models.CharField(max_length=100, blank=True, null=True)
    port1 = models.PositiveSmallIntegerField(blank=True, null=True)
    ip1 = models.CharField(max_length=15, blank=True, null=True)
    ip2 = models.CharField(max_length=15, blank=True, null=True)
    priority = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'server_list'
        unique_together = (('svr', 'port1'), ('ip1', 'port1'),)