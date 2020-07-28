from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.db import connection
from django.templatetags.static import static
from django.utils import timezone
from django.conf import settings, os
from django.contrib.auth.decorators import login_required
from django.db import connections

from .models import *
from .forms import *
from django.template import Context, Engine, TemplateDoesNotExist, loader

#########################################################################
# custom function
#########################################################################
# Encrypt key
# test
def get_key():
    #file_path = os.path.join(settings.KEY_URL, 'other/keyfile.lst')
    #with open(file_path, encoding='utf-8') as txtfile:
    #    for row in txtfile.readlines():
    #        key = row
    key = settings.ENC_KEY

    return key

def get_password(account_pass):
    query = "SELECT id, password_hash FROM account_hash WHERE password_hash=PASSWORD('" + account_pass + "') limit 0,1"

    for result in Account_hash.objects.raw(query):
       return result.password_hash

def put_password(account_pass):
    query = "insert ignore into account_hash(password_encrypt,password_hash)" \
            "values (HEX(AES_ENCRYPT('" + account_pass + "', '" + get_key() + "')), \
             password('" + account_pass + "'))"

    cursor = connection.cursor()
    cursor.execute(query)

@login_required

#########################################################################
# fast select
#########################################################################
def account_select_fast(request):
    if request.method == 'POST':
        account_user = request.POST.get('account_search')

        context = {
            'account_user': account_user,
            'page' : 50
        }
        return render(request, 'account.html', context)

    else:
        return render(request, 'account.html')

#########################################################################
# Account page
#########################################################################
def account(request):
    account_svr_list = Account.objects.all().filter(account_del_yn='N').order_by('account_svr').values('account_svr').distinct()

    context = {
        'account_svr_list': account_svr_list
    }

    return render(request, 'account.html', context)

def account_select(request):
    if request.method == 'POST':
        account_requestor = request.POST.get('s_account_requestor')
        account_devteam = request.POST.get('s_account_devteam')
        account_svr = request.POST.get('s_account_svr')
        account_user = request.POST.get('s_account_user')
        account_host = request.POST.get('s_account_host')
        account_grant = request.POST.get('s_account_grant')
        account_db = request.POST.get('s_account_db')
        account_table = request.POST.get('s_account_table')
        account_url = request.POST.get('s_account_url')
        callmorepostFlag = 'true'

        account_list = Account.objects.filter(
            account_requestor__contains=account_requestor,
            account_devteam__contains=account_devteam,
            account_svr__contains=account_svr,
            account_user__contains=account_user,
            account_host__contains=account_host,
            account_grant__contains=account_grant,
            account_db__contains=account_db,
            account_table__contains=account_table,
            account_url__contains=account_url,
            account_del_yn = 'N'
		).order_by('-id')

        page = int(request.POST.get('page'))
        total_count = account_list.count()
        page_max = round(account_list.count() / 15)
        paginator = Paginator(account_list, page * 15)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                account_list = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                account_list = paginator.get_page(1)
        except PageNotAnInteger:
            account_list = paginator.get_page(1)
        except EmptyPage:
            account_list = paginator.get_page(paginator.num_pages)

        context = {
            'account_requestor': account_requestor,
            'account_devteam': account_devteam,
            'account_svr': account_svr,
            'account_user': account_user,
            'account_host': account_host,
            'account_grant': account_grant,
            'account_db': account_db,
            'account_table': account_table,
            'account_url': account_url,
            'account_list': account_list,
            'total_count': total_count, 'callmorepostFlag': callmorepostFlag,
            'page_max': page_max
        }

        return render(request, 'account_select.html', context)

    else:
        return render(request, 'account.html')

