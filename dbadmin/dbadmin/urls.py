from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

import login.views
import home.views
import account.views
import testing.views

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
    path('account/', account.views.account, name='account_select'),
    path('account/select_fast', account.views.account_select_fast, name='account_select_fast'),
    path('account/select_ajax', account.views.account_select_ajax, name='account_select_ajax'),
    #url(r'^list/ajax/$', home.views.post_list_ajax, name='post_list_ajax')

    path('account/insert/', account.views.account_insert, name='account_insert'),
    path('account/update/', account.views.account_update, name='account_update'),
    path('account/delete/', account.views.account_delete, name='account_delete'),

    # account Repository Manage
    path('account/repository/', account.views.account_repository, name='account_repository_select'),
    path('account/repository_insert/', account.views.account_repository_insert, name='account_repository_insert'),
    path('account/repository_update/', account.views.account_repository_update, name='account_repository_update'),
    path('account/repository_delete/', account.views.account_repository_delete, name='account_repository_delete'),

    # account test
    path('account/select_del/', account.views.account_select_del, name='account_select_del'),


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

    #graph test
    path('testing/graph/', testing.views.graph, name='graph'),

    #post test
    path('testing/post/', testing.views.post, name='post'),
    path('testing/post/select/', testing.views.post_ajax, name='post_ajax'),

    #########################################################################

]
