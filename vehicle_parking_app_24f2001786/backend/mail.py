import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from config import LocalDevelopmentConfig

# Load configuration
config = LocalDevelopmentConfig()

# Configure logger
logger = logging.getLogger(__name__)

def send_email(to_address, subject, message, content="html", attachment_file=None, attachment_data=None, attachment_filename=None):
    """
    Sends an email using SMTP configuration.
    It can handle file-based attachments (attachment_file) and
    in-memory data attachments (attachment_data), automatically
    handling whether the data is a string or bytes.
    """
    msg = MIMEMultipart()
    msg["From"] = config.SENDER_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject

    # Attach the main body of the email
    msg.attach(MIMEText(message, content))

    # --- Handle In-Memory Attachments (like PDF or CSV data) ---
    if attachment_data and attachment_filename:
        part = MIMEBase("application", "octet-stream")
        
        # Check if the data is a string (e.g., from a CSV) or already bytes (e.g., from a PDF)
        if isinstance(attachment_data, str):
            # If it's a string, it must be encoded to bytes.
            part.set_payload(attachment_data.encode('utf-8'))
        else:
            # If it's already bytes, it can be used directly.
            part.set_payload(attachment_data)
            
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={attachment_filename}")
        msg.attach(part)
    
    # --- Handle File-Path Based Attachments ---
    elif attachment_file:
        try:
            with open(attachment_file, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_file)}")
            msg.attach(part)
        except FileNotFoundError:
            print(f"❌ Attachment file not found: {attachment_file}")
            # Decide if you want to send the email anyway or return False
            # return False 

    try:
        with smtplib.SMTP(host=config.SMTP_SERVER_HOST, port=config.SMTP_SERVER_PORT) as s:
            # For MailHog, login isn’t required
            if config.SMTP_USERNAME and config.SENDER_PASSWORD:
                s.login(config.SMTP_USERNAME, config.SENDER_PASSWORD)
            s.send_message(msg)
            print(f"✅ Email sent to {to_address}")
            return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_address}: {e}")
        return False

