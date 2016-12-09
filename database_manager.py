import os
from flask import Flask, json
from flaskext.mysql import MySQL

class DatabaseManager():

    def getting_database_instance(self):
        # Checking if it exist a kubernetes' mysql pod
        if 'FLASK_WEB_DB_PORT_3306_TCP_ADDR' in os.environ:
            mysql_database_host = os.environ['FLASK_WEB_DB_PORT_3306_TCP_ADDR']
            mysql_port = 3306
        # Checking if it exist a mysql container
        elif 'MYSQL_PORT_3306_TCP_ADDR' in os.environ:
            mysql_database_host = os.environ['MYSQL_PORT_3306_TCP_ADDR']
            mysql_port = 3306
        else:
            mysql_database_host = '127.0.0.1'
        return mysql_database_host

    def start_connection(self, mysql_database_host='127.0.0.1'):
        app = Flask(__name__)
        app.config['DEBUG'] = True
        app.config['MYSQL_DATABASE_HOST'] = mysql_database_host
        app.config['MYSQL_DATABASE_USER'] = 'root'
        app.config['MYSQL_DATABASE_PASSWORD'] = 'app'
        app.config['MYSQL_DATABASE_DB'] = 'FlaskWebApp'
        app.config['MYSQL_DATABASE_PORT'] = 3309
        status_db_connection = False

        mysql = MySQL()
        try:
            mysql.init_app(app)
            conn = mysql.connect()
            cursor = conn.cursor()
            status_db_connection = True
            return status_db_connection, conn, cursor
        except Exception as e:
            error_status, error_message = e.args

            # 2003: Code if we can't reach MySQL
            if error_status == 2003:
                error_treated_message = "[FATAL]: Can't connect to MySQL server. Check if Database is up."
                print(error_treated_message)
                return status_db_connection, error_status, error_treated_message
            elif error_status == 1045:
                error_treated_message = "[FATAL]: Access denied when trying to connect to Database: {}".format(mysql_database_host)
                print(error_treated_message)
                return status_db_connection, error_status, error_treated_message
            else:
                error_treated_message = "[FATAL]: Database error: {}".format(e.args)
                print(error_treated_message)
                return status_db_connection, error_status, error_treated_message

    def getting_users(self,cursor,additional_param=''):
        try:
            cursor.execute("SELECT * FROM users {}".format(additional_param))
        except Exception as e:
            # Table users not created
            if e.args[0] == 1146:
                error_treated_message = "[FATAL]: Search failed due an inexistent 'users' table"
                print(error_treated_message)
                return json.dumps({"message":"{}".format(error_treated_message),"status":False}), 500, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                error_treated_message = "[FATAL]: Database error: {}".format(e)
                return json.dumps({"message":"{}".format(error_treated_message),"status":False}), 500, {'Content-Type': 'application/json; charset=utf-8'}

        users_info = []

        for (user_id, user_name, user_login, user_email, user_password, active) in cursor:
            user_list = {
                        "id":user_id,
                        "name":"{}".format(user_name),
                        "login":"{}".format(user_login),
                        "email":"{}".format(user_email)
            }
            users_info.append(user_list)
        return json.dumps(users_info,sort_keys=False), 200, {'Content-Type': 'application/json; charset=utf-8'}
