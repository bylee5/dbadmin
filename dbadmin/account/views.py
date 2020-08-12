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
import socket, struct
import math

#########################################################################
# 계정 정합성 체크
#########################################################################

#------------------------------------------------------------------------
# ※ 이슈 : 계정 한개만 존재 할 경우, 수정 입력등에 이슈 있을 수 있음
#------------------------------------------------------------------------


# 1.패스워드 중복 여부 체크
# 하나의 아이디에는 동일한 패스워드를 사용해야 한다.
# 운영, 개발간에는 패스워드가 달라야한다.
# 다른계정에 동일 패스워드를 사용하는 계정은 없어야 한다.
# 체크값 : 호스트, 계정, 패스워드
def check_overlap_password(svr, user, password):
    # real/stage
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    print(password)
    if svr.find('dev') < 0:
        print("리얼")
        query = "SELECT distinct account_pass FROM account_account where 1=1 " \
                " AND account_svr not like '%dev%'" \
                " AND account_user='" + user + "'" \
                " AND account_del_yn='N'"

    # dev/qa
    else:
        print("DEV")
        query = "SELECT distinct account_pass FROM account_account where 1=1 " \
                " AND account_svr like '%dev%'" \
                " AND account_user='" + user + "'" \
                " AND account_del_yn='N'"

    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

        print(rows)
        print("반복횟수 : " + str(len(rows)))
        print(len(rows))

        if len(rows) < 2: # 내가 첫 계정인가? 계정이 없는경우 0, 하나만 있는 경우 1
            print("내가 첫 계정인가? Yes!!")
            alert_type = "ERR_0"
            alert_message = ""

            # 다른계정의 패스워드와 공유할 수 있는 경우가 있어 아래 부분 주석 처리함.
            # with connections['default'].cursor() as cursor1:
            #     query = "SELECT DISTINCT account_user, account_pass FROM account_account WHERE account_pass='" + password + "'"
            #     cursor1.execute(query)
            #     row = cursor1.fetchone()
            #
            #     if len(row) == 0:
            #         print("내가 이 패스워드의 첫 주인이군")
            #         alert_type = "ERR_0"
            #         alert_message = ""
            #     else:
            #         print("뭐야 누가 쓰고있네?")
            #         alert_type = "ERR_2"
            #         alert_message = "동일 패스워드를 사용하는 타 계정이 존재합니다. 다른 패스워드를 사용해주세요.\n(중복 패스워드 사용계정 : " + row[0] + ")"
            #
            #     cursor1.close()

        else:
            print("내가 첫...계정이 아니구나. 비교를하자.")

            for row in rows:
                if row[0] == password: # 패스워드가 존재하는가?"
                    # print("동일계정에 일치하는 패스워드가 존재하네. 이상없군. 빠져나오자.")
                    alert_type = "ERR_0"
                    alert_message = ""
                    break
                else: # 패스워드가 존재하지 않는가?
                    # print("계정이 존재하는데, 패스워드가 일치하는게 없나보네...")
                    alert_type = "ERR_1"
                    alert_message = "입력하신 패스워드가 동일 계정 내 패스워드와 다릅니다."

        cursor.close()

    # print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    return alert_type, alert_message

# 2. 계정 중복 여부 체크
# 동일한 계정이 존재해선 안된다.
# 체크값 : 서버, 아이디, 패스워드, 호스트, 권한, DB, TABLE
def check_overlap_account(svr, user, host, password, grant, db, table):
    query = "SELECT count(*) AS cnt FROM account_account WHERE 1=1" \
            " AND account_svr='" + svr + "'" \
            " AND account_user='" + user + "'" \
            " AND account_host='" + host + "'" \
            " AND account_pass='" + password + "'" \
            " AND account_grant='" + grant + "'" \
            " AND account_db='" + db + "'" \
            " AND account_table='" + table + "'" \
            " AND account_del_yn='N'"

    print(query)
    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()

    if row[0] == 0:
        alert_type = "ERR_0"
        alert_message = ""

    else:
        alert_type = "ERR_3"
        alert_message = "입력하신 계정과 중복인 계정이 존재합니다. 호스트, 권한 등을 확인해주세요."

    return alert_type, alert_message

