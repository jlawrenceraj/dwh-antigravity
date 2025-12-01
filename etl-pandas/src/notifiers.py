import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import logging

class EmailNotifier:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def send_error_report(self, error_file_path: str, recipient: str):
        if not self.config.get('features', {}).get('enable_email', False):
            self.logger.info("Email notification is disabled via feature flag.")
            return

        email_config = self.config.get('email', {})
        sender_email = email_config.get('sender_email')
        smtp_server = email_config.get('smtp_server')
        smtp_port = email_config.get('smtp_port')
        password = email_config.get('password')

        if not all([sender_email, smtp_server, smtp_port]):
            self.logger.error("Missing email configuration.")
            return

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = f"ETL Error Report: {os.path.basename(error_file_path)}"

        body = "Please find attached the error records from the recent ETL run."
        msg.attach(MIMEText(body, 'plain'))

        # Attachment
        if os.path.exists(error_file_path):
            with open(error_file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(error_file_path)}",
            )
            msg.attach(part)
        else:
            self.logger.warning(f"Error file not found: {error_file_path}")
            return

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            if password:
                server.login(sender_email, password)
            server.send_message(msg)
            server.quit()
            self.logger.info(f"Error report sent to {recipient}")
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
