import mysql.connector
from mysql.connector.constants import ClientFlag
import secrets

config = {
    'user': secrets.user,
    'password': secrets.password,
    'host': secrets.host,
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': 'ssl/server-ca.pem',
    'ssl_cert': 'ssl/client-cert.pem',
    'ssl_key': 'ssl/client-key.pem',
    'database': 'database1'
}

dotops_DB = mysql.connector.connect(**config)

cursor = dotops_DB.cursor()


def read_next_product():
    cursor.execute("SELECT * FROM next_product")

    myresult = cursor.fetchall()

    return myresult[0][0]


def update_next_product(name):
    sql = "UPDATE next_product SET name = '%s'" % name

    cursor.execute(sql)

    dotops_DB.commit()