# 3. 동일 패스워드를 사용 타 계정 여부 ing ~
# 체크값 :
def check_overlap_test(svr, user, password):
    query = "SELECT count(*) AS cnt FROM account_account \
            WHERE account_del_yn='N' AND account_svr='" + svr + "' AND account_user='" + user + "' AND account_pass!='" + password + "'"

    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()

    if row[0] == 0:
        alert_type = "ERR_0"
        alert_message = ""

    else:
        alert_type = "ERR_3"
        alert_message = "동일 패스워드를 사용하는 타 계정이 존재합니다. 다른 패스워드를 사용해주세요."

    return alert_type, alert_message

# 4. 상위 호환 계정 권한 존재유무 체크 ing ~
# 5. 상위 호환 계정 호스트대역 존재유무 체크 ing ~
# 6. 상위 호환 계정 테이블 존재유무 체크 ing ~
# 7. 리얼, NDEVDB 패스워드 불일치 여부 (* 불일치 해야함)

# 00. 메인 계정 정합성 체크 함수
def check_account_consistency(svr, user, host, password, db, table, grant):

    alert_type, alert_message = check_overlap_password(svr, user, password)
    if alert_type == "ERR_1" or alert_type == "ERR_2":
        return alert_type, alert_message

    alert_type, alert_message = check_overlap_account(svr, user, host, password, grant, db, table)
    if alert_type == "ERR_3":
        return alert_type, alert_message

    # 아무 if 조건에도 걸리지 않는다면, 즉, 정합성이 모두 맞다면, ERR_0을 리턴
    alert_type = "ERR_0"
    alert_message = ""

    return alert_type, alert_message

#########################################################################
# custom function
#########################################################################
# Encrypt key
def get_key():
    #file_path = os.path.join(settings.KEY_URL, 'other/keyfile.lst')
    #with open(file_path, encoding='utf-8') as txtfile:
    #    for row in txtfile.readlines():
    #        key = row
    key = settings.ENC_KEY

    return key

# 패스워드 해시값 가져오기
def get_password_hash(account_pass):
    query = "SELECT id, password_hash FROM account_hash WHERE password_hash=PASSWORD('" + account_pass + "') limit 0,1"

    for result in Account_hash.objects.raw(query):
       return result.password_hash

# 패스워드 암호화값 사용 여부 체크
def is_password_encrypt_yn(account_pass):
    query = "SELECT AES_DECRYPT(UNHEX('" + account_pass + "'), '" + get_key() + "')"

    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()

    if row[0] is None: # 패스워드 암호화가 안되있는경우. False 리턴
        print("암호화가 안되어있네요..")
        return False
    else: # 패스워드 암호화가 되어있는경우. True 리턴
        print("암호화가 되있군요!!")
        return True

# 패스워드 암호화값 가져오기
def get_password_encrypt(account_pass):
    query = "SELECT id, password_encrypt FROM account_hash WHERE password_hash=PASSWORD('" + account_pass + "') limit 0,1"

    for result in Account_hash.objects.raw(query):
       return result.password_encrypt

# 패스워드 복호화값 가져오기
def get_password_decrypt(account_pass):
    query = "SELECT AES_DECRYPT(UNHEX('" + account_pass + "'), '" + get_key() + "') as pass"

    print(query)
    with connections['default'].cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()

    row = row[0].decode("utf-8")
    return row

# 패스워드 암호화, 해시값 세팅
def put_password(account_pass):
    # print("패스워드 암호화 함수 시작")
    # print(account_pass)
    query = "insert ignore into account_hash(password_encrypt,password_hash)" \
            "values (HEX(AES_ENCRYPT('" + account_pass + "', '" + get_key() + "')), \
             password('" + account_pass + "'))"

    # print("패스워드 암호화 함수 중간")
    cursor = connection.cursor()
    cursor.execute(query)
    # print("패스워드 암호화 함수 끝")

def recreate_account_sql(request, account_id_list):
    print(account_id_list)
    # for account_id in account_id_list.split(','):

    u_query = "/*RE-CREATE ACCOUNT_SQL*/UPDATE account_account set account_sql = " + \
    "CONCAT('/*',account_svr,'*/ USE mysql; /*',account_url,'*/ " + \
    "GRANT ',account_grant,' ON ', account_db,'.',account_table,' TO '''" + \
    ",account_user,'''@''',account_host,''' IDENTIFIED BY PASSWORD ''',account_hash,''';') " + \
    "WHERE id in(" + account_id_list + ");"

    print("리크리에이트 SQL u_query : ")
    print(u_query)

    try:
        cursor = connections['default'].cursor()
        cursor.execute(u_query)
        connection.commit()

        # 성공 후 데일리 백업 체크, 히스토리 로깅
        create_daily_backup_table(request, 'account')
        log_history_insert(request, "'" + account_id_list + "'", 'account', 'update', u_query)

    except:
        connection.rollback()
    finally:
        cursor.close()


