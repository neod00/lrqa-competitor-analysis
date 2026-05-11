import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yaml
from dotenv import load_dotenv


class EmailSender:
    def __init__(self):
        load_dotenv()
        self.gmail_user = os.getenv("GMAIL_ADDRESS")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        self.recipients = [email.strip() for email in os.getenv("EMAIL_RECIPIENTS", "").split(",") if email.strip()]

        with open("config.yaml", "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["email"]

    def send_report(self, subject, html_content):
        if not self.gmail_user or not self.gmail_password:
            print("이메일 환경 변수가 설정되지 않았습니다.")
            return False

        if not self.recipients:
            print("이메일 수신자가 설정되지 않았습니다.")
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{self.config['subject_prefix']} {subject}"
        msg["From"] = self.gmail_user
        msg["To"] = ", ".join(self.recipients)

        part = MIMEText(html_content, "html", "utf-8")
        msg.attach(part)

        try:
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            if self.config.get("use_tls", True):
                server.starttls()
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            print(f"이메일 발송 성공: {', '.join(self.recipients)}")
            return True
        except Exception as e:
            print(f"이메일 발송 실패: {e}")
            return False
