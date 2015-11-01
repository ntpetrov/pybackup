#!/usr/bin/env python

import smtplib
import yaml
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

config = yaml.safe_load(open("config.yml"))

def mail_notify():
    filename = config['rsync']['log_file']
    body = config['mail']['body']
    toEmail = config['mail']['to']
    fromEmail = config['mail']['from']
    subject = config['mail']['subject']
    msg = MIMEMultipart('alternative')
    host = config['mail']['host']
    port = config['mail']['port']
    password = config['mail']['pass']
    s = smtplib.SMTP('%s' %host, port)
#    s.starttls()
    s.login('%s' %fromEmail,'%s' %password)
    msg['Subject'] = subject
    msg['From'] = fromEmail
    f = file(filename)
    attachment = MIMEText(f.read())
    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(attachment)
    content = MIMEText(body, 'plain')
    msg.attach(content)
    s.sendmail(fromEmail, toEmail, msg.as_string())

if __name__ == "__main__":
   mail_notify() 
