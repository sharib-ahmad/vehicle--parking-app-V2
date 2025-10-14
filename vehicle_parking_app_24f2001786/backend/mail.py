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
    Send an email using SMTP, with support for file-based or in-memory attachments.

    Args:
        to_address (str): Recipient's email address.
        subject (str): Email subject.
        message (str): The HTML or plain text body of the email.
        content (str): Type of content, either "html" or "plain".
        attachment_file (str, optional): The file path of the attachment. Defaults to None.
        attachment_data (str, optional): The raw string or byte data for an in-memory attachment. Defaults to None.
        attachment_filename (str, optional): The desired filename for the in-memory attachment. Required if attachment_data is used.
    """

    msg = MIMEMultipart()
    msg["From"] = config.SENDER_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject

    # Attach email content
    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    part = None
    filename = None

    # Handle attachments
    if attachment_data and attachment_filename:
        # --- Handle in-memory attachment ---
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment_data.encode('utf-8')) # Encode string data to bytes
        encoders.encode_base64(part)
        filename = attachment_filename
    elif attachment_file:
        # --- Handle file-based attachment ---
        with open(attachment_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        filename = os.path.basename(attachment_file)
    
    if part and filename:
        part.add_header(
            "Content-Disposition", f"attachment; filename={filename}"
        )
        msg.attach(part)

    try:
        with smtplib.SMTP(host=config.SMTP_SERVER_HOST, port=config.SMTP_SERVER_PORT) as s:
            s.login(config.SENDER_ADDRESS, config.SENDER_PASSWORD)
            s.send_message(msg)
            logger.info(f"✅ Email sent to {to_address}")
            return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