def account_insert(request):

    if request.method == 'POST':
        account_requestor = request.POST.get('i_account_requestor')
        account_devteam = request.POST.get('i_account_devteam')
        account_info = request.POST.get('i_account_info')
        account_url = request.POST.get('i_account_url')
        account_svr = request.POST.get('i_account_svr')
        account_user = request.POST.get('i_account_user')
        account_host = request.POST.get('i_account_host')
        account_pass = request.POST.get('i_account_pass')
        account_db = request.POST.get('i_account_db')
        account_table = request.POST.get('i_account_table')
        account_grant = request.POST.get('i_account_grant')
        account_grant_direct = request.POST.get('i_account_grant_direct')

        if account_grant == '':  # 권한 직접 입력인경우
            account_grant = request.POST.get('i_account_grant_direct')

        # 패스워드 암호화 적용
        put_password(account_pass)
        account_hash = get_password(account_pass)

        # print("============================================================")
        # print("입력란 테스트 선입니다.")
        # print("============================================================")
        # print(account_requestor)
        # print(account_devteam)
        # print(account_info)
        # print(account_url)
        # print(account_svr)
        # print(account_user)
        # print(account_host)
        # print(account_pass)
        # print(account_db)
        # print(account_table)
        # print(account_grant)
        # print(account_hash)
        # print("============================================================")

        # HOST 여러대역 처리
        account_host_lists = account_host.split(',')

        for account_host_list in account_host_lists:
            account_host = account_host_list.replace(" ", "")

            account_sql = "/*" + account_url + \
                            "*/" + " grant " + account_grant  + " on " + \
                            account_db + "." + account_table + \
                            " to " + "'" + account_user + "'@'" + account_host + \
                            "' identified by '" + account_pass + "';"
            # print("host : " + account_host)
            # print("sql : " + account_sql)

            insert_sql = "insert into account_account(account_create_dt, account_update_dt, \
            account_requestor, account_devteam, account_svr, account_user, \
            account_host, account_pass, account_hash, account_grant, account_grant_with, \
            account_db, account_table, account_info, account_sql, account_url, account_del_yn, account_del_reason, account_del_note) values( \
            now(), \
            now(), \
            '" + account_requestor + "', \
            '" + account_devteam + "', \
            '" + account_svr + "', \
            '" + account_user + "', \
            '" + account_host + "', \
            '" + account_pass + "', \
            '" + account_hash + "', \
            '" + account_grant + "', \
            'N', \
            '" + account_db + "', \
            '" + account_table + "', \
            '" + account_info + "', " + \
            '"' + account_sql + '"' + ", \
            '" + account_url + "', \
            'N','','')"

            # print("insert_sql : " + insert_sql)

            try:
                cursor = connections['default'].cursor()
                cursor.execute(insert_sql)
                connection.commit()
            finally:
                cursor.close()

        # print("============================================================")

            ####################################################################################################
            # ex) /*ARCG-9999*/grant select, insert, update, delete on admdb.* to 'deal_detail'@'10.11.12.%' identified by 'password';
            #print(modify_form.account_sql)

            # 계정 생성 예제
            # GRANT SELECT ON `testdb`.* TO 'test'@'10.11.20.%' IDENTIFIED BY PASSWORD '*6A654172F7C08BAA30B145980AA553792E9DFFC3';
            # GRANT SELECT ON `testdb`.* TO 'test'@'10.11.22.%' IDENTIFIED WITH 'mysql_native_password' AS '*6A654172F7C08BAA30B145980AA553792E9DFFC3';
            # CREATE USER 'test'@'10.11.19.%' IDENTIFIED WITH 'mysql_native_password' AS '*6A654172F7C08BAA30B145980AA553792E9DFFC3

            # SELECT password_hash FROM account_hash WHERE password_hash=PASSWORD('hoho!!kKee1');

            # 암복호화
            # select HEX(AES_ENCRYPT('Manger!1', '암복호키'));
            # select AES_DECRYPT(UNHEX('23D5F3AF5041ABADF64E89F1FCE0A994'), '암복호키');
            # grant select on admdb.* to 'test'@'10.11.22.%' identified by password '*5CE39A29BB2B3BBE6293BC10E9404F058109A152';
            ####################################################################################################

        callmorepostFlag = 'true'

        account_list = Account.objects.filter(
            account_user__contains=account_user,
            account_del_yn='N'
        ).order_by('-id')

        page = int(request.POST.get('page'))
        total_count = account_list.count()
        page_max = round(account_list.count() / 15)
        paginator = Paginator(account_list, page * 15)

        try:
            if int(page) >= page_max:  # 마지막 페이지 멈춤 구현
                account_list = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                account_list = paginator.get_page(1)
        except PageNotAnInteger:
            account_list = paginator.get_page(1)
        except EmptyPage:
            account_list = paginator.get_page(paginator.num_pages)

        # alert 테스트
        alert_type = 1

        context = {
            'account_user': account_user,
            'account_list': account_list,
            'total_count': total_count, 'callmorepostFlag': callmorepostFlag,
            'page_max': page_max,
            'alert_type': alert_type
        }

        return render(request, 'account_select.html', context)

    else:
        return render(request, 'account.html')

