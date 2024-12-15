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

# msg = MIMEMultipart('Hello World!') # 郵件內容
# msg['Subject'] = 'Gmail sent by Python scripts' # 郵件標題
# msg['From'] = '5b1g0028@stust.edu.tw'
# msg['To'] = 'willie@goodjob.idv.tw'

# with open("D:\DevProgram\Project\python\obfuscated_p21x.py", 'rb') as f:
#     content = f.read()
# attach_file = MIMEApplication(content, Name="obfuscated_p21x.py")
# msg.attach(attach_file)

# smtp=smtplib.SMTP('smtp.gmail.com', 587)
# smtp.ehlo()
# smtp.starttls()
# smtp.login('5b1g0028@stust.edu.tw','@Dz8w5uT')
# status=smtp.send_message(msg)
# if status=={}:
#     print("郵件傳送成功!")
# else:
#     print("郵件傳送失敗!")
# smtp.quit()