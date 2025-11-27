import csv
import smtplib
from email.message import EmailMessage
from typing import Dict, Any, List
import os

class ErrorHandler:
    def __init__(self, output_path: str, fieldnames: List[str]):
        self.output_path = output_path
        self.fieldnames = fieldnames + ['errors']
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.file = open(self.output_path, 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def handle(self, record: Dict[str, Any], errors: List[str]):
        record['errors'] = '; '.join(errors)
        self.writer.writerow(record)

    def close(self):
        self.file.close()

class SuccessHandler:
    def __init__(self, output_path: str, fieldnames: List[str]):
        self.output_path = output_path
        self.fieldnames = fieldnames
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.file = open(self.output_path, 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=self.fieldnames)
        self.writer.writeheader()

    def handle(self, record: Dict[str, Any]):
        self.writer.writerow(record)

    def close(self):
        self.file.close()

class EmailNotifier:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def send_error_notification(self, error_file_path: str, error_count: int):
        msg = EmailMessage()
        msg['Subject'] = f"ETL Validation Errors - {error_count} records failed"
        msg['From'] = self.config.get('sender')
        msg['To'] = ', '.join(self.config.get('recipients', []))
        msg.set_content(f"Validation completed. {error_count} records failed validation. See attached error file.")

        with open(error_file_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(error_file_path)
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

        # Mock sending email for now as we don't have a real SMTP server
        print(f"Mocking email send to {msg['To']} with subject '{msg['Subject']}'")
        # with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
        #     server.send_message(msg)

class DBLoader:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def load(self, file_path: str):
        # Placeholder for DB loading logic
        print(f"Mocking DB load from {file_path} to {self.connection_string}")