# 일간 백업 진행. 매일 첫 DML 이벤트가 발생 할 경우, 백업 테이블 생성
def create_daily_backup_table(request, backup_type):
    db_schema_source = 'dbadmin'
    db_schema_target = 'dbadmin_backup'
    current_dt = datetime.now().strftime("%Y%m%d")

    print("backup_type : " + backup_type)

    if backup_type == 'account':
        table_list = ['account_hash','account_account']
    elif backup_type == 'repository':
        table_list = ['account_repository']
    else:
        table_list = None

    if table_list is not None:
        print("일간 백업 동작")
        for table in table_list:
            s_query = "SELECT table_name FROM information_schema.tables WHERE table_schema='" + db_schema_target + "' and table_name LIKE '" + table + "%" + current_dt + "%'"
            # print(s_query)

            with connections['default'].cursor() as cursor:
                cursor.execute(s_query)
                rows = cursor.fetchone()

            # 일간 백업 대상 테이블이 없는경우에는 수행하지 아니함
            if rows is None:
                c_query = "CREATE TABLE " + db_schema_target + "." + table + "_" + current_dt + " LIKE " + db_schema_source + "." + table
                i_query = "INSERT INTO " + db_schema_target + "." + table + "_" + current_dt + " SELECT * FROM " + db_schema_source + "." + table
                print(c_query)
                print(i_query)

                try:
                    with connections['default'].cursor() as cursor:
                        cursor.execute(c_query)
                        cursor.execute(i_query)

                        log_history_insert(request, 'null', 'backup', 'create', c_query)
                        log_history_insert(request, 'null', 'backup', 'insert', i_query)

                except:
                    connection.rollback()
                finally:
                    cursor.close()

            print("아무일도 없었다고 한다...")

    else:
        print("백업 테이블 테스트. 거짓말같이 아무일도 없었다고 한다...")

# 로깅 히스토리
def log_history_insert(request, related_id, menu_type, sql_type, execute_sql):
    table = 'account_history'

    who_updated = request.user.username
    ip = request.META.get('REMOTE_ADDR')
    who_writer = struct.unpack("!I", socket.inet_aton(ip))[0]  # IP 10진수
    # ip_re = socket.inet_ntoa(struct.pack('!I', who_writer))  # IP 10진수 원복 IP

    # print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    # print(who_updated)
    # print(who_writer)
    # print(related_id)
    # print(menu_type)
    # print(sql_type)
    # print(execute_sql)
    # print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

    i_query = "INSERT INTO " + table + "(related_id, who_updated, who_writer, menu_type, sql_type, execute_sql) VALUES(" + \
               related_id + ",'" + who_updated + "'," + str(who_writer) + ",'" + menu_type + "','" + sql_type + "'," + '"' + execute_sql + '");'

    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    print("로그히스토리용 i_query : " + i_query)
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

    try:
        with connections['default'].cursor() as cursor:
            cursor.execute(i_query)
    except:
        connection.rollback()
    finally:
        cursor.close()

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
@login_required
def account(request):
    account_svr_list = Account.objects.all().filter(account_del_yn='N').order_by('account_svr').values('account_svr').distinct()

    context = {
        'account_svr_list': account_svr_list
    }

    return render(request, 'account.html', context)

