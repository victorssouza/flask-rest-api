from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from collections import OrderedDict
# Custom lib
from database_manager import DatabaseManager

app = Flask(__name__)

def __init__():
    database_manager = DatabaseManager()
    mysql_database_host = database_manager.getting_database_instance()
    conn, cursor = database_manager.start_connection(mysql_database_host)

@app.errorhandler(404)
def page_not_found(error):
    #return render_template('not_found.html'), 404
    return json.dumps({"message":"page not found","status":False}), 404, {'Content-Type': 'application/json; charset=utf-8'}

@app.route("/")
def main():
        mysql_database_host = database_manager.getting_database_instance()
        status_db_connection, conn, cursor = database_manager.start_connection(mysql_database_host)
        if status_db_connection:
            return render_template('index.html'), 200
        else:
            return json.dumps({"status":False,"message":"{}".format(cursor)}), {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/api/v1/mock/recreate-table", methods=["POST"])
def create_tbls():
    if request.method == 'POST':
        mysql_database_host = database_manager.getting_database_instance()
        conn, cursor = database_manager.start_connection(mysql_database_host)

        db_table = request.form['table']
        sql_drop_tables = """DROP TABLE IF EXISTS {}""".format(db_table)
        sql_create_tables = """CREATE TABLE `FlaskWebApp`.`{}` (
            `user_id` BIGINT NULL AUTO_INCREMENT,
            `user_name` VARCHAR(200) NULL,
            `user_login` VARCHAR(20) NULL,
            `user_email` VARCHAR(200) NULL,
            `user_password` VARCHAR(200) NULL,
            `active` BOOLEAN NOT NULL DEFAULT TRUE,
            PRIMARY KEY (`user_id`));""".format(db_table)
        try:
            cursor.execute(sql_drop_tables)
            cursor.execute(sql_create_tables)
            return json.dumps({"status":True,"message":"table recreated"}), 201, {'Content-Type': 'application/json; charset=utf-8'}
        except Exception as e:
            return json.dumps({"status":False,"message":"failed: {}".format(e)}), 500, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return "True"

@app.route("/api/v1/mock/populate-table", methods=["POST"])
def populate_tbls():
    if request.method == 'POST':
        mysql_database_host = database_manager.getting_database_instance()
        conn, cursor = database_manager.start_connection(mysql_database_host)

        default_users = [
                        {"name":"Luis Gomes","login":"lugomes","email":"luis.gomes@tam.com","password":"1231"},
                        {"name":"Roberto Kawasaki","login":"rkawasaki","email":"robbies.kk@uol.com","password":"senha1"},
                        {"name":"Albertovaldo Melo","login":"amelo","email":"albertovv_@postit.com","password":"pass"},
                        {"name":"Postit A4","login":"post4","email":"postit.afour@tam.com","password":"312313"},
                        {"name":"Farshad Momtaz Jr.","login":"fmomtaz","email":"farshad@samsung.com","password":"password"},
                        {"name":"Lais Gomes","login":"lagomes","email":"luis.gomes@icon.com.br","password":"mypass123"},
                        {"name":"Prado Mary","login":"pmary","email":"prado.mary@mercadolivre.com.br","password":"livelo"},
                        {"name":"Paper Jobs","login":"pjobs","email":"pap@apple.com.br","password":"randomone"},
                        {"name":"Bill Gates","login":"bgates","email":"bill_handsome_71@microsoft.com","password":"ransom"},
                        {"name":"Rosa Mattos","login":"rmattos","email":"rosa.mattos@gmail.com","password":"iris"}
                        ]
        for user in default_users:
            user_password_hashed = generate_password_hash(user['password'])
            insert_query = (""" INSERT INTO {} (user_name,user_login, user_email,user_password) VALUES ('{}','{}','{}','{}')""").format(request.form['table'],user['name'],user['login'],user['email'],user_password_hashed)
            try:
                cursor.execute(insert_query)
                conn.commit()
            except Exception as e:
                return json.dumps({"status":False,"message":"failed: {}".format(e)}), 500, {'Content-Type': 'application/json; charset=utf-8'}
        return json.dumps({"status":True,"message":"fake data inserted"}), 201, {'Content-Type': 'application/json; charset=utf-8'}

@app.route("/api/v1/users/", methods=["GET","POST"])
def create_users():
    if request.method == 'POST':
        mysql_database_host = database_manager.getting_database_instance()
        conn, cursor = database_manager.start_connection(mysql_database_host)

        name = request.form['name']
        login = request.form['login'].replace(" ","").lower()
        email = request.form['email'].replace(" ","").lower()
        password = request.form['password']
        user_password_hashed = generate_password_hash(password)
        sql_query = """INSERT INTO users (user_name,user_login,user_email,user_password) VALUES ('{}','{}','{}','{}')""".format(name, login, email, user_password_hashed)
        try:
            cursor.execute(sql_query)
            conn.commit()
            return json.dumps({"status":True,"message":"user '{}' created".format(request.form['login'].replace(" ","").lower())}), {'Content-Type': 'application/json; charset=utf-8'}
        except:
            return json.dumps({"status":False,"message":"user not created"}), {'Content-Type': 'application/json; charset=utf-8'}
    if request.method == 'GET':
        mysql_database_host = database_manager.getting_database_instance()
        status_db_connection, conn, cursor = database_manager.start_connection(mysql_database_host)
        if  status_db_connection:
            return database_manager.getting_users(cursor)
        else:
            return json.dumps({"status":False,"message":"{}".format(cursor)}), {'Content-Type': 'application/json; charset=utf-8'}

@app.route("/api/v1/users/search/q=<search_key>:<search_value>")
def search_users_from_attributes(search_key,search_value):
    mysql_database_host = database_manager.getting_database_instance()
    conn, cursor = database_manager.start_connection(mysql_database_host)

    if search_key == 'login':
        search_key = 'user_login'
    elif search_key == 'email':
        search_key = 'user_email'
    else:
        return json.dumps({"message":"not a valid url param","status":False}), {'Content-Type': 'application/json; charset=utf-8'}

    search_users_from_attributes = ("""SELECT * FROM users WHERE {} = '{}' AND active = 1""").format(search_key, search_value)
    cursor.execute(search_users_from_attributes)

    user = []
    for (user_id, user_name, user_login, user_email, user_password, active) in cursor:
        user_list = {
                   "id":user_id,
                   "name":"{}".format(user_name),
                   "login":"{}".format(user_login),
                   "email":"{}".format(user_email)
                   }
        user.append(user_list)

    if user == []:
        return json.dumps({"message":"user not found","status":False}), {'Content-Type': 'application/json; charset=utf-8'}
    return json.dumps(user), {'Content-Type': 'application/json; charset=utf-8'}

@app.route("/api/v1/users/<user_id>", methods=["GET", "PUT"])
def consult_specific_user(user_id):
    if request.method == 'GET':
        mysql_database_host = database_manager.getting_database_instance()
        conn, cursor = database_manager.start_connection(mysql_database_host)

        try:
            int(user_id)
        except:
            return json.dumps({"message":"invalid input","status":False}), {'Content-Type': 'application/json; charset=utf-8'}
        search_user_query = """SELECT * FROM users WHERE user_id = {} AND active = 1""".format(user_id)
        query_result = cursor.execute(search_user_query)
        if str(query_result) == "0":
            return json.dumps({"message":"user not found"}), {'Content-Type': 'application/json; charset=utf-8'}
        elif str(query_result) == "1":
            for (user_id, user_name, user_login, user_email, user_password, active) in cursor:
                user_list = {
                            "id":user_id,
                            "name":"{}".format(user_name),
                            "login":"{}".format(user_login),
                            "email":"{}".format(user_email)
                }
            return json.dumps(user_list, sort_keys=False), {'Content-Type': 'application/json; charset=utf-8'}
        else:
            return json.dumps({"message":"something is wrong!"}), {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'PUT':
        mysql_database_host = database_manager.getting_database_instance()
        conn, cursor = database_manager.start_connection(mysql_database_host)

        if request.form['name'] or request.form['email']:
            if request.form['name']:
                name_update_query = """UPDATE users SET user_name = '{}' WHERE user_id = '{}'""".format(request.form['name'],user_id)
                cursor.execute(name_update_query)
            if request.form['email']:
                email_update_query = """UPDATE users SET user_email = '{}' WHERE user_id = '{}'""".format(request.form['email'],user_id)
                cursor.execute(email_update_query)
            return json.dumps({"status":True,"message":"email updated"}), {'Content-Type': 'application/json; charset=utf-8'}
        else:
            return json.dumps({"status":False}), {'Content-Type': 'application/json; charset=utf-8'}

if __name__ == "__main__":
    database_manager = DatabaseManager()
    app.run(port=8080, host='0.0.0.0')