def account_update(request):
    if request.method == 'POST':

        #### UPDATE
        u_id = request.POST.get('u_id')
        u_account_requestor = request.POST.get('u_account_requestor');
        u_account_svr = request.POST.get('u_account_svr');
        u_account_user = request.POST.get('u_account_user');
        u_account_devteam = request.POST.get('u_account_devteam');
        u_account_host = request.POST.get('u_account_host');
        u_account_pass = request.POST.get('u_account_pass');
        u_account_grant = request.POST.get('u_account_grant');
        u_account_grant_with = request.POST.get('u_account_grant_with');
        u_account_db = request.POST.get('u_account_db');
        u_account_table = request.POST.get('u_account_table');
        u_account_info = request.POST.get('u_account_info');
        u_account_url = request.POST.get('u_account_url');

        u_account_sql = "/*" + u_account_svr + "*/ " + "use mysql; " + "/*" + u_account_url + \
                              "*/" + " grant " + u_account_grant + " on " + \
                              u_account_db + "." + u_account_table + \
                              " to " + "'" + u_account_user + "'@'" + u_account_host + \
                              "' identified by '" + u_account_pass + "';"

        put_password(u_account_pass)
        u_account_hash = get_password(u_account_pass)

        # print(u_id)

        update_sql = "update account_account " + \
        "set account_update_dt = now() " + \
        ", account_requestor = " + "'" + u_account_requestor + "'" + \
        ", account_devteam = " + "'" + u_account_devteam + "'" + \
        ", account_info = " + "'" + u_account_info + "'" + \
        ", account_url = " + "'" + u_account_url + "'" + \
        ", account_svr = " + "'" + u_account_svr + "'" + \
        ", account_user = " + "'" + u_account_user + "'" + \
        ", account_host = " + "'" + u_account_host + "'" + \
        ", account_pass = " + "'" + u_account_pass + "'" + \
        ", account_db = " + "'" + u_account_db + "'" + \
        ", account_table = " + "'" + u_account_table + "'" + \
        ", account_grant = " + "'" + u_account_grant + "'" + \
        ", account_grant_with = " + "'" + u_account_grant_with + "'" + \
        ", account_sql = " + '"' + u_account_sql + '"' + \
        ", account_hash = " + "'" + u_account_hash + "'" + \
        " where id = " + u_id + ";"

        # print("============================================================")
        # print("UPDATE 리턴값 테스트 선입니다.")
        # print("============================================================")
        # print(u_id)
        # print(u_account_requestor)
        # print(u_account_devteam)
        # print(u_account_info)
        # print(u_account_url)
        # print(u_account_svr)
        # print(u_account_user)
        # print(u_account_host)
        # print(u_account_pass)
        # print(u_account_db)
        # print(u_account_table)
        # print(u_account_grant)
        # print(u_account_grant_with)
        # print("============================================================")
        # print("수정본 u_account_sql : " + u_account_sql)
        # print("수정본 account_hash: " + u_account_hash)
        # print(update_sql)
        # print("============================================================")

        try:
            cursor = connections['default'].cursor()
            cursor.execute(update_sql)
            connection.commit()
        finally:
            cursor.close()

        ########################################## 페이지 원래대로 테스트

        account_requestor = request.POST.get('s_account_requestor')
        account_devteam = request.POST.get('s_account_devteam')
        account_svr = request.POST.get('s_account_svr')
        account_user = request.POST.get('s_account_user')
        account_host = request.POST.get('s_account_host')
        account_grant = request.POST.get('s_account_grant')
        account_db = request.POST.get('s_account_db')
        account_table = request.POST.get('s_account_table')
        account_url = request.POST.get('s_account_url')
        callmorepostFlag = 'true'

        # print("검색란 리턴값 테스트 선입니다.")
        # print("============================================================")
        # print(account_requestor)
        # print(account_devteam)
        # print(account_svr)
        # print(account_user)
        # print(account_host)
        # print(account_grant)
        # print(account_db)
        # print(account_table)
        # print(account_url)
        # print("============================================================")

        account_list = Account.objects.filter(
            account_requestor__contains=account_requestor,
            account_devteam__contains=account_devteam,
            account_svr__contains=account_svr,
            account_user__contains=account_user,
            account_host__contains=account_host,
            account_grant__contains=account_grant,
            account_db__contains=account_db,
            account_table__contains=account_table,
            account_url__contains=account_url,
            account_del_yn='N'
        ).order_by('-id')

        page = int(request.POST.get('page'))
        total_count = account_list.count()
        page_max = round(account_list.count() / 15)
        paginator = Paginator(account_list, page * 15)

        try:
            if int(page) >= page_max:  # 마지막 페이지 멈춤 구현
                account_list = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                account_list = paginator.get_page(1)
        except PageNotAnInteger:
            account_list = paginator.get_page(1)
        except EmptyPage:
            account_list = paginator.get_page(paginator.num_pages)

        context = {
            'account_requestor': account_requestor,
            'account_devteam': account_devteam,
            'account_svr': account_svr,
            'account_user': account_user,
            'account_host': account_host,
            'account_grant': account_grant,
            'account_db': account_db,
            'account_table': account_table,
            'account_url': account_url,
            'account_list': account_list,
            'total_count': total_count, 'callmorepostFlag': callmorepostFlag,
            'page_max': page_max
        }

        return render(request, 'account_select.html', context)


    else:
        return render(request, 'account.html')


