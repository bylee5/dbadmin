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

from .models import *
from .forms import *
from django.template import Context, Engine, TemplateDoesNotExist, loader

# Create your views here.

#JobInfo
#JobServerMap
#ServerList

def server_list(request):
    # 서버 베이스

    query = "SELECT REPLACE(sl.svr,'.tmonc.net','') as svr, ji.job_info_name as job_info_name, jsm.use_yn as use_yn \
                FROM server_list AS sl \
                LEFT OUTER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
                LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
                ORDER BY sl.svr ASC, ji.job_info_seqno ASC, jsm.use_yn DESC"

    query_cnt = "SELECT REPLACE(sl.svr,'.tmonc.net','') AS svr, COUNT(*) AS cnt, IFNULL(SUM(jsm.use_yn),0) AS use_yn_on_cnt \
                FROM server_list AS sl \
                LEFT OUTER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
                LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
                GROUP BY REPLACE(sl.svr,'.tmonc.net','') \
                ORDER BY sl.svr ASC, ji.job_info_seqno ASC, jsm.use_yn DESC"

    with connection.cursor() as cursor:
        # 서버리스트 및 DATA 카운트 가져오기
        # svr = row[0]
        # job_info_name = row[1]
        # use_yn = row[2]

        results = []

        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            results.append(row)

        # 서버리스트 및 DATA 카운트 가져오기
        # svr = row[0]
        # cnt = row[3]
        # use_yn_on_cnt = row[4]

        results_server_list = []

        cursor.execute(query_cnt)
        rows = cursor.fetchall()

        for row in rows:
            results_server_list.append(row)

    context = {
        'server_lists': results,
        'server_lists_distinct': results_server_list
    }

    return render(request, 'server_list.html', context)

def server_job_list(request):

    # 잡 베이스
    query = "SELECT ji.job_info_name, REPLACE(sl.svr,'.tmonc.net','') as svr, jsm.use_yn \
    FROM job_info AS ji \
    LEFT OUTER JOIN job_server_map AS jsm ON ji.job_info_seqno = jsm.job_info_seqno \
    LEFT OUTER JOIN server_list AS sl ON jsm.server_list_seqno = sl.server_list_seqno \
    ORDER BY ji.job_info_seqno ASC, jsm.use_yn DESC, sl.svr ASC"

    return render(request, 'server_job_list.html')

