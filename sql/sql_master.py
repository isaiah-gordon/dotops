import mysql.connector
from mysql.connector.constants import ClientFlag
from sql import secrets

config = {
    'user': secrets.user,
    'password': secrets.password,
    'host': secrets.host,
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': 'sql/ssl/server-ca.pem',
    'ssl_cert': 'sql/ssl/client-cert.pem',
    'ssl_key': 'sql/ssl/client-key.pem',
    'database': 'database1'
}

dotops_database = mysql.connector.connect(**config)

cursor = dotops_database.cursor()


def game_status():
    cursor.execute("SELECT status FROM active_game")

    result = cursor.fetchall()

    return result[0][0]


def read():
    cursor.execute("SELECT * FROM active_game")

    result = cursor.fetchall()

    return result[0]


def update(dict):

    for key in dict:
        sql = "UPDATE active_game SET %s = '%s'" % (key, dict[key])
        cursor.execute(sql)

    dotops_database.commit()
