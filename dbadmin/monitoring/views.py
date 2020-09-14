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
from django.template import Context, Engine, TemplateDoesNotExist, loader
import socket, struct
import math

from collections import namedtuple
from slacker import Slacker

#########################################################################
# namedtuplefetchall
#########################################################################
def namedtuplefetchall(cursor):
    #"Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

#########################################################################
# server_list, server_job_list
#########################################################################
@login_required
def server_list(request):
    if request.method == 'POST':
        # 서버 베이스 입력값
        svr = request.POST.get('svr')

    else:
        # 서버 베이스 입력값. 입력값이 없는경우
        svr = ''


    # 서버리스트 및 JOB 스케줄 가져오기
    query = "SELECT a.svr, IFNULL(a.row_number,1) as row_number, b.cnt, b.use_yn_on_cnt, a.job_info_name, a.use_yn FROM ( \
    SELECT REPLACE(sl.svr,'.tmonc.net','') AS svr, ji.job_info_name AS job_info_name, jsm.jsm.row_number, ji.job_info_seqno , jsm.use_yn AS use_yn \
    FROM server_list AS sl \
    LEFT OUTER JOIN ( \
    	SELECT server_list_seqno, job_info_seqno, use_yn, @ROW_NUM := IF(@PREV_VALUE = jsm.server_list_seqno, @ROW_NUM + 1, 1) AS row_number \
    		  , @PREV_VALUE := jsm.server_list_seqno AS dummy \
    	FROM job_server_map jsm \
    	 , (SELECT @ROW_NUM := 1) X \
    	 , (SELECT @PREV_VALUE := '') Y \
    	ORDER BY jsm.server_list_seqno \
    ) AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    ORDER BY sl.svr ASC, ji.job_info_seqno ASC, jsm.use_yn DESC) a \
    INNER JOIN \
    (SELECT REPLACE(sl.svr,'.tmonc.net','') AS svr, COUNT(ji.job_info_seqno) AS cnt, IFNULL(SUM(jsm.use_yn),0) AS use_yn_on_cnt \
    FROM server_list AS sl \
    LEFT OUTER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    GROUP BY REPLACE(sl.svr,'.tmonc.net','')) b \
    ON a.svr=b.svr \
    WHERE a.svr LIKE '" + svr + "%' \
    ORDER BY a.svr ASC, a.row_number, a.use_yn DESC"

    #query = "SELECT REPLACE(sl.svr,'.tmonc.net','') as svr, ji.job_info_name as job_info_name, jsm.use_yn as use_yn \
    #			FROM server_list AS sl \
    #			JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    #			LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    #			where sl.svr like '" + svr + "%' \
    #			ORDER BY sl.svr ASC, ji.job_info_seqno ASC, jsm.use_yn DESC"

    # 서버리스트 및 DATA 카운트 가져오기 (집계)
    #query_cnt = "SELECT REPLACE(sl.svr,'.tmonc.net','') AS svr, COUNT(ji.job_info_seqno) AS cnt, IFNULL(SUM(jsm.use_yn),0) AS use_yn_on_cnt \
    #			FROM server_list AS sl \
    #			LEFT OUTER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    #			LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    #			where sl.svr like '" + svr + "%' \
    #			GROUP BY REPLACE(sl.svr,'.tmonc.net','')"
    # ORDER BY sl.svr ASC, ji.job_info_seqno ASC, jsm.use_yn DESC"

    with connections['tmon_dba'].cursor() as cursor:

        # 서버리스트 및 JOB 스케줄 가져오기
        # svr = row[0]
        # job_info_name = row[1]
        # use_yn = row[2]

        results = []
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            results.append(row)


        # 서버리스트 및 DATA 카운트 가져오기 (집계)
        # svr = row[0]
        # cnt = row[1]
        # use_yn_on_cnt = row[2]

        #results_server_list = []
        #cursor.execute(query_cnt)
        #rows = cursor.fetchall()

        #for row in rows:
        #    results_server_list.append(row)

    context = {
        'server_lists': results,
        #'server_lists_distinct': results_server_list,
        'svr': svr
    }

    return render(request, 'server_list.html', context)

