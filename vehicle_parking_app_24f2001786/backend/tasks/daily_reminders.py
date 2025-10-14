from datetime import datetime, timedelta, timezone
from celery import shared_task
from models import db, User, ParkingLot, ReservedParkingSpot, UserRole
from mail import send_email
from jinja2 import Template
from tasks import logger

@shared_task(ignore_results = False ,name="tasks.send_daily_reminders")
def send_daily_reminders():
    """
    Sends daily reminders based on user activity and new parking lots.

    - If a new parking lot was created in the last 24 hours, a notification
      is sent to ALL users about the new lot.
    - If there are no new lots, a reminder is sent only to users who have not
      booked a parking spot in the last 3 days.

    This task is scheduled to run daily. The exact time can be configured in
    the Celery Beat schedule, allowing users to choose their preferred time.
    """
    logger.info("Executing daily reminder task...")
    try:
        # --- Check for new parking lots created in the last 24 hours ---
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        new_lots = ParkingLot.query.filter(ParkingLot.created_at >= one_day_ago).all()

        users_to_notify = []
        subject = ""
        html_template_str = ""

        if new_lots:
            # --- Condition 1: New parking lot(s) created ---
            # Notify ALL non-admin users about the new options.
            users_to_notify = User.query.filter(User.role != UserRole.ADMIN).all()
            subject = "New Parking Lots Available!"
            
            html_template_str = """
            <html>
            <body style="font-family: sans-serif;">
                <h3>Check out our new parking lots!</h3>
                <p>Hi {{ username }},</p>
                <p>We've added new parking locations for your convenience:</p>
                <ul>
                {% for lot in new_lots %}
                    <li><strong>{{ lot.prime_location_name }}</strong> (Capacity: {{ lot.capacity }})</li>
                {% endfor %}
                </ul>
                <p>Need a place to park soon? <a href="http://localhost:5173/user/dashboard">Book a Spot Now</a></p>
            </body>
            </html>
            """
        else:
            # --- Condition 2: No new lots, check for inactive users ---
            # Find users who haven't made a reservation in the last 3 days.
            three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
            
            # Subquery to find IDs of users who have been active recently
            active_user_ids_query = db.session.query(ReservedParkingSpot.user_id).filter(
                ReservedParkingSpot.parking_timestamp >= three_days_ago
            ).distinct()
            
            # Find users whose IDs are NOT in the active list
            users_to_notify = User.query.filter(
                User.role != UserRole.ADMIN,
                ~User.id.in_(active_user_ids_query)
            ).all()

            subject = "We Miss You! Need a Parking Spot?"
            
            html_template_str = """
            <html>
            <body style="font-family: sans-serif;">
                <h3>Need a Parking Spot?</h3>
                <p>Hi {{ username }},</p>
                <p>We've noticed you haven't booked a parking spot with us recently. If you need a place to park, we're here to help!</p>
                <p><a href="http://localhost:5173/user/dashboard">Book a Spot Now</a></p>
            </body>
            </html>
            """
        
        if not users_to_notify:
            logger.info("No users to notify today.")
            return "No reminders sent."

        # --- Send the appropriate email to the selected users ---
        template = Template(html_template_str)
        for user in users_to_notify:
            html_content = template.render(
                username=user.username, 
                new_lots=new_lots  # Pass new_lots data for the template
            )
            # Assuming send_email is configured to handle HTML content
            send_email(user.email, subject, html_content)
            logger.info(f"Sent notification to {user.email}")

        logger.info(f"Daily reminder task completed. Messages sent to {len(users_to_notify)} users.")
        return f"Task completed. Messages sent to {len(users_to_notify)} users."

    except Exception as e:
        logger.error(f"Error in send_daily_reminders task: {e}")
        return "An error occurred."