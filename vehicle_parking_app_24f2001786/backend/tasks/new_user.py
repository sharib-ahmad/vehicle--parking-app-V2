from celery import shared_task
from tasks import logger
from models import User
from mail import send_email
from jinja2 import Template



@shared_task(ignore_results=False, name="tasks.send_welcome_email")
def send_welcome_email(email):
    """Sends a welcome email to a new user."""
    logger.info(f"Sending welcome email to email: {email}")
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            logger.warning(f"User with id {email} not found for welcome email.")
            return "User not found."

        subject = "Welcome to Our Parking App!"
        
        html_template_str = """
        <html>
        <body style="font-family: sans-serif;">
            <h3>Welcome, {{ full_name }}!</h3>
            <p>Thank you for joining our platform. We're excited to help you find the best parking spots with ease.</p>
            <p>You can start by searching for parking lots or booking a spot right away.</p>
            <p>Best regards,<br>The Parking Team</p>
        </body>
        </html>
        """
        template = Template(html_template_str)
        html_content = template.render(full_name=user.full_name)

        send_email(user.email, subject, html_content)
        logger.info(f"Welcome email sent successfully to {user.email}")
        return f"Welcome email sent to {user.email}"

    except Exception as e:
        logger.error(f"Error in send_welcome_email task: {e}", exc_info=True)
        return "An error occurred while sending the welcome email."