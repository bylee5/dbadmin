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
from django.http import JsonResponse
import time

from .models import *
from .forms import FaqForm
from django.template import Context, Engine, TemplateDoesNotExist, loader
import socket, struct
import math

from collections import namedtuple
from slacker import Slacker

@login_required

#########################################################################
# main page
#########################################################################
# Create your views here.
def main(request):
    return render(request, 'test_main.html')

#########################################################################
# custom function
#########################################################################
# 테스팅 용도
def get_key():
    with open('static/other/keyfile.lst', encoding='utf-8') as txtfile:
        for row in txtfile.readlines():
            key = row

    return key

#########################################################################
# testing page
#########################################################################

def page(request):
    if request.method == 'POST':
        faq_id= request.POST['faq_id']
        faq_type= request.POST['faq_type']
        faq_question= request.POST['faq_question']
        faq_answer= request.POST['faq_answer']

        faq_list = Faq.objects.filter(
            faq_id__startswith=faq_id,
            faq_type__startswith=faq_type,
            faq_question__startswith=faq_question,
            faq_answer__startswith=faq_answer
        ).order_by('-id')

        paginator = Paginator(faq_list, 15)
        page = request.GET.get('page')
        faqs = paginator.get_page(page)
        context = {'faqs': faqs}
        return render(request, 'test_page.html', context)

    else:
        faq_list = Faq.objects.all().order_by('-id')
        paginator = Paginator(faq_list, 15)
        page = request.GET.get('page')
        faqs = paginator.get_page(page)
        context = {'faqs': faqs}
        return render(request, 'test_page.html', context)


def page_insert(request):
    if request.method == 'POST':
        form = FaqForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/testing/page')
    else:
        form = FaqForm()

    return render(request, 'test_page.html', {'form': form})


def page_delete(request):
    if request.method == 'POST':
        getObject= Faq.objects.get(id = request.POST['id'])
        getObject.delete()
        return redirect('/testing/page')

    return render(request, 'test_page.html')

def page_update(request):
    if request.method == 'POST':
        getObject = Faq.objects.get(id = request.POST['id']) # pk에 해당하는 업데이트 대상을 가져옴
        form = FaqForm(request.POST) # 입력값 가져옴

        if form.is_valid():
            #print(form.cleaned_data) # 콘솔 찍기. 디버깅

            getObject.faq_id = form.cleaned_data['faq_id']
            getObject.faq_type = form.cleaned_data['faq_type']
            getObject.faq_question = form.cleaned_data['faq_question']
            getObject.faq_answer = form.cleaned_data['faq_answer']
            getObject.save()

        return redirect('/testing/page')

    else:
        form = FaqForm()

    return render(request, 'test_page.html', {'form': form})


#########################################################################
# testing graph
#########################################################################

def graph(request):
    # query = "SELECT DATE(account_create_dt) AS account_create_dt, account_svr, COUNT(*) AS account_create_cnt" + \
    #         " FROM account_account" + \
    #         " GROUP BY DATE(account_create_dt), account_svr"

    # query = "SELECT DATE(account_create_dt) AS account_create_dt, COUNT(*) AS account_create_cnt" + \
    #         " FROM account_account" + \
    #         " GROUP BY DATE(account_create_dt)"
    # QUERY JSON 타입으로 변환 쿼리
    query = "SELECT JSON_ARRAY(GROUP_CONCAT(a.account_create_dt)) AS account_create_dt, JSON_ARRAY(GROUP_CONCAT(a.account_create_cnt)) AS account_create_cnt" + \
            " FROM (	SELECT DATE(account_create_dt) AS account_create_dt, COUNT(*) AS account_create_cnt" + \
            " FROM account_account" + \
	        " GROUP BY DATE(account_create_dt)) a"

    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        account_stat = namedtuplefetchall(cursor)
    print("===========================================")
    print(account_stat)
    print("===========================================")

    context = {
        'account_stat': account_stat,
        'Title': 'Account Create Count',
    }

    return render(request, 'test_graph.html', context)

