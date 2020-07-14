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
#from django.contrib.auth.decorators import login_required

from django.db import connections
from .models import *
from .forms import *
from django.template import Context, Engine, TemplateDoesNotExist, loader

# Create your views here.

#JobInfo
#JobServerMap
# #ServerList
#：
#:

#@login_required

def server_list(request):
    if request.method == 'POST':
        # 서버 베이스 입력값
        svr = request.POST.get('svr')

    else:
        # 서버 베이스 입력값. 입력값이 없는경우
        svr = ''


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
    	ORDER BY jsm.server_list_seqno \
    ) AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    ORDER BY sl.svr ASC, ji.job_info_seqno ASC, jsm.use_yn DESC) a \
    INNER JOIN \
    (SELECT REPLACE(sl.svr,'.tmonc.net','') AS svr, COUNT(*) AS cnt, IFNULL(SUM(jsm.use_yn),0) AS use_yn_on_cnt \
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
    ########################################################## INSERT
    if request.method == 'POST':

        server_list = request.POST.getlist('server_list') # 서버명
        server_list4 = request.POST.getlist('server_list4') # 저장해야 할 변환값
        server_list5 = request.POST.getlist('server_list5') # 원래 입력값
        server_list4 = ", ".join( repr(e) for e in server_list4) # QUERY에 쓰일 JOB_NAME 값

        svr = server_list[0] + ".tmonc.net"

        print("=================================================")
        print("svr : " + str(svr))
        print("server_list. 서버명 : " + str(server_list[0]))
        print("server_list4. 변경값 대상 잡 : " + str(server_list4))
        print("server_list5. 원래값 : " + str(server_list5))
        print("length server_list4. 변경 대상 잡 포함여부 : " + str(len(server_list4)))
        print("=================================================")


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
    	ORDER BY jsm.server_list_seqno \
    ) AS jsm ON sl.server_list_seqno = jsm.server_list_seqno \
    LEFT OUTER JOIN job_info AS ji ON jsm.job_info_seqno = ji.job_info_seqno \
    ORDER BY sl.svr ASC, ji.job_info_seqno ASC, jsm.use_yn DESC) a \
    INNER JOIN \
    (SELECT REPLACE(sl.svr,'.tmonc.net','') AS svr, COUNT(*) AS cnt, IFNULL(SUM(jsm.use_yn),0) AS use_yn_on_cnt \
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


def server_job_list(request):

    # 잡 베이스
    query = "SELECT ji.job_info_name, REPLACE(sl.svr,'.tmonc.net','') as svr, jsm.use_yn \
    FROM job_info AS ji \
    LEFT OUTER JOIN job_server_map AS jsm ON ji.job_info_seqno = jsm.job_info_seqno \
    LEFT OUTER JOIN server_list AS sl ON jsm.server_list_seqno = sl.server_list_seqno \
    ORDER BY ji.job_info_seqno ASC, jsm.use_yn DESC, sl.svr ASC"

    return render(request, 'server_job_list.html')
