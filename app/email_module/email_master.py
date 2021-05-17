import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import os


def modify_template(html_string, mod_dict):

    soup = BeautifulSoup(html_string, 'html.parser')

    for modification in mod_dict['text']:
        # print(modification)
        text = soup.find(id=modification)
        text.string.replace_with(mod_dict['text'][modification])

    for modification in mod_dict['images']:
        image = soup.find(id=modification)
        image['src'] = mod_dict['images'][modification]

    return soup


def send_email(receiver_email, subject, template, data_dict):

    print('SENDING EMAIL...')

    port = 465  # For SSL
    system_email = os.environ.get("email_address")
    password = os.environ.get("email_password")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = 'system@dotops.app'
    message["To"] = receiver_email

    file = open(template, "r", encoding="utf-8")
    html = file.read()
    file.close()

    custom_html = modify_template(html, data_dict)

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(custom_html, "html", "utf-8")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(system_email, password)

        server.sendmail(system_email, receiver_email, message.as_string())
        print('EMAIL SENT!')
