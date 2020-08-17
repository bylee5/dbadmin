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
    return render(request, 'test_graph.html')


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

        print("-------------------------------------------------------------")
        print(s_job_name)

        # 잡 리스트 및 JOB 스케줄 가져오기
        s_query = "SELECT ji.job_info_name, COUNT(svr) AS svr_total, SUM(use_yn) AS svr_use_total" + \
                    " FROM server_list sl" + \
                    " INNER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno" + \
                    " RIGHT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                    " where ji.job_info_name like '%" + s_job_name + "%'" + \
                    " GROUP BY ji.job_info_name" + \
                    " ORDER BY ji.job_info_name"
        print(s_query)

        print("-------------------------------------------------------------")
        with connections['tmon_dba'].cursor() as cursor:
            job_info_lists = []
            cursor.execute(s_query)
            job_info_lists = namedtuplefetchall(cursor)

        context = {
            'job_info_lists': job_info_lists,
        }

        return render(request, 'test1_left_ajax.html', context)

    else:
        return render(request, 'test1.html')


def test1_right_ajax(request):
    if request.method == 'POST':
        job_info_name = request.POST.get('job_info_name')
        print("-------------------------------------------------------------")
        print("right POST 테스트")
        print(job_info_name)

        # 잡 리스트 및 JOB 스케줄 가져오기
        s_query =   "SELECT REPLACE(sl.svr,'.tmonc.net','') AS svr, jsm.use_yn" + \
                    " FROM server_list sl" + \
                    " INNER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno" + \
                    " RIGHT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno" + \
                    " WHERE 1=1" + \
                    " AND ji.job_info_name='" + str(job_info_name) + "'" + \
                    " ORDER BY svr"

        print(s_query)
        print("-------------------------------------------------------------")

        with connections['tmon_dba'].cursor() as cursor:
            job_svr_lists = []
            cursor.execute(s_query)
            job_svr_lists = namedtuplefetchall(cursor)

        context = {
            'job_svr_lists': job_svr_lists,
            'job_info_name': job_info_name,
        }

        return render(request, 'test1_right_ajax.html', context)
    else:
        return render(request, 'test1.html')



####################

def test2(request):
    return render(request, 'test2.html')

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