@login_required
def account_select(request):
    if request.method == 'POST':
        account_requestor = request.POST.get('s_account_requestor')
        account_devteam = request.POST.get('s_account_devteam')
        account_svr = request.POST.get('s_account_svr')
        account_user = request.POST.get('s_account_user')
        account_host = request.POST.get('s_account_host')
        account_grant = request.POST.get('s_account_grant').upper()
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
        page_max = math.ceil(total_count / 15)
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
            'page_max': page_max,
            'alert_type': "ERR_0"
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
        forceinsert_flag = request.POST.get('forceinsert_flag')

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        if account_grant == '':  # 권한 직접 입력인경우
            account_grant = request.POST.get('i_account_grant_direct').upper()

        # 패스워드 암호화 처리
        if is_password_encrypt_yn(account_pass) == True: # 암호화가 되있다면
            account_pass = get_password_decrypt(account_pass)

        put_password(account_pass)
        account_hash = get_password_hash(account_pass)
        account_pass = get_password_encrypt(account_pass)

        print("============================================================")
        print("입력란 테스트 선입니다.")
        print("============================================================")
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
        print("강제 입력 여부 : " + str(forceinsert_flag))
        print("============================================================")

        # HOST 여러대역 처리
        account_host_lists = account_host.split(',')

        for account_host_list in account_host_lists:
            account_host = account_host_list.replace(" ", "")

            account_sql = "/*" + account_svr + "*/ " + "USE mysql; " + "/*" + account_url + \
                            "*/" + " GRANT " + account_grant  + " ON " + \
                            account_db + "." + account_table + \
                            " TO " + "''" + account_user + "''@''" + account_host + \
                            "'' IDENTIFIED BY PASSWORD ''" + account_hash + "'';"
            print("sql : " + account_sql)

            insert_sql = "INSERT INTO account_account(account_create_dt, account_update_dt, " + \
                         "account_requestor, account_devteam, account_svr, account_user, " + \
                         "account_host, account_pass, account_hash, account_grant, account_grant_with, " + \
                         "account_db, account_table, account_info, account_sql, account_url, account_del_yn, account_del_reason, account_del_note) VALUES( " + \
                         "'" + last_modify_dt + "'," + \
                         "'" + last_modify_dt + "'," + \
                         "'" + account_requestor + "'," + \
                         "'" + account_devteam + "'," + \
                         "'" + account_svr + "'," + \
                         "'" + account_user + "'," + \
                         "'" + account_host + "'," + \
                         "'" + account_pass + "'," + \
                         "'" + account_hash + "'," + \
                         "'" + account_grant + "'," + \
                         "'N'," + \
                         "'" + account_db + "'," + \
                         "'" + account_table + "'," + \
                         "'" + account_info + "', " + \
                         "'" + account_sql + "'" + ", " + \
                         "'" + account_url + "', " + \
                         "'N', '', '')"

            # print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            # print("insert_sql : ")
            # print(insert_sql)
            # print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")


            # 강제 입력 여부. True면 정합성 체크 안함
            if forceinsert_flag == 'True':
                print("강제 입력 동작합니다")
                alert_type = "ERR_0"
                alert_message = ""

            else:
                print("강제 입력 동작 XXXXX !!!!")
                # 계정 정합성 체크. ERR_0 리턴 외 다른값이면 정합성간 문제 발생하여 쿼리 수행 안함
                alert_type, alert_message = check_account_consistency(account_svr, account_user, account_host, account_pass, account_db, account_table, account_grant)

            # 쿼리 수행
            # print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            # print("alert_type : " + alert_type)
            # print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

            if alert_type == "ERR_0":
                try:
                    cursor = connections['default'].cursor()
                    cursor.execute(insert_sql)
                    connection.commit()

                    # 성공 후 데일리 백업 체크, 히스토리 로깅
                    create_daily_backup_table(request, 'account')
                    log_history_insert(request, 'null', 'account', 'insert', insert_sql)

                except:
                    connection.rollback()

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
        page_max = math.ceil(total_count / 15)
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
            'page_max': page_max,
            'alert_type': alert_type,
            'alert_message': alert_message,
            'last_modify_dt': last_modify_dt
        }

        return render(request, 'account_select.html', context)

    else:
        return render(request, 'account.html')