def graph_test(request):
    print("graph_test");
    # query = "SELECT JSON_ARRAY(GROUP_CONCAT(a.account_create_dt)) AS account_create_dt, JSON_ARRAY(GROUP_CONCAT(a.account_create_cnt)) AS account_create_cnt" + \
    #         " FROM (	SELECT DATE(account_create_dt) AS account_create_dt, COUNT(*) AS account_create_cnt" + \
    #         " FROM account_account" + \
    #         " GROUP BY DATE(account_create_dt)) a"

    query = "SELECT DATE(account_create_dt) AS account_create_dt, COUNT(*) AS account_create_cnt" + \
            " FROM account_account" + \
            " GROUP BY DATE(account_create_dt)"

    query = "SELECT DATE_FORMAT(account_create_dt,'%y/%m/%d %H:%m:%i'), COUNT(*) AS account_create_cnt" + \
            " FROM account_account" + \
            " GROUP BY DATE_FORMAT(account_create_dt,'%y/%m/%d %H:%m:%i')"

    query = "SELECT create_dt, COUNT(*) as cnt, ROUND(RAND()*10,0) FROM account_history GROUP BY create_dt"

    # query = "SELECT account_svr AS account_svr, COUNT(*) AS account_cnt" + \
    #         " FROM account_account" + \
    #         " GROUP BY account_svr" + \
    #         " ORDER BY account_svr"

    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

        key = []
        value1 = []
        value2 = []

        for row in rows:
            key.append(row[0])
            value1.append(row[1])
            value2.append(row[2])

    # print("===========================================================")
    # print(key)
    # print(value)
    # print("==========================================================")

    context = {
        'key': key,
        'value1': value1,
        'value2': value2
    }
    return JsonResponse(context)



#########################################################################
# testing post
# AJAX UnLimit Scrolling Test
#########################################################################

def post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        read = request.POST.get('read')

        read_list = Post.objects.all().order_by('read').values('read').distinct()
        context = {'read_list': read_list, 'title': title, 'content': content, 'read': read}
        return render(request, 'test_post.html', context)

    else:
        read_list = Post.objects.all().order_by('read').values('read').distinct()
        context = {'read_list': read_list}
        return render(request, 'test_post.html', context)

    #try:
    #    post_list = paginator.page(page)
    #except PageNotAnInteger:
    #    post_list = paginator.page(1)
    #except EmptyPage:
    #    post_list = paginator.page(paginator.num_pages)

    #title = request.POST['title']
    #content = request.POST['content']
    #callmorepostFlag = 'true'

    #context = {'post_list': post_list}
    #context = {'post_list': post_list, 'callmorepostFlag': callmorepostFlag,
    #           'title': title, 'content': content}
    #return render(request, 'test_post_ajax.html', context)

def post_ajax(request): #Ajax 로 호출하는 함수

    if request.method == 'POST':

        title = request.POST.get('title')
        content = request.POST.get('content')
        read = request.POST.get('read')
        callmorepostFlag = 'true'

        print("--------------------------------------------------------------------------------------------------- read : " + read)

        post_list = Post.objects.filter(
            title__contains=title,
			content__contains=content,
            read__contains=read
		).order_by('-id')

        page = int(request.POST.get('page'))

        #print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        #print("ajax 타이틀 : " + str(title))
        #print("ajax 컨텐츠 : " + str(content))
        #print("page : " + str(page))
        total_count = post_list.count()
        page_max = round(post_list.count() / 15)

        #print("count : " + str(total_count))
        #print("page max : " + str(page_max))
        #print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

        paginator = Paginator(post_list, page * 15)

        try:
            if int(page) >= page_max : # 마지막 페이지 멈춤 구현
                post_list = paginator.get_page(1)
                callmorepostFlag = 'false'

            else:
                post_list = paginator.get_page(1)

        except PageNotAnInteger:
            post_list = paginator.get_page(1)
        except EmptyPage:
            post_list = paginator.get_page(paginator.num_pages)

        context = {'post_list': post_list,
                   'total_count': total_count, 'callmorepostFlag': callmorepostFlag,
                   'title': title, 'content': content, 'read': read}
        return render(request, 'test_post_ajax.html', context)

    else:
        return render(request, 'test_post.html')

#########################################################################
# server_list test
#########################################################################
def namedtuplefetchall(cursor):
    #"Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def test1(request):
    return render(request, 'test1.html')

