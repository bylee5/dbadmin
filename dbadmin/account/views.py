from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.db import connection

from .models import *
from .forms import *

# faq_list = Faq.objects.filter(faq_id="test@test.com")
# Create your views here.

#########################################################################
# custom function
#########################################################################
# Encrypt key
def get_key():
    with open('static/other/keyfile.lst', encoding='utf-8') as txtfile:
        for row in txtfile.readlines():
            key = row

    return key

def get_password():
    with open('static/other/keyfile.lst', encoding='utf-8') as txtfile:
        for row in txtfile.readlines():
            key = row

    return key

#########################################################################
# Account page
#########################################################################
def account(request):
    if request.method == 'POST':
        account_requestor = request.POST.get('account_requestor')
        account_devteam = request.POST.get('account_devteam')
        account_svr = request.POST.get('account_svr')
        account_user = request.POST.get('account_user')
        account_host = request.POST.get('account_host')
        account_grant = request.POST.get('account_grant')
        account_db = request.POST.get('account_db')
        account_table = request.POST.get('account_table')
        account_url = request.POST.get('account_url')

        context = {
            'account_requestor': account_requestor,
            'account_devteam': account_devteam,
            'account_svr': account_svr,
            'account_user': account_user,
            'account_host': account_host,
            'account_grant': account_grant,
            'account_db': account_db,
            'account_table': account_table,
            'account_url': account_url
        }
        return render(request, 'account.html', context)

    else:
        return render(request, 'account.html')

def account_select(request):
    if request.method == 'POST':
        account_requestor = request.POST.get('account_requestor')
        account_devteam = request.POST.get('account_devteam')
        account_svr = request.POST.get('account_svr')
        account_user = request.POST.get('account_user')
        account_host = request.POST.get('account_host')
        account_grant = request.POST.get('account_grant')
        account_db = request.POST.get('account_db')
        account_table = request.POST.get('account_table')
        account_url = request.POST.get('account_url')
        callmorepostFlag = 'true'

        #account_list = Account.objects.all().order_by('-id')
        account_list = Account.objects.filter(
            account_requestor__contains=account_requestor,
            account_devteam__contains=account_devteam,
            account_svr__contains=account_svr,
            account_user__contains=account_user,
            account_host__contains=account_host,
            account_grant__contains=account_grant,
            account_db__contains=account_db,
            account_table__contains=account_table,
            account_url__contains=account_url
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
            'total_count': total_count, 'callmorepostFlag': callmorepostFlag
        }

        return render(request, 'account_select.html', context)

    else:
        return render(request, 'account.html')

def account_select_fast(request):
    if request.method == 'POST':
        account_user = request.POST.get('account_search')

        context = {
            'account_user': account_user
        }
        return render(request, 'account.html', context)

    else:
        return render(request, 'account.html')