def account_update(request):
    if request.method == 'POST':

        #### UPDATE
        u_id = request.POST.get('u_id')
        u_account_requestor = request.POST.get('u_account_requestor')
        u_account_svr = request.POST.get('u_account_svr')
        u_account_user = request.POST.get('u_account_user')
        u_account_devteam = request.POST.get('u_account_devteam')
        u_account_host = request.POST.get('u_account_host')
        u_account_pass = request.POST.get('u_account_pass')
        u_account_grant = request.POST.get('u_account_grant').upper()
        u_account_grant_with = request.POST.get('u_account_grant_with')
        u_account_db = request.POST.get('u_account_db')
        u_account_table = request.POST.get('u_account_table')
        u_account_info = request.POST.get('u_account_info')
        u_account_url = request.POST.get('u_account_url')
        forceupdate_flag = request.POST.get('forceupdate_flag')

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # 패스워드 암호화 처리
        if is_password_encrypt_yn(u_account_pass) == True: # 암호화가 되있다면
            u_account_pass = get_password_decrypt(u_account_pass)

        put_password(u_account_pass)
        u_account_hash = get_password_hash(u_account_pass)
        u_account_pass = get_password_encrypt(u_account_pass)

        print("================================================")

        u_account_sql = "/*" + u_account_svr + "*/ " + "USE mysql; " + "/*" + u_account_url + \
                              "*/" + " GRANT " + u_account_grant + " ON " + \
                              u_account_db + "." + u_account_table + \
                              " TO " + "''" + u_account_user + "''@''" + u_account_host + \
                              "'' IDENTIFIED BY PASSWORD ''" + u_account_hash + "'';"

        update_sql = "UPDATE account_account " + \
        "SET account_update_dt = '" + last_modify_dt + "'" + \
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
        ", account_sql = " + "'" + u_account_sql + "'" + \
        ", account_hash = " + "'" + u_account_hash + "'" + \
        " WHERE id = " + u_id + ";"

        print("============================================================")
        print("UPDATE 리턴값 테스트 선입니다.")
        print("============================================================")
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
        print("forceupdate_flag : " + str(forceupdate_flag))
        # print("============================================================")


        # 정합성 체크간 업데이트 중복계정 이슈로 못하던 문제 예외처리
        # 하나라도 정합성 체크에 필요한 항목이 업데이트 항목에 포함되있다면
        old_account = Account.objects.get(id=u_id)

        if old_account.account_svr != u_account_svr \
            or old_account.account_user != u_account_user \
            or old_account.account_host != u_account_host \
            or old_account.account_pass != u_account_pass \
            or old_account.account_db != u_account_db \
            or old_account.account_table != u_account_table \
            or old_account.account_grant != u_account_grant:

            # 계정 정합성 체크. ERR_0 리턴 외 다른값이면 정합성간 문제 발생하여 쿼리 수행 안함
            # print("정합성 체크 ON")
            # 강제 입력 여부. True면 정합성 체크 안함
            if forceupdate_flag == 'True':
                print("강제 수정 동작합니다")
                alert_type = "ERR_0"
                alert_message = ""

            else:
                print("강제 수정 동작 XXXXX !!!!")
                # 계정 정합성 체크. ERR_0 리턴 외 다른값이면 정합성간 문제 발생하여 쿼리 수행 안함
                alert_type, alert_message = check_account_consistency(u_account_svr, u_account_user, u_account_host, u_account_pass, u_account_db, u_account_table, u_account_grant)

        else:
            # print("정합성 체크 OFF")
            alert_type = "ERR_0"
            alert_message = ""


        # 쿼리 수행
        # print("alert_type : " + alert_type)
        # print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

        if alert_type == "ERR_0":
            try:
                cursor = connections['default'].cursor()
                cursor.execute(update_sql)
                connection.commit()

                # 성공 후 데일리 백업 체크, 히스토리 로깅
                create_daily_backup_table(request, 'account')
                log_history_insert(request, u_id, 'account', 'update', update_sql)

            except:
                connection.rollback()

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
        page_max = math.ceil(total_count / 15)
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
            'page_max': page_max,
            'alert_type': alert_type,
            'alert_message': alert_message,
            'last_modify_dt': last_modify_dt
        }

        return render(request, 'account_select.html', context)


    else:
        return render(request, 'account.html')

