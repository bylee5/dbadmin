# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountAccount(models.Model):
    account_create_dt = models.DateTimeField()
    account_update_dt = models.DateTimeField()
    account_end_dt = models.DateTimeField(blank=True, null=True)
    account_requestor = models.CharField(max_length=100)
    account_devteam = models.CharField(max_length=100)
    account_svr = models.CharField(max_length=100)
    account_user = models.CharField(max_length=50)
    account_host = models.CharField(max_length=100)
    account_pass = models.CharField(max_length=100)
    account_hash = models.CharField(max_length=100)
    account_grant = models.CharField(max_length=100)
    account_grant_with = models.CharField(max_length=100)
    account_db = models.CharField(max_length=100)
    account_table = models.CharField(max_length=100)
    account_info = models.CharField(max_length=100)
    account_sql = models.CharField(max_length=200)
    account_url = models.CharField(max_length=100)
    account_del_yn = models.CharField(max_length=100)
    account_del_dt = models.DateTimeField(blank=True, null=True)
    account_del_reason = models.CharField(max_length=100)
    account_del_note = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'account_account'


class AccountFaq(models.Model):
    faq_id = models.CharField(max_length=16)
    faq_type = models.CharField(max_length=10)
    faq_question = models.TextField()
    faq_answer = models.TextField()

    class Meta:
        managed = False
        db_table = 'account_faq'


class AccountHash(models.Model):
    password_encrypt = models.CharField(unique=True, max_length=100)
    password_hash = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'account_hash'


class AccountRepository(models.Model):
    create_dt = models.DateTimeField()
    repository_team = models.CharField(max_length=20)
    repository_name = models.CharField(max_length=100)
    repository_url = models.CharField(max_length=250)
    account_user = models.CharField(max_length=50)
    url = models.CharField(max_length=100)
    info = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'account_repository'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


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


class TestingFaq(models.Model):
    faq_id = models.CharField(max_length=16)
    faq_type = models.CharField(max_length=10)
    faq_question = models.TextField()
    faq_answer = models.TextField()

    class Meta:
        managed = False
        db_table = 'testing_faq'


class TestingPost(models.Model):
    created = models.DateTimeField()
    title = models.CharField(max_length=50)
    content = models.TextField()
    read = models.IntegerField()
    likes = models.IntegerField()
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'testing_post'
