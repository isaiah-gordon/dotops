import mysql.connector
from mysql.connector.constants import ClientFlag
import os

# LOCAL TESTING
# config = {
#     'user': os.environ.get("database_user"),
#     'password': os.environ.get("database_password"),
#     'host': os.environ.get("database_host"),
#     'client_flags': [ClientFlag.SSL],
#     'ssl_ca': 'ssl/server-ca.pem',
#     'ssl_cert': 'ssl/client-cert.pem',
#     'ssl_key': 'ssl/client-key.pem',
#     'database': 'database1'
# }

# SERVER CONFIG
config = {
    'user': os.environ.get("database_user"),
    'password': os.environ.get("database_password"),
    'host': os.environ.get("database_host"),
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': 'app/sql/ssl/server-ca.pem',
    'ssl_cert': 'app/sql/ssl/client-cert.pem',
    'ssl_key': 'app/sql/ssl/client-key.pem',
    'database': 'database1'
}

dotops_database = mysql.connector.connect(**config)

cursor = dotops_database.cursor(dictionary=True)


def store_profile_lookup(store_number, search_key):
    cursor.execute("SELECT {0} FROM store_profiles WHERE store_number = '{1}'".format(search_key, store_number))
    result = cursor.fetchall()

    dotops_database.commit()
    return result[0][search_key]


def find_user(email):
    cursor.execute("SELECT * FROM users WHERE email = '%s'" % email)
    result = cursor.fetchall()

    if not result:
        return False

    dotops_database.commit()

    return result[0]


def query(sql_query):
    cursor.execute(sql_query)

    result = cursor.fetchall()

    dotops_database.commit()

    return result