def server_list_update(request):
    if request.method == 'POST':

        server_list = request.POST.getlist('server_list') # 서버명
        server_list4 = request.POST.getlist('server_list4') # 저장해야 할 변환값
        server_list5 = request.POST.getlist('server_list5') # 원래 입력값
        server_list4 = ", ".join( repr(e) for e in server_list4) # QUERY에 쓰일 JOB_NAME 값

        svr = server_list[0] + ".tmonc.net"

        # print("=================================================")
        # print("svr : " + str(svr))
        # print("server_list. 서버명 : " + str(server_list[0]))
        # print("server_list4. 변경값 대상 잡 : " + str(server_list4))
        # print("server_list5. 원래값 : " + str(server_list5))
        # print("length server_list4. 변경 대상 잡 포함여부 : " + str(len(server_list4)))
        # print("=================================================")


        if len(server_list4) != 0: # 하나라도 ON 입력값이 있는 경우
            query_update_use_yn_y = "UPDATE server_list AS sl \
            		JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
            		LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
            		SET jsm.use_yn=1 \
            		WHERE 1=1 \
            		AND sl.svr = '" + svr + "' \
            		AND ji.job_info_name IN (" + server_list4 + ")"

            query_update_use_yn_n = "UPDATE server_list AS sl \
            		JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
            		LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
            		SET jsm.use_yn=0 \
            		WHERE 1=1 \
            		AND sl.svr = '" + svr + "' \
            		AND ji.job_info_name NOT IN (" + server_list4 + ")"

            try:
                cursor = connections['tmon_dba'].cursor()
                cursor.execute(query_update_use_yn_y)
                cursor.execute(query_update_use_yn_n)
                connection.commit()
            finally:
                cursor.close()

        else: # ON 변경값이 하나라도 없는경우. 전부 OFF 처리
            query_update_use_yn_n = "UPDATE server_list AS sl \
             		JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
             		LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
             		SET jsm.use_yn=0 \
             		WHERE 1=1 \
             		AND sl.svr = '" + svr + "'"

            try:
                cursor = connections['tmon_dba'].cursor()
                cursor.execute(query_update_use_yn_n)
                connection.commit()
            finally:
                cursor.close()

        svr = request.POST.get('svr') # 리턴을 위함 (select)
    else:
        svr = '' # 리턴을 위함

    ########################################################## SELECT
    # 서버리스트 및 JOB 스케줄 가져오기
    query = "SELECT a.svr, IFNULL(a.row_number,1), b.cnt, b.use_yn_on_cnt, a.job_info_name, a.use_yn FROM ( \
    SELECT REPLACE(sl.svr,'.tmonc.net','') AS svr, ji.job_info_name AS job_info_name, jsm.jsm.row_number, ji.job_info_seqno , jsm.use_yn AS use_yn \
    FROM server_list AS sl \
    LEFT OUTER JOIN ( \
    	SELECT server_list_seqno, job_info_seqno, use_yn, @ROW_NUM := IF(@PREV_VALUE = jsm.server_list_seqno, @ROW_NUM + 1, 1) AS row_number \
    		  , @PREV_VALUE := jsm.server_list_seqno AS dummy \
    	FROM job_server_map jsm \
    	 , (SELECT @ROW_NUM := 1) X \
    	 , (SELECT @PREV_VALUE := '') Y \
    	ORDER BY jsm.server_list_seqno, jsm.job_info_seqno \
    ) AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    ORDER BY sl.svr ASC, ji.job_info_seqno ASC, jsm.use_yn DESC) a \
    INNER JOIN \
    (SELECT REPLACE(sl.svr,'.tmonc.net','') AS svr, COUNT(ji.job_info_seqno) AS cnt, IFNULL(SUM(jsm.use_yn),0) AS use_yn_on_cnt \
    FROM server_list AS sl \
    LEFT OUTER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    GROUP BY REPLACE(sl.svr,'.tmonc.net','')) b \
    ON a.svr=b.svr \
    WHERE a.svr LIKE '" + svr + "%' \
    ORDER BY a.svr ASC, a.row_number, a.use_yn DESC"

    with connections['tmon_dba'].cursor() as cursor:

        # 서버리스트 및 JOB 스케줄 가져오기
        # svr = row[0]
        # job_info_name = row[1]
        # use_yn = row[2]

        results = []
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            results.append(row)

    context = {
        'server_lists': results,
        'svr': svr
    }

    return render(request, 'server_list.html', context)

