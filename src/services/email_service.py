import os, smtplib, json
import jinja2

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from utils.resource import internalPath

from dotenv import load_dotenv

load_dotenv()

def send_mail(email_data): 
        
    with open(internalPath('data/recipients.json'), 'r',encoding='utf-8') as file:
        people_data = json.load(file)

    file_path_list = [{"name": "payload.json", "path": "payload.json"}]  

    with open(internalPath('ui/email_chamados.html'), "r", encoding='utf-8') as file:
        template_str = file.read()

    jinja_template = jinja2.Template(template_str)

    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    for person in people_data:
        email_content = jinja_template.render(email_data)

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = person["email"]
        msg["Subject"] = email_data["subject"]
        msg.attach(MIMEText(email_content, "html"))

        for file_info in file_path_list:
            with open(file_info['path'], 'rb') as file:
                msg.attach(MIMEApplication(file.read(), Name=file_info['name']))

        # print(f"Sending email to {person['email']}")
        server.sendmail(sender_email, person["email"], msg.as_string())

    server.quit()

