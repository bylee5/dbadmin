from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

import login.views
import home.views
import account.views
import testing.views
import monitoring.views

urlpatterns = [
    #url(r'^$', login.views.login),

    #########################################################################
    # django admin
    #########################################################################
    path('admin/', admin.site.urls),


    #########################################################################
    # login app
    #########################################################################
    path('', login.views.login),
    path('login/', login.views.login, name='login'),
    path('logout/', login.views.logout, name='logout'),


    #########################################################################
    # home app
    #########################################################################
    path('home/', home.views.home, name='home'),


    #########################################################################
    # account app
    #########################################################################
    # account manage
    path('account/', account.views.account, name='account'),
    path('account/select', account.views.account_select, name='account_select'),
    path('account/insert/', account.views.account_insert, name='account_insert'),
    path('account/update/', account.views.account_update, name='account_update'),
    path('account/delete/', account.views.account_delete, name='account_delete'),
    path('account/multi_dml/', account.views.account_multi_dml, name='account_multi_dml'),
    path('account/account_search_sql_list/', account.views.account_search_sql_list, name='account_search_sql_list'),

    path('account/select_fast', account.views.account_select_fast, name='account_select_fast'),

    # account remove
    path('account/account_remove', account.views.account_remove, name='account_remove'),
    path('account/account_remove_select', account.views.account_remove_select, name='account_remove_select'),

    # account Repository Manage
    path('account/repository/', account.views.account_repository, name='account_repository'),
    path('account/repository/select', account.views.account_repository_select, name='account_repository_select'),
    path('account/repository/insert', account.views.account_repository_insert, name='account_repository_insert'),
    path('account/repository/update', account.views.account_repository_update, name='account_repository_update'),


    #########################################################################
    # monitoring app
    #########################################################################

    # server_list
    path('monitoring', monitoring.views.server_list, name='server_list'),
    path('monitoring/server_list/', monitoring.views.server_list, name='server_list'),
    path('monitoring/server_list_update/', monitoring.views.server_list_update, name='server_list_update'),

    # server_job_list
    path('monitoring/server_job_list/', monitoring.views.server_job_list, name='server_job_list'),
    path('monitoring/server_job_list_update/', monitoring.views.server_job_list_update, name='server_job_list_update'),


    #########################################################################
    # testing app
    #########################################################################
    #main test
    path('testing/', testing.views.main, name='main'),

    #page test
    path('testing/page/', testing.views.page, name='page'),
    path('testing/page/insert/', testing.views.page_insert, name='page_insert'),
    path('testing/page/delete/', testing.views.page_delete, name='page_delete'),
    path('testing/page/update/', testing.views.page_update, name='page_update'),


    #main test
    path('testing/slack_test', testing.views.slack_test, name='slack_test'),

    #graph test
    path('testing/graph/', testing.views.graph, name='graph'),

    #post test
    path('testing/post/', testing.views.post, name='post'),
    path('testing/post/select/', testing.views.post_ajax, name='post_ajax'),

    #serverlist test
    path('testing/test1/', testing.views.test1, name='test1'),
    path('testing/test1/left_ajax', testing.views.test1_left_ajax, name='test1_left_ajax'),
    path('testing/test1/right_ajax', testing.views.test1_right_ajax, name='test1_right_ajax'),

    path('testing/test2/', testing.views.test2, name='test2'),

    #########################################################################

]