def account_delete(request):
    if request.method == 'POST':

        #### DELETE
        d_id = request.POST.get('d_id')
        d_account_requestor = request.POST.get('d_account_requestor');
        d_account_svr = request.POST.get('d_account_svr');
        d_account_user = request.POST.get('d_account_user');
        d_account_devteam = request.POST.get('d_account_devteam');
        d_account_host = request.POST.get('d_account_host');
        d_account_pass = request.POST.get('d_account_pass');
        d_account_grant = request.POST.get('d_account_grant');
        d_account_grant_with = request.POST.get('d_account_grant_with');
        d_account_db = request.POST.get('d_account_db');
        d_account_table = request.POST.get('d_account_table');
        d_account_info = request.POST.get('d_account_info');
        d_account_url = request.POST.get('d_account_url');
        d_account_del_reason = request.POST.get('d_account_del_reason');
        d_account_del_note = request.POST.get('d_account_del_note');

        # print("============================================================")
        # print("DELETE 리턴값 테스트 선입니다.")
        # print("============================================================")
        # print(d_id)
        # print(d_account_requestor)
        # print(d_account_devteam)
        # print(d_account_info)
        # print(d_account_url)
        # print(d_account_svr)
        # print(d_account_user)
        # print(d_account_host)
        # print(d_account_pass)
        # print(d_account_db)
        # print(d_account_table)
        # print(d_account_grant)
        # print(d_account_grant_with)
        # print(d_account_del_reason)
        # print(d_account_del_note)
        # print("============================================================")

        delete_sql = "update account_account " + \
        "set account_del_dt = now() " + \
        ", account_del_yn = 'Y' " + \
        ", account_del_reason = " + "'" + d_account_del_reason+ "'" + \
        ", account_del_note = " + "'" + d_account_del_note + "'" + \
        " where id = " + d_id + ";"

        # print(delete_sql)
        # print("============================================================")

        try:
            cursor = connections['default'].cursor()
            cursor.execute(delete_sql)
            connection.commit()
        finally:
            cursor.close()

        ########################################## 페이지 원래대로 테스트

        account_requestor = request.POST.get('s_account_requestor')
        account_devteam = request.POST.get('s_account_devteam')
        account_svr = request.POST.get('s_account_svr')
        account_user = request.POST.get('s_account_user')
        account_host = request.POST.get('s_account_host')
        account_grant = request.POST.get('s_account_grant')
        account_db = request.POST.get('s_account_db')
        account_table = request.POST.get('s_account_table')
        account_url = request.POST.get('s_account_url')
        callmorepostFlag = 'true'

        # print("검색란 리턴값 테스트 선입니다.")
        # print("============================================================")
        # print(account_requestor)
        # print(account_devteam)
        # print(account_svr)
        # print(account_user)
        # print(account_host)
        # print(account_grant)
        # print(account_db)
        # print(account_table)
        # print(account_url)
        # print("============================================================")

        account_list = Account.objects.filter(
            account_requestor__contains=account_requestor,
            account_devteam__contains=account_devteam,
            account_svr__contains=account_svr,
            account_user__contains=account_user,
            account_host__contains=account_host,
            account_grant__contains=account_grant,
            account_db__contains=account_db,
            account_table__contains=account_table,
            account_url__contains=account_url,
            account_del_yn='N'
        ).order_by('-id')

        page = int(request.POST.get('page'))
        total_count = account_list.count()
        page_max = round(account_list.count() / 15)
        paginator = Paginator(account_list, page * 15)

        try:
            if int(page) >= page_max:  # 마지막 페이지 멈춤 구현
                account_list = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                account_list = paginator.get_page(1)
        except PageNotAnInteger:
            account_list = paginator.get_page(1)
        except EmptyPage:
            account_list = paginator.get_page(paginator.num_pages)

        context = {
            'account_requestor': account_requestor,
            'account_devteam': account_devteam,
            'account_svr': account_svr,
            'account_user': account_user,
            'account_host': account_host,
            'account_grant': account_grant,
            'account_db': account_db,
            'account_table': account_table,
            'account_url': account_url,
            'account_list': account_list,
            'total_count': total_count, 'callmorepostFlag': callmorepostFlag,
            'page_max': page_max
        }

        return render(request, 'account_select.html', context)


    else:
        return render(request, 'account.html')