def server_job_list(request):
    if request.method == 'POST':
        # 서버 베이스 입력값
        job_info_name = request.POST.get('job_info_name')

    else:
        # 서버 베이스 입력값. 입력값이 없는경우
        job_info_name = ''


    # 잡 리스트 및 JOB 스케줄 가져오기
    query = "SELECT a.job_info_name, IFNULL(a.row_number,1) AS row_number, b.cnt, b.use_yn_on_cnt, a.svr, a.use_yn FROM ( \
    SELECT ji.job_info_name AS job_info_name, REPLACE(sl.svr,'.tmonc.net','') AS svr, jsm.jsm.row_number, ji.job_info_seqno , jsm.use_yn AS use_yn \
    FROM server_list AS sl \
    INNER JOIN ( \
    SELECT job_info_seqno, server_list_seqno, use_yn, @ROW_NUM := IF(@PREV_VALUE = jsm.job_info_seqno, @ROW_NUM + 1, 1) AS row_number \
    	  , @PREV_VALUE := jsm.job_info_seqno AS dummy \
    FROM job_server_map jsm \
     , (SELECT @ROW_NUM := 1) X \
     , (SELECT @PREV_VALUE := '') Y \
    ORDER BY jsm.job_info_seqno \
    ) AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    ORDER BY ji.job_info_name ASC, ji.job_info_seqno ASC, jsm.use_yn DESC) a \
    INNER JOIN \
    (SELECT ji.job_info_name AS job_info_name, COUNT(ji.job_info_seqno) AS cnt, IFNULL(SUM(jsm.use_yn),0) AS use_yn_on_cnt \
    FROM server_list AS sl \
    INNER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    GROUP BY ji.job_info_name) b \
    ON a.job_info_name=b.job_info_name \
    WHERE a.job_info_name LIKE '%" + job_info_name + "%' \
    ORDER BY a.job_info_name ASC, a.row_number, a.use_yn DESC"

    with connections['tmon_dba'].cursor() as cursor:

        # 서버리스트 및 JOB 스케줄 가져오기
        # svr = row[0]
        # job_info_name = row[1]
        # use_yn = row[2]

        results = []
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            results.append(row)

    context = {
        'server_job_lists': results,
        'job_info_name': job_info_name
    }

    return render(request, 'server_job_list.html', context)


def server_job_list_update(request):
    ########################################################## INSERT
    if request.method == 'POST':

        server_job_list = request.POST.getlist('server_job_list') # 잡명
        server_job_list4 = request.POST.getlist('server_job_list4') # 저장해야 할 변환값
        server_job_list5 = request.POST.getlist('server_job_list5') # 원래 입력값
        server_job_list4 = ", ".join( repr(e) for e in server_job_list4) # QUERY에 쓰일 서버명

        server_job_name = server_job_list[0]

        # print("=================================================")
        # print("server_job_list: 잡명: " + str(server_job_list[0]))
        # print("server_job_list4: 변경값 대상 서버: " + str(server_job_list4))
        # print("server_job_list5: 원래값 : " + str(server_job_list5))
        # print("length server_job_list4: 변경 대상 서버 포함여부 : " + str(len(server_job_list4)))
        # print("=================================================")
        # #svr = server_list[0] + ".tmonc.net"


        if len(server_job_list4) != 0: # 하나라도 ON 입력값이 있는 경우
            query_update_use_yn_y = "UPDATE server_list AS sl \
            		JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
            		LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
            		SET jsm.use_yn=1 \
            		WHERE 1=1 \
            		AND ji.job_info_name = '" + server_job_name + "' \
            		AND sl.svr IN (" + server_job_list4 + ")"

            query_update_use_yn_n = "UPDATE server_list AS sl \
            		JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
            		LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
            		SET jsm.use_yn=0 \
            		WHERE 1=1 \
            		AND ji.job_info_name = '" + server_job_name + "' \
            		AND sl.svr NOT IN (" + server_job_list4 + ")"

            # print("하나라도ON : " + str(query_update_use_yn_y))
            # print("하나라도ON : " + str(query_update_use_yn_n))

            try:
                cursor = connections['tmon_dba'].cursor()
                cursor.execute(query_update_use_yn_y)
                cursor.execute(query_update_use_yn_n)
                connection.commit()
            finally:
                cursor.close()

        else: # ON 변경값이 하나라도 없는경우. 전부 OFF 처리
            query_update_use_yn_n = "UPDATE server_list AS sl \
             		JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
             		LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
             		SET jsm.use_yn=0 \
             		WHERE 1=1 \
                    AND ji.job_info_name = '" + server_job_name + "'"

            # print("전부 OFF : " + str(query_update_use_yn_n))
            try:
                cursor = connections['tmon_dba'].cursor()
                cursor.execute(query_update_use_yn_n)
                connection.commit()
            finally:
                cursor.close()

        job_info_name = request.POST.get('job_info_name') # 리턴을 위함 (select)
    else:
        job_info_name = '' # 리턴을 위함

    ########################################################## SELECT
    # 서버리스트 및 JOB 스케줄 가져오기
    query = "SELECT a.job_info_name, IFNULL(a.row_number,1) AS row_number, b.cnt, b.use_yn_on_cnt, a.svr, a.use_yn FROM ( \
    SELECT ji.job_info_name AS job_info_name, REPLACE(sl.svr,'.tmonc.net','') AS svr, jsm.jsm.row_number, ji.job_info_seqno , jsm.use_yn AS use_yn \
    FROM server_list AS sl \
    INNER JOIN ( \
    SELECT job_info_seqno, server_list_seqno, use_yn, @ROW_NUM := IF(@PREV_VALUE = jsm.job_info_seqno, @ROW_NUM + 1, 1) AS row_number \
    	  , @PREV_VALUE := jsm.job_info_seqno AS dummy \
    FROM job_server_map jsm \
     , (SELECT @ROW_NUM := 1) X \
     , (SELECT @PREV_VALUE := '') Y \
    ORDER BY jsm.job_info_seqno \
    ) AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    ORDER BY ji.job_info_name ASC, ji.job_info_seqno ASC, jsm.use_yn DESC) a \
    INNER JOIN \
    (SELECT ji.job_info_name AS job_info_name, COUNT(ji.job_info_seqno) AS cnt, IFNULL(SUM(jsm.use_yn),0) AS use_yn_on_cnt \
    FROM server_list AS sl \
    INNER JOIN job_server_map AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    GROUP BY ji.job_info_name) b \
    ON a.job_info_name=b.job_info_name \
    WHERE a.job_info_name LIKE '%" + job_info_name + "%' \
    ORDER BY a.job_info_name ASC, a.row_number, a.use_yn DESC"

    with connections['tmon_dba'].cursor() as cursor:

        # 서버리스트 및 JOB 스케줄 가져오기
        # svr = row[0]
        # job_info_name = row[1]
        # use_yn = row[2]

        results = []
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            results.append(row)

    context = {
        'server_job_lists': results,
        'job_info_name': job_info_name
    }

    return render(request, 'server_job_list.html', context)

