"""
Copyright (c) 2024 豆伯

This software is licensed under the MIT License. See LICENSE for details.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pathlib

class SendMail:
    def __init__(self, account, password, smtp_server='smtp.gmail.com', smtp_port=587):
        self.account = account
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    
    def send(self, to, subject, content, attach_file=None):
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.account
        msg['To'] = to

        msg.attach(MIMEText(content))

        if attach_file is not None:
            with open(attach_file, 'rb') as f:
                content = f.read()
            attach_file = MIMEApplication(content, Name=pathlib.Path(attach_file).name)
            msg.attach(attach_file)

        smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(self.account, self.password)
        status = smtp.send_message(msg)
        smtp.quit()
        return status