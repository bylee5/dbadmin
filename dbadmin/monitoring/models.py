# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class JobInfo(models.Model):
    job_info_seqno = models.AutoField(primary_key=True)
    job_info_name = models.CharField(max_length=150)
    job_info_detail = models.CharField(max_length=300, blank=True, null=True)
    job_info_note = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'job_info'
        app_label = 'tmon_dba'


class JobServerMap(models.Model):
    job_server_map_seqno = models.BigAutoField(primary_key=True)
    job_info_seqno = models.PositiveIntegerField()
    server_list_seqno = models.PositiveSmallIntegerField()
    use_yn = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'job_server_map'
        unique_together = (('job_info_seqno', 'server_list_seqno'),)
        app_label = 'tmon_dba'


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
        unique_together = (('ip1', 'port1'), ('svr', 'port1'),)
        app_label = 'tmon_dba'
