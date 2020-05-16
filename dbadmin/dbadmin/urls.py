from django.contrib import admin
from django.urls import path, include
import login.views
import home.views
import account.views
from django.conf.urls import url

urlpatterns = [
    #url(r'^$', login.views.login),

    path('admin/', admin.site.urls),
    path('', login.views.login),

    #########################################################################
    # login app
    #########################################################################
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
    # test
    #########################################################################
    path('home/test/', home.views.test, name='test_select'),

    path('home/test/insert/', home.views.test_insert, name='test_insert'),
    path('home/test/delete/', home.views.test_delete, name='test_delete'),
    path('home/test/update/', home.views.test_update, name='test_update'),

    path('home/test1/', home.views.test1, name='test1'),
    path('home/testGraph/', home.views.testGraph, name='testGraph'),


    #post test
    path('home/post/', home.views.post_list, name='post_list'),
    path('home/post/select/', home.views.post_list_ajax, name='post_list_ajax'),

    #########################################################################

]
