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


def read_next_product():
    cursor.execute("SELECT * FROM next_product")

    myresult = cursor.fetchall()

    return myresult[0][0]


def update_next_product(name):
    sql = "UPDATE next_product SET name = '%s'" % name

    cursor.execute(sql)

    dotops_database.commit()

