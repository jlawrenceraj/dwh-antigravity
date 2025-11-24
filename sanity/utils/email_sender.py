import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os

def send_email_with_screenshots(subject, body, screenshot_paths, config):
    sender_email = config['email']['sender_email']
    sender_password = config['email']['sender_password']
    recipient_email = config['email']['recipient_email']
    smtp_server = config['email']['smtp_server']
    smtp_port = config['email']['smtp_port']

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    msg.attach(MIMEText(body, 'plain'))

    for path in screenshot_paths:
        if os.path.exists(path):
            with open(path, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data, name=os.path.basename(path))
                msg.attach(image)
        else:
            print(f"Warning: Screenshot not found at {path}")

    try:
        # Note: This is a basic implementation. For production, consider handling different security protocols (SSL/TLS).
        # Using starttls for port 587 usually.
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Optional: Enable debugging to see SMTP interaction
            # server.set_debuglevel(1)
            
            if config['email'].get('use_tls', False):
                server.starttls()
            
            if sender_password:
                server.login(sender_email, sender_password)
            
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
