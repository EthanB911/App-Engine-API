# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_cloudsql_mysql]
import os
from flask import Flask
import pymysql
import random

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
instance_name = os.environ.get('GAE_INSTANCE')

app = Flask(__name__)

@app.route('/')
def main():
    # When deployed to App Engine, the `GAE_ENV` environment variable will be
    # set to `standard`
    records_to_insert = []
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user, password=db_password,
                              unix_socket=unix_socket, db=db_name)
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        host = '127.0.0.1'
        cnx = pymysql.connect(user=db_user, password=db_password,
                              host=host, db=db_name)

    for i in range(0, 100):
        n = random.randint(1, 100000)
        records_to_insert.append((n, instance_name))

    with cnx.cursor() as cursor:
        mySql_insert_query = """INSERT INTO generated_number ( number, instance_name) VALUES (%s, %s) """
        cursor.executemany(mySql_insert_query, records_to_insert)
        #current_msg = result[0][0]
    cnx.commit()
    cnx.close()

    return {"results" : records_to_insert}
# [END gae_python37_cloudsql_mysql]
@app.route('/remove')
def remove():
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user, password=db_password,
                              unix_socket=unix_socket, db=db_name)
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        host = '127.0.0.1'
        cnx = pymysql.connect(user=db_user, password=db_password,
                              host=host, db=db_name)
    with cnx.cursor() as cursor:
        cursor.execute('delete from generated_number;')
    cnx.commit()
    cnx.close()

@app.route('/minmax')
def minmax():
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user, password=db_password,
                              unix_socket=unix_socket, db=db_name)
    else:
        # If running locally, use the TCP connections instead
        # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        # so that your application can use 127.0.0.1:3306 to connect to your
        # Cloud SQL instance
        host = '127.0.0.1'
        cnx = pymysql.connect(user=db_user, password=db_password,
                              host=host, db=db_name)


    with cnx.cursor() as cursor:
        cursor.execute('select min(number) as MIN , max(number) as MAX, instance_name from generated_number group by instance_name;')
        instances = cursor.fetchall()



    cnx.commit()
    cnx.close()

    return {"instances": instances}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