def test1_left_ajax(request):
    if request.method == 'POST':
        s_job_name = request.POST.get('s_job_name')

        # print("-------------------------------------------------------------")
        # print(s_job_name)

        if s_job_name is None:
            s_job_name=''

        # 잡 리스트 및 JOB 스케줄 가져오기
        s_query = "/*left*/SELECT ji.job_info_name, COUNT(svr) AS svr_total, IFNULL(SUM(use_yn),0) AS svr_use_total" + \
                    " FROM server_list sl" + \
                    " INNER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno" + \
                    " RIGHT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                    " where ji.job_info_name like '%" + s_job_name + "%'" + \
                    " GROUP BY ji.job_info_name" + \
                    " ORDER BY ji.job_info_name"
        # print(s_query)
        # print("-------------------------------------------------------------")

        with connections['tmon_dba'].cursor() as cursor:
            job_info_lists = []
            cursor.execute(s_query)
            job_info_lists = namedtuplefetchall(cursor)

        # print("============= count ================")
        # print(len(job_info_lists))

        context = {
            'job_info_lists': job_info_lists,
            's_job_name': s_job_name,
        }

        return render(request, 'test1_left_ajax.html', context)

    else:
        return render(request, 'test1_left_ajax.html')


def test1_right_ajax(request):
    if request.method == 'POST':

        job_info_names = request.POST.getlist('job_info_name[]') # 원래 입력값
        job_info_name = ", ".join( repr(e) for e in job_info_names) # QUERY에 쓰일 JOB_NAME 값

        s_svr = request.POST.get('s_svr') # 원래 입력값
        checkbox_unregister = request.POST.get('checkbox_unregister') # 원래 입력값
        checkbox_off = request.POST.get('checkbox_off') # 원래 입력값

        # print("-------------------------------------------------------------")
        # print("right POST 테스트")
        # print("-------------------------------------------------------------")
        # print(job_info_names)
        # print("s_svr : " + str(s_svr))
        # print("checkbox_unregister : " + str(checkbox_unregister))
        # print("checkbox_off : " + str(checkbox_off))
        # print("-------------------------------------------------------------")
        if s_svr is None:
            s_svr=''

        if len(job_info_names) == 0:
            # print("비어있는 값 입력")
            job_svr_lists = ''
            job_info_name = "''"

        else:
            job_svr_lists = []
            for job_name in job_info_names:
                if checkbox_off =='ON':
                    str_checkbox_off = " AND use_yn=1"
                else:
                    str_checkbox_off = ""

                # 미등록 안보기 ON
                if checkbox_unregister == 'ON':
                    s_query =   "/*right*/SELECT ji.job_info_name, REPLACE(sl.svr,'.tmonc.net','') AS svr, jsm.use_yn" + \
                                " FROM server_list sl" + \
                                " INNER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno" + \
                                " RIGHT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                                " WHERE 1=1" + \
                                " AND sl.svr IS NOT NULL AND jsm.use_yn IS NOT NULL" + \
                                " AND ji.job_info_name='" + job_name + "'" + \
                                " AND sl.svr like '%" + s_svr + "%'" + \
                                str_checkbox_off + \
                                " ORDER BY ji.job_info_name, svr"

                # 미등록 OFF
                else:
                    s_query =  "/*right*/SELECT ji.job_info_name, REPLACE(sl.svr,'.tmonc.net','') AS svr, jsm.use_yn" + \
                                " FROM server_list sl JOIN job_info AS ji" + \
                                " LEFT JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno AND ji.job_info_seqno = jsm.job_info_seqno" + \
                                " WHERE 1=1" + \
                                " AND ji.job_info_name='" + job_name + "'" + \
                                " AND sl.svr like '%" + s_svr + "%'" + \
                               str_checkbox_off + \
                               " ORDER BY ji.job_info_name, svr"

                # print(s_query)
                # print("-------------------------------------------------------------")

                try:
                    with connections['tmon_dba'].cursor() as cursor:
                        cursor.execute(s_query)
                        svr_lists = namedtuplefetchall(cursor)
                        job_svr_lists.append([job_name, svr_lists])
                finally:
                    cursor.close()

        # print(job_svr_lists)
        context = {
            'job_svr_lists': job_svr_lists,
            'job_info_name': job_info_name,
        }

        return render(request, 'test1_right_ajax.html', context)
    else:
        return render(request, 'test1_right_ajax.html')



####################

