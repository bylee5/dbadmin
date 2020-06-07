
SELECT password_hash FROM account_hash WHERE password_hash=PASSWORD('hoho!!kKee1');
#######################################################################################################
# account
#######################################################################################################
SELECT * FROM account_account ORDER BY 1 DESC;

SELECT id, AES_DECRYPT(UNHEX(password_encrypt), '****~!!1') AS pass, password_encrypt, password_hash FROM dbadmin.account_hash ORDER BY 1 DESC;


SELECT * FROM account_repository;

DESC account_repository;
DESC account_account;

UPDATE account_account SET account_del_dt=NULL, account_end_dt=NULL
UPDATE account_account SET account_del_dt='2020-04-21 22:36:18' WHERE account_del_yn='Y'

## 전체 조회
SELECT * FROM account_account ORDER BY 1 DESC;
## 전체 조회 (패스워드 부분)
SELECT * FROM account_account ORDER BY 1 DESC;

### 삭제 초기화
UPDATE account_account SET account_del_yn='N', account_del_reason='', account_del_note='', account_del_dt=NULL;

### 삭제 조회
SELECT id, account_create_dt, account_requestor, account_svr, account_user, account_host, account_pass, account_del_dt, account_del_yn, account_del_reason, account_del_note
FROM account_account WHERE account_del_yn='Y' ORDER BY 1 DESC;


SELECT USER, HOST FROM mysql.user;
SHOW CREATE USER 'test'@'10.11.19.%';
SHOW GRANTS FOR 'test'@'10.11.19.%';


-- GRANT SELECT ON `testdb`.* TO 'test'@'10.11.20.%' IDENTIFIED BY PASSWORD '*6A654172F7C08BAA30B145980AA553792E9DFFC3';
-- GRANT SELECT ON `testdb`.* TO 'test'@'10.11.22.%' IDENTIFIED WITH 'mysql_native_password' AS '*6A654172F7C08BAA30B145980AA553792E9DFFC3';
-- CREATE USER 'test'@'10.11.19.%' IDENTIFIED WITH 'mysql_native_password' AS '*6A654172F7C08BAA30B145980AA553792E9DFFC3
#GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY PASSWORD '*A77XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' WITH GRANT OPTION





SHOW WARNINGS

#######################################################################################################
# 암복호화
#######################################################################################################

-- select HEX(AES_ENCRYPT('Manger!1', '****~!!1'));
-- SELECT AES_DECRYPT(UNHEX('23D5F3AF5041ABADF64E89F1FCE0A994'), '****~!!1');

SHOW GRANTS FOR 'test1'@'localhost';

GRANT ALL PRIVILEGES ON *.* TO 'ODBC'@'localhost' IDENTIFIED BY "패스워드";
FLUSH PRIVILEGES;

SHOW TABLES;
SELECT * FROM account_hash;


SELECT PASSWORD('manager');


# 패스워드 조회
SELECT id, AES_DECRYPT(UNHEX(password_encrypt), '****~!!1') AS pass, password_encrypt, password_hash FROM dbadmin.account_hash ORDER BY 1 DESC;

--     id  AES_DECRYPT(UNHEX(password_encrypt), '****~!!1')  password_encrypt                  password_hash
-- ------  ------------------------------------------------  --------------------------------  -------------------------------------------
--      1  (NULL)                                            manager                           *7D2ABFF56C15D67445082FBB4ACD2DCD26C0ED57
--      2  manager                                           6F0508A8A51C7B98E0C0F316D797B98D  *7D2ABFF56C15D67445082FBB4ACD2DCD26C0ED57
--      4  hoho!!kKee@                                       B4E00120C4137CE0070E8E719C7CE7A1  *5CE39A29BB2B3BBE6293BC10E9404F058109A152
--
SELECT USER, HOST, authentication_string, password_expired, account_locked FROM mysql.user;
SHOW GRANTS FOR 'intra_write'@'10.11.11.%';

# grant select on admdb.* to 'test'@'10.11.22.%' identified by password '*5CE39A29BB2B3BBE6293BC10E9404F058109A152';
CREATE USER 'test'@'10.11.21.%' IDENTIFIED WITH mysql_native_password BY '*5CE39A29BB2B3BBE6293BC10E9404F058109A152';


#######################################################################################################
# testing
#######################################################################################################


SELECT * FROM testing_faq;
SELECT * FROM testing_post;


DESC testing_post;

#alter table testing_faq convert to character set utf8;
#alter table testing_post convert to character set utf8;

#INSERT INTO testing_faq SELECT * FROM home_faq;
#INSERT INTO testing_post SELECT * FROM home_post;



#######################################################################################################
# 장고 어드민 조회
#######################################################################################################

SELECT * FROM auth_group ORDER BY 1 DESC;
SELECT * FROM auth_group_permissions ORDER BY 1 DESC;

SELECT * FROM auth_permission ORDER BY 1 DESC;
SELECT * FROM auth_user ORDER BY 1 DESC; -- 사용자 계정
#select * from auth_user_groups order by 1 desc;
#select * from auth_user_user_permissions order by 1 desc;
#select * from django_admin_log order by 1 desc;
SELECT * FROM django_content_type ORDER BY 1 DESC;
#select * from django_migrations order by 1 desc;
SELECT * FROM django_session ORDER BY 1 DESC;



SELECT NOW(), DATE_ADD(NOW(), INTERVAL 20 SECOND);