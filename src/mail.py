import smtplib
from email.message import EmailMessage
import logging
from configparser import ConfigParser

logger = logging.getLogger()

def send_email():
    try:
        config = ConfigParser()
        config.read('src/config_file.txt')

        gmail_username = config['gmail_credentials']['gmail_username']
        gmail_pass = config['gmail_credentials']['gmail_password']

        msg = EmailMessage()
        msg.set_content('Unable to connect to trading server. Check status')

        msg['Subject'] = 'Trading Server Error'
        msg['From'] = gmail_username
        msg['To'] = gmail_username

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_username, gmail_pass)
        server.send_message(msg)
        server.close()
        print('Server error, Email sent to user')
        logger.info('Server error, Email sent to user')
    except:
        print('Error while sending Email, check credentials')
        logger.error('Error while sending Email, check credentials')