def account_insert(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            modify_form = form.save(commit=False)

            modify_form.account_sql = "/*" + form.cleaned_data['account_url'] + \
            "*/" + " grant " + form.cleaned_data['account_grant'] + " on " + \
            form.cleaned_data['account_db'] + "." + form.cleaned_data['account_table'] + \
            " to " + "'" + form.cleaned_data['account_user'] + "'@'" + form.cleaned_data['account_host'] + \
            "' identified by '" + form.cleaned_data['account_pass'] + "';"

            # 패스워드 암호화 적용
            query = "insert ignore into account_hash(password_encrypt,password_hash)" \
                    "values (HEX(AES_ENCRYPT('" + form.cleaned_data['account_pass'] + "', '" + get_key() + "')), \
                     password('" + form.cleaned_data['account_pass'] + "'))"

            cursor = connection.cursor()
            cursor.execute(query)

            ####################################################################################################
            #query = "SELECT id, password_hash FROM account_hash WHERE password_hash=PASSWORD('" + form.cleaned_data['account_pass'] + "')"
            query = "SELECT id, password_hash FROM account_hash WHERE password_hash=PASSWORD('" + form.cleaned_data['account_pass'] + "')"

            for result in Account_hash.objects.raw(query):
                print("--------------------------------------------------------------------")
                print("query : " + query)
                print(form.cleaned_data['account_pass'])
                print("result : ")
                print(result.password_hash)
                #print("%s" % (result.password_hash))
                print("--------------------------------------------------------------------")
                modify_form.account_hash = result.password_hash

            #print("account_hash : " + account_hash)
            #cursor = connection.cursor()
            #modify_form.account_hash = cursor.execute(query)
            #print("result : " + modify_form.account_hash)

            ####################################################################################################

            # ex) /*ARCG-9999*/grant select, insert, update, delete on admdb.* to 'deal_detail'@'10.11.12.%' identified by 'password';
            #print(modify_form.account_sql)

            #SELECT password_hash FROM account_hash WHERE password_hash=PASSWORD('hoho!!kKee1');

            # 암복호화
            # select HEX(AES_ENCRYPT('Manger!1', '암복호키'));
            # select AES_DECRYPT(UNHEX('23D5F3AF5041ABADF64E89F1FCE0A994'), '암복호키');
            # grant select on admdb.* to 'test'@'10.11.22.%' identified by password '*5CE39A29BB2B3BBE6293BC10E9404F058109A152';

            #modify_form.account_sql = form.cleaned_data['account_svr']+' show '+form.cleaned_data['account_user']
            #print("============ 'sql' :" + modify_form.account_sql)

            modify_form.save()
            return redirect('/account')
        else:
            print('insert fail........................................................................')
            return redirect('/account')

    else:
        form = AccountForm()

    return render(request, 'account_insert.html', {'form': form})

def account_update(request):
    if request.method == 'POST':
        account = Account.objects.get(id=request.POST['id'])
        page = request.POST['page']
        print("========================================================== page 값 확인: " + page)
        form = AccountUpdateForm(request.POST)

        if form.is_valid():
            account.account_update_dt = datetime.now()
            account.account_requestor = form.cleaned_data['account_requestor']
            account.account_devteam = form.cleaned_data['account_devteam']
            account.account_svr = form.cleaned_data['account_svr']
            account.account_user = form.cleaned_data['account_user']
            account.account_host = form.cleaned_data['account_host']
            account.account_pass = form.cleaned_data['account_pass']
            account.account_grant = form.cleaned_data['account_grant']
            account.account_grant_with = form.cleaned_data['account_grant_with']
            account.account_db = form.cleaned_data['account_db']
            account.account_table = form.cleaned_data['account_table']
            account.account_info = form.cleaned_data['account_info']
            account.account_url = form.cleaned_data['account_url']

            account.account_sql = "/*" + form.cleaned_data['account_url'] + \
                                  "*/" + " grant " + form.cleaned_data['account_grant'] + " on " + \
                                  form.cleaned_data['account_db'] + "." + form.cleaned_data['account_table'] + \
                                  " to " + "'" + form.cleaned_data['account_user'] + "'@'" + form.cleaned_data[
                                      'account_host'] + \
                                  "' identified by '" + form.cleaned_data['account_pass'] + "';"
            account.save()

        return redirect('/account')

    else:
        form = AccountForm()

    return render(request, 'account.html', {'form': form})

def account_delete(request):
    if request.method == 'POST':
        account = Account.objects.get(id = request.POST['id']) # pk에 해당하는 업데이트 대상을 가져옴
        form = AccountDelForm(request.POST) # 입력값 가져옴

        if form.is_valid():
            #print(form.cleaned_data) # 콘솔 찍기. 디버깅

            account.account_del_yn = 'Y'
            account.account_update_dt = datetime.now()
            account.account_del_dt = datetime.now()
            account.account_del_reason = form.cleaned_data['account_del_reason']
            account.account_del_note = form.cleaned_data['account_del_note']
            account.save()

        return redirect('/account')

    else:
        form = AccountForm()

    return render(request, 'account.html', {'form': form})





#########################################################################
# Account Delete='Y' page
#########################################################################
def account_select_del(request):
    if request.method == 'POST':
        account_requestor = request.POST['account_requestor']
        account_devteam = request.POST['account_devteam']
        account_svr = request.POST['account_svr']
        account_user = request.POST['account_user']
        account_host = request.POST['account_host']
        account_grant = request.POST['account_grant']
        account_db = request.POST['account_db']
        account_table = request.POST['account_table']
        account_url = request.POST['account_url']

        #print("input val : " + account_user)

        account_list = Account.objects.filter(
            account_requestor__startswith=account_requestor,
            account_devteam__startswith=account_devteam,
            account_svr__startswith=account_svr,
            account_user__contains=account_user,
            account_host__startswith=account_host,
            account_grant__contains=account_grant,
            account_db__startswith=account_db,
            account_table__startswith=account_table,
            account_url__contains=account_url,
            account_del_yn='Y' # 계정 삭제여부

        ).order_by('-id')

        page = request.GET.get('page')
        pagelist = request.GET.get('pagelist')

        if pagelist is None:
            pagelist = 15

        #print(pagelist)
        paginator = Paginator(account_list, pagelist)
        accounts = paginator.get_page(page)
        context = {'accounts': accounts, 'pagelist': pagelist}
        return render(request, 'account_select_del.html', context)

    else:
        #account_list = Account.objects.all().order_by('-id')
        page = request.GET.get('page')
        pagelist = request.GET.get('pagelist')

        if pagelist is None:
            pagelist = 15

        account_list = Account.objects.filter(account_del_yn='Y').order_by('-id')
        paginator = Paginator(account_list, pagelist)
        accounts = paginator.get_page(page)
        context = {'accounts': accounts, 'pagelist': pagelist}
        return render(request, 'account_select_del.html', context)

def account_fn_search(request):
    if request.method == 'POST':
        faq_list = Faq.objects.filter(faq_id="test@test.com")
        paginator = Paginator(faq_list, 10)
        page = request.GET.get('page')
        faqs = paginator.get_page(page)
        context = {'faqs' : faqs}
    return render(request, 'account.html', context)


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