def account_delete(request):
    if request.method == 'POST':

        #### DELETE
        d_id = request.POST.get('d_id')
        d_account_requestor = request.POST.get('d_account_requestor')
        d_account_svr = request.POST.get('d_account_svr')
        d_account_user = request.POST.get('d_account_user')
        d_account_devteam = request.POST.get('d_account_devteam')
        d_account_host = request.POST.get('d_account_host')
        d_account_pass = request.POST.get('d_account_pass')
        d_account_grant = request.POST.get('d_account_grant')
        d_account_grant_with = request.POST.get('d_account_grant_with')
        d_account_db = request.POST.get('d_account_db')
        d_account_table = request.POST.get('d_account_table')
        d_account_info = request.POST.get('d_account_info')
        d_account_url = request.POST.get('d_account_url')
        d_account_del_reason = request.POST.get('d_account_del_reason')
        d_account_del_note = request.POST.get('d_account_del_note')

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

        delete_sql = "/*ACCOUNT DEL_YN=Y*/ UPDATE account_account " + \
        "SET account_del_dt = now() " + \
        ", account_del_yn = 'Y' " + \
        ", account_del_reason = " + "'" + d_account_del_reason+ "'" + \
        ", account_del_note = " + "'" + d_account_del_note + "'" + \
        " WHERE id = " + d_id + ";"

        print(delete_sql)
        # print("============================================================")

        try:
            cursor = connections['default'].cursor()
            cursor.execute(delete_sql)
            connection.commit()

            # 성공 후 데일리 백업 체크, 히스토리 로깅
            create_daily_backup_table(request, 'account')
            log_history_insert(request, d_id, 'account', 'delete', delete_sql)

        except:
            connection.rollback()
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
        page_max = math.ceil(total_count / 15)
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
            'page_max': page_max,
            'alert_type': "ERR_0"
        }

        return render(request, 'account_select.html', context)


    else:
        return render(request, 'account.html')

def account_multi_dml(request):
    if request.method == 'POST':
        checkboxValues = request.POST.getlist('checkboxValues[]')
        account_id_list = ",".join( repr(e) for e in checkboxValues).replace("'","") # QUERY에 쓰일 서버명

        # 수정 일시년월일 (또는 입력일시)
        last_modify_dt = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        if len(checkboxValues) != 0:
            # print("입력값 있음")
            dml_type = request.POST.get('dml_type')

            if dml_type == 'update':
                mu_type = request.POST.get('mu_type')
                mu_value = request.POST.get('mu_value')

                # 권한 입력의 경우, 대문자로 처리
                if mu_type == 'account_grant':
                    mu_value = mu_value.upper()

                u_query = "/*MULTI-UPDATE*/UPDATE account_account SET account_update_dt = '" + last_modify_dt + "', " + \
                            mu_type + " = '" + mu_value + "' WHERE id IN(" + account_id_list + ")"

                # 패스워드 암호화 처리
                if mu_type == 'account_pass':
                    print("다중 패스워드 변경")
                    account_pass = mu_value
                    if is_password_encrypt_yn(account_pass) == True:  # 암호화가 되있다면
                        account_pass = get_password_decrypt(account_pass)

                    put_password(account_pass)
                    account_hash = get_password_hash(account_pass)
                    account_pass = get_password_encrypt(account_pass)

                    u_query = "/*MULTI-UPDATE*/UPDATE account_account SET account_update_dt = '" + last_modify_dt + "', " + \
                                mu_type + " = '" + account_pass + "', account_hash ='" + account_hash +"' WHERE id IN(" + account_id_list + ")"

                    print(u_query)

                # print("==========================================================")
                # print("업데이트가 들어왔네")
                # print(account_id_list)
                # print(mu_type)
                # print(mu_value)
                # print(u_query)
                # print("==========================================================")

                try:
                    cursor = connections['default'].cursor()
                    cursor.execute(u_query)
                    connection.commit()

                    # 성공 후 데일리 백업 체크, 히스토리 로깅.
                    create_daily_backup_table(request, 'account')
                    log_history_insert(request,  "'" + account_id_list + "'", 'account', 'update', u_query)

                    # 다중 업데이트의 경우, account_sql 재 보정 필요
                    recreate_account_sql(request, account_id_list)

                except:
                    connection.rollback()
                finally:
                    cursor.close()

            elif dml_type == 'delete':
                md_account_del_reason = request.POST.get('md_account_del_reason')
                md_account_del_note = request.POST.get('md_account_del_note')
                d_query = "/*MULTI-DELETE ACCOUNT DEL_YN=Y*/ UPDATE account_account " + \
                             "SET account_del_dt = '" + last_modify_dt + "'" \
                             ", account_del_yn = 'Y'" + \
                             ", account_del_reason = " + "'" + md_account_del_reason + "'" + \
                             ", account_del_note = " + "'" + md_account_del_note + "'" + \
                             " WHERE id IN(" + account_id_list + ")"

                # print("==========================================================")
                # print("삭제가 들어왔네")
                # print(account_id_list)
                # print(md_account_del_reason)
                # print(md_account_del_note)
                # print(d_query)
                # print("==========================================================")

                try:
                    cursor = connections['default'].cursor()
                    cursor.execute(d_query)
                    connection.commit()

                    # 성공 후 데일리 백업 체크, 히스토리 로깅
                    create_daily_backup_table(request, 'account')
                    log_history_insert(request, "'" + account_id_list + "'", 'account', 'delete', d_query)

                except:
                    connection.rollback()
                finally:
                    cursor.close()

            alert_type = "ERR_0"
            alert_message = ""

        else:
            alert_type = "ERR_3"
            alert_message = "반영 대상이 없습니다. 작업대상 ID 체크박스를 클릭해주세요."
            last_modify_dt = ""


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
        page_max = math.ceil(total_count / 15)
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
            'page_max': page_max,
            'alert_type': alert_type,
            'alert_message': alert_message,
            'last_modify_dt': last_modify_dt
        }

        return render(request, 'account_select.html', context)


    else:
        return render(request, 'account.html')