#########################################################################
# Account Delete='Y' page
#########################################################################

def account_remove(request):
    account_svr_list = Account.objects.all().filter(account_del_yn='Y').order_by('account_svr').values('account_svr').distinct()

    context = {
        'account_svr_list': account_svr_list
    }

    return render(request, 'account_remove.html', context)

def account_remove_select(request):
    if request.method == 'POST':
        account_requestor = request.POST.get('s_account_requestor')
        account_devteam = request.POST.get('s_account_devteam')
        account_svr = request.POST.get('s_account_svr')
        account_user = request.POST.get('s_account_user')
        account_host = request.POST.get('s_account_host')
        account_grant = request.POST.get('s_account_grant')
        account_db = request.POST.get('s_account_db')
        account_table = request.POST.get('s_account_table')
        account_url = request.POST.get('s_account_url')
        callmorepostFlag = 'true'

        account_list = Account.objects.filter(
            account_requestor__contains=account_requestor,
            account_devteam__contains=account_devteam,
            account_svr__contains=account_svr,
            account_user__contains=account_user,
            account_host__contains=account_host,
            account_grant__contains=account_grant,
            account_db__contains=account_db,
            account_table__contains=account_table,
            account_url__contains=account_url,
            account_del_yn = 'Y'
		).order_by('-account_del_dt')

        page = int(request.POST.get('page'))
        total_count = account_list.count()
        page_max = round(account_list.count() / 15)
        paginator = Paginator(account_list, page * 15)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                account_list = paginator.get_page(1)
                callmorepostFlag = 'false'
            else:
                account_list = paginator.get_page(1)
        except PageNotAnInteger:
            account_list = paginator.get_page(1)
        except EmptyPage:
            account_list = paginator.get_page(paginator.num_pages)

        context = {
            'account_requestor': account_requestor,
            'account_devteam': account_devteam,
            'account_svr': account_svr,
            'account_user': account_user,
            'account_host': account_host,
            'account_grant': account_grant,
            'account_db': account_db,
            'account_table': account_table,
            'account_url': account_url,
            'account_list': account_list,
            'total_count': total_count, 'callmorepostFlag': callmorepostFlag,
            'page_max': page_max
        }

        return render(request, 'account_remove_select.html', context)

    else:
        return render(request, 'account_remove.html')