def update_job_use_yn_ajax(request):
    if request.method == 'POST':
        job_name = request.POST.get('job_name')
        svr = request.POST.get('svr')
        flag = request.POST.get('flag') # true or false
        use_yn = request.POST.get('use_yn') # None 일경우, 미등록 처리 하기 위함

        flag = 1 if flag == 'true' else 0 # true = 1, false = 0
        # print("------------------------------------------------------------------------------------------------------")
        # print("/* use yn 입력값 테스트 */")
        # print(job_name)
        # print(svr)
        # print("변경값 : " + str(flag))
        # print("사용여부 : " + str(use_yn))
        # print("------------------------------------------------------------------------------------------------------")

        # 미등록 서버,잡 입력받는경우. INSERT
        if use_yn == 'None':
            print("미등록입니다. 신규 등록합니다.")
            query =   "INSERT INTO job_server_map (job_info_seqno, server_list_seqno, use_yn)" + \
                        " SELECT ji.job_info_seqno, sl.server_list_seqno, 1" + \
                        " FROM server_list sl JOIN job_info AS ji" + \
                        " WHERE 1=1" + \
                        " AND ji.job_info_name='" + job_name + "'" + \
                        " AND sl.svr='" + svr + ".tmonc.net'"

        # 기 등록 서버, 잡 입력받은경우
        else:
            print("등록입니다. 업데이트합니다.")
            query = "/*update_job_use_yn_ajax*/UPDATE job_server_map jsm SET use_yn=" + str(flag) + \
                    " WHERE 1=1" + \
                    " AND jsm.job_info_seqno = (SELECT job_info_seqno FROM job_info ji WHERE ji.job_info_name = '" + job_name+ "')" + \
                    " AND jsm.server_list_seqno = (SELECT server_list_seqno FROM server_list sl WHERE sl.svr=CONCAT('" + svr + "','.tmonc.net'))"
        # print("------------------------------------------------------------------------------------------------------")
        # print(query)
        # print("------------------------------------------------------------------------------------------------------")

        try:
            cursor = connections['tmon_dba'].cursor()
            cursor.execute(query)
            connection.commit()
        except:
            connection.rollback()
        finally:
            cursor.close()

    context = {
        'job_name': job_name,
        'svr': svr,
        'flag': flag,
    }

    return render(request, 'test1_dummy_ajax.html', context)


def test1_reload_left_ajax(request):
    if request.method == 'POST':
        time.sleep(0.2)
        job_info_name = request.POST.getlist('job_info_name[]')
        s_job_name = request.POST.get('s_job_name')
        s_svr = request.POST.get('s_svr')
        checkbox_unregister = request.POST.get('checkbox_unregister')
        checkbox_off = request.POST.get('checkbox_off')

        # print("-------------------------------------------------------------")
        # print("test1_reload_left_ajax")
        # print("-------------------------------------------------------------")
        # print(s_job_name)
        # print(job_info_name)
        # print(s_svr)
        # print(checkbox_unregister)
        # print(checkbox_off)
        # print("-------------------------------------------------------------")

        if s_job_name is None:
            s_job_name=''

        # 잡 리스트 및 JOB 스케줄 가져오기
        s_query = "/*left-reload*/SELECT ji.job_info_name, COUNT(svr) AS svr_total, IFNULL(SUM(use_yn),0) AS svr_use_total" + \
                    " FROM server_list sl" + \
                    " INNER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno" + \
                    " RIGHT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                    " where ji.job_info_name like '%" + s_job_name + "%'" + \
                    " GROUP BY ji.job_info_name" + \
                    " ORDER BY ji.job_info_name"
        # print(s_query)

        # print("-------------------------------------------------------------")
        with connections['tmon_dba'].cursor() as cursor:
            job_info_lists = []
            cursor.execute(s_query)
            job_info_lists = namedtuplefetchall(cursor)

        context = {
            'job_info_lists': job_info_lists,
            'job_info_name_checked_list': job_info_name,
            's_svr': s_svr,
            'checkbox_unregister': checkbox_unregister,
            'checkbox_off': checkbox_off,
        }

        return render(request, 'test1_left_ajax.html', context)

    else:
        return render(request, 'test1_left_ajax.html')

def test2(request):
    return render(request, 'test1_dummy_ajax.html')

#########################################################################
# testing slack 슬객 테스트
#########################################################################

def slack_notify(slack_message, channel, username, attachments=None):
    token = 'BLP01FSDV/H2Zl9HYH5Pd2K62ehGOUjDMY'
    slack = Slacker(token)
    slack.chat.post_message(text=slack_message, channel=channel, username=username, attachments=attachments)

def slack_test(request):
    print("슬랙 테스트 함수. 지나갑니다.")
    # slack_message = "테스트 발송"
    # slack_notify(slack_message, '#gytjdlee', '알림봇 테스트')

    return redirect('/testing')