#########################################################################
# server_list_new
#########################################################################

def server_job_list_new(request):
    return render(request, 'server_job_list_new.html')

def server_job_list_left_ajax(request):
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

        return render(request, 'server_job_list_left_ajax.html', context)

    else:
        return render(request, 'server_job_list_left_ajax.html')

def server_job_list_right_ajax(request):
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

        return render(request, 'server_job_list_right_ajax.html', context)
    else:
        return render(request, 'server_job_list_right_ajax.html')

def server_job_list_update_job_use_yn_ajax(request):
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

    return render(request, 'server_job_list_dummy_ajax.html', context)

def server_job_list_delete_job_use_yn_ajax(request):
    if request.method == 'POST':
        job_name = request.POST.get('job_name')
        svr = request.POST.get('svr')
        flag = request.POST.get('flag') # true or false
        use_yn = request.POST.get('use_yn') # None 일경우, 미등록 처리 하기 위함

        flag = 1 if flag == 'true' else 0 # true = 1, false = 0
        print("-------------------------------------------------------------------------------------------------------")
        print("/* delete_job_use_yn_ajax 입력값 테스트 */")
        print(job_name)
        print(svr)
        print("변경값 : " + str(flag))
        print("사용여부 : " + str(use_yn))
        print("-------------------------------------------------------------------------------------------------------")

        # 등록잡 삭제하기
        print("등록된 잡 삭제하기")
        query = "/*delete_job_use_yn_ajax*/ DELETE FROM job_server_map" + \
                " WHERE 1=1" + \
                " AND job_info_seqno = (SELECT job_info_seqno FROM job_info ji WHERE ji.job_info_name = '" + job_name+ "')" + \
                " AND server_list_seqno = (SELECT server_list_seqno FROM server_list sl WHERE sl.svr=CONCAT('" + svr + "','.tmonc.net'))"
        # print("------------------------------------------------------------------------------------------------------")
        print(query)
        print("-------------------------------------------------------------------------------------------------------")

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

    return render(request, 'server_job_list_dummy_ajax.html', context)

def server_job_list_reload_left_ajax(request):
    if request.method == 'POST':
        time.sleep(0.2)
        job_info_name = request.POST.getlist('job_info_name[]')
        s_job_name = request.POST.get('s_job_name')
        s_svr = request.POST.get('s_svr')
        checkbox_unregister = request.POST.get('checkbox_unregister')
        checkbox_off = request.POST.get('checkbox_off')

        # print("-------------------------------------------------------------")
        # print("server_job_list_reload_left_ajax")
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

        return render(request, 'server_job_list_left_ajax.html', context)

    else:
        return render(request, 'server_job_list_left_ajax.html')