#########################################################################
# Account repository page
#########################################################################
def account_repository(request):
    if request.method == 'POST':
        repository_team = request.POST['repository_team']
        repository_name = request.POST['repository_name']
        repository_url = request.POST['repository_url']
        account_user = request.POST['account_user']
        url = request.POST['url']
        info = request.POST['info']

        account_repository_list = AccountRepository.objects.filter(
            repository_team__contains=repository_team,
            repository_name__contains=repository_name,
            repository_url__contains=repository_url,
            account_user__contains=account_user,
            url__contains=url,
            info__contains=info,
        ).order_by('-create_dt')

        page = request.GET.get('page')

        paginator = Paginator(account_repository_list, 15)
        account_repositories = paginator.get_page(page)
        context = {'account_repositories': account_repositories}
        return render(request, 'account_repository.html', context)

    else:
        page = request.GET.get('page')

        account_repository_list = AccountRepository.objects.all().order_by('-create_dt')
        paginator = Paginator(account_repository_list, 15)
        account_repositories = paginator.get_page(page)
        context = {'account_repositories': account_repositories}
        return render(request, 'account_repository.html', context)

def account_repository_insert(request):
    if request.method == 'POST':
        form = AccountRepositoryForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/account/repository')
    else:
        form = AccountRepositoryForm()

    return render(request, 'account_repository.html', {'form': form})

def account_repository_update(request):
    if request.method == 'POST':
        getObject = AccountRepository.objects.get(id = request.POST['id']) # pk에 해당하는 업데이트 대상을 가져옴
        form = AccountRepositoryForm(request.POST) # 입력값 가져옴
        #print('url : ' + form.cleaned_data['repository_url'])

        if form.is_valid():
            getObject.repository_team = form.cleaned_data['repository_team']
            getObject.repository_name = form.cleaned_data['repository_name']
            getObject.repository_url = form.cleaned_data['repository_url']
            getObject.account_user = form.cleaned_data['account_user']
            getObject.url = form.cleaned_data['url']
            getObject.info = form.cleaned_data['info']
            getObject.save()

        return redirect('/account/repository')

    else:
        form = AccountRepositoryForm()

    return render(request, 'account_repository.html', {'form': form})

def account_repository_delete(request):
    if request.method == 'POST':
        getObject = AccountRepository.objects.get(id = request.POST['id'])
        getObject.delete()
        return redirect('/account/repository')

    return render(request, 'account_repository.html')