#########################################################################
# Account remove page. account_del_yn='Y'
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
        page_max = math.ceil(total_count / 15)
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

@login_required
def account_repository(request):
    return render(request, 'account_repository.html')

@login_required
def account_repository_select(request):
    if request.method == 'POST':
        s_repository_team = request.POST.get('s_repository_team')
        s_repository_type = request.POST.get('s_repository_type')
        s_repository_name = request.POST.get('s_repository_name')
        s_repository_url = request.POST.get('s_repository_url')
        s_account_user = request.POST.get('s_account_user')
        s_url = request.POST.get('s_url')
        s_info = request.POST.get('s_info')

        repository_list = AccountRepository.objects.filter(
            repository_team__contains=s_repository_team,
            repository_type__contains=s_repository_type,
            repository_name__contains=s_repository_name,
            repository_url__contains=s_repository_url,
            account_user__contains=s_account_user,
            url__contains=s_url,
            info__contains=s_info
        ).order_by('-id')

        s_total_count = repository_list.count()


        context = {
            'repository_list': repository_list,
            'repository_team': s_repository_team,
            'repository_type': s_repository_type,
            'repository_name': s_repository_name,
            'repository_url': s_repository_url,
            'account_user': s_account_user,
            'url': s_url,
            'info': s_info,
            'total_count': s_total_count
        }

        return render(request, 'account_repository_select.html', context)

    else:
        return render(request, 'account_repository.html')

def account_repository_insert(request):
    if request.method == 'POST':
        i_repository_team = request.POST.get('i_repository_team')
        i_repository_type = request.POST.get('i_repository_type')
        i_repository_name = request.POST.get('i_repository_name')
        i_repository_url = request.POST.get('i_repository_url')
        i_account_user = request.POST.get('i_account_user')
        i_url = request.POST.get('i_url')
        i_info = request.POST.get('i_info')

        insert_sql = "INSERT INTO account_repository(create_dt, repository_team, repository_type, " + \
                    "repository_name, repository_url, account_user, url, info) VALUES(" + \
                    "now(), " + \
                    "'" + i_repository_team + "', " + \
                    "'" + i_repository_type + "', " + \
                    "'" + i_repository_name + "', " + \
                    "'" + i_repository_url + "', " + \
                    "'" + i_account_user + "', " + \
                    "'" + i_url + "', " + \
                    "'" + i_info + "')"

        # print(insert_sql)

        try:
            cursor = connections['default'].cursor()
            cursor.execute(insert_sql)
            connection.commit()

            # 성공 후 데일리 백업 체크, 히스토리 로깅
            create_daily_backup_table(request, 'repository')
            log_history_insert(request, 'null', 'repository', 'insert', insert_sql)
        except:
            connection.rollback()
        finally:
            cursor.close()

        # 마지막 수정값
        last_modify_dt = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        s_repository_team = request.POST.get('s_repository_team')
        s_repository_type = request.POST.get('s_repository_type')
        s_repository_name = request.POST.get('s_repository_name')
        s_repository_url = request.POST.get('s_repository_url')
        s_account_user = request.POST.get('s_account_user')
        s_url = request.POST.get('s_url')
        s_info = request.POST.get('s_info')

        # print("-----------------------------------------------")
        # print(i_repository_team)
        # print(i_repository_type)
        # print(i_repository_name)
        # print(i_repository_url)
        # print(i_account_user)
        # print(i_url)
        # print(i_info)
        #
        # print(s_repository_team)
        # print(s_repository_name)
        # print(s_repository_url)
        # print(s_account_user)
        # print(s_url)
        # print(s_info)
        # print("-----------------------------------------------")

        repository_list = AccountRepository.objects.filter(
            repository_team__contains=s_repository_team,
            repository_type__contains=s_repository_type,
            repository_name__contains=s_repository_name,
            repository_url__contains=s_repository_url,
            account_user__contains=s_account_user,
            url__contains=s_url,
            info__contains=s_info
        ).order_by('-id')

        s_total_count = repository_list.count()

        context = {
            'repository_list': repository_list,
            'repository_team': s_repository_team,
            'repository_type': s_repository_type,
            'repository_name': s_repository_name,
            'repository_url': s_repository_url,
            'account_user': s_account_user,
            'url': s_url,
            'info': s_info,
            'total_count': s_total_count
        }

        return render(request, 'account_repository_select.html', context)

    else:
        return render(request, 'account_repository.html')

def account_repository_update(request):
    if request.method == 'POST':
        u_id = request.POST.get('u_id')
        u_repository_team = request.POST.get('u_repository_team')
        u_repository_type = request.POST.get('u_repository_type')
        u_repository_name = request.POST.get('u_repository_name')
        u_repository_url = request.POST.get('u_repository_url')
        u_account_user = request.POST.get('u_account_user')
        u_url = request.POST.get('u_url')
        u_info = request.POST.get('u_info')

        update_sql = "UPDATE account_repository SET " + \
                     "repository_team = " + "'" + u_repository_team + "'" + \
                     ", repository_type = " + "'" + u_repository_type + "'" + \
                     ", repository_name = " + "'" + u_repository_name + "'" + \
                     ", repository_url = " + "'" + u_repository_url + "'" + \
                     ", account_user = " + "'" + u_account_user + "'" + \
                     ", url = " + "'" + u_url + "'" + \
                     ", info = " + "'" + u_info + "'" + \
                     " WHERE id = " + u_id + ";"

        # print(update_sql)

        try:
            cursor = connections['default'].cursor()
            cursor.execute(update_sql)
            connection.commit()

            # 성공 후 데일리 백업 체크, 히스토리 로깅
            create_daily_backup_table(request, 'repository')
            log_history_insert(request, u_id, 'repository', 'update', update_sql)

        except:
            connection.rollback()

        finally:
            cursor.close()

        # 마지막 수정값
        last_modify_dt = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        s_repository_team = request.POST.get('s_repository_team')
        s_repository_type = request.POST.get('s_repository_type')
        s_repository_name = request.POST.get('s_repository_name')
        s_repository_url = request.POST.get('s_repository_url')
        s_account_user = request.POST.get('s_account_user')
        s_url = request.POST.get('s_url')
        s_info = request.POST.get('s_info')

        # print("-----------------------------------------------")
        # print(u_repository_team)
        # print(u_repository_name)
        # print(u_repository_url)
        # print(u_account_user)
        # print(u_url)
        # print(u_info)
        #
        # print(s_repository_team)
        # print(s_repository_name)
        # print(s_repository_url)
        # print(s_account_user)
        # print(s_url)
        # print(s_info)
        # print("-----------------------------------------------")

        repository_list = AccountRepository.objects.filter(
            repository_team__contains=s_repository_team,
            repository_type__contains=s_repository_type,
            repository_name__contains=s_repository_name,
            repository_url__contains=s_repository_url,
            account_user__contains=s_account_user,
            url__contains=s_url,
            info__contains=s_info
        ).order_by('-id')

        s_total_count = repository_list.count()

        context = {
            'repository_list': repository_list,
            'repository_team': s_repository_team,
            'repository_type': s_repository_type,
            'repository_name': s_repository_name,
            'repository_url': s_repository_url,
            'account_user': s_account_user,
            'url': s_url,
            'info': s_info,
            'total_count': s_total_count
        }

        return render(request, 'account_repository_select.html', context)

    else:
        return render(request, 'account_repository.html')






