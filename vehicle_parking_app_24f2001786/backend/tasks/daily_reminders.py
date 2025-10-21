import os
import requests
from datetime import datetime, timedelta, timezone
from celery import shared_task
from models import db, User, ParkingLot, ReservedParkingSpot, UserRole
from tasks import logger

def send_google_chat_notification(message):
    """Sends a message to a Google Chat webhook."""
    webhook_url = os.getenv("GOOGLE_CHAT_WEBHOOK")
    if not webhook_url:
        logger.error("GOOGLE_CHAT_WEBHOOK environment variable not set.")
        return

    try:
        # Google Chat API expects a 'text' key in the JSON payload
        payload = {'text': message}
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()  # Will raise an exception for HTTP error codes
        logger.info("Successfully sent notification to Google Chat.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Google Chat notification: {e}")


@shared_task(ignore_results=False, name="tasks.send_daily_reminders")
def send_daily_reminders():
    """
    Sends daily reminders to a Google Chat channel. It checks for two conditions
    independently: new parking lots and inactive users.
    """
    logger.info("Executing daily reminder task for Google Chat...")
    try:
        notifications_sent = False

        # --- Part 1: Check for new parking lots created in the last 24 hours ---
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        new_lots = ParkingLot.query.filter(ParkingLot.created_at >= one_day_ago).all()

        if new_lots:
            lot_details = "\n".join([f"- *{lot.prime_location_name}* (Capacity: {lot.maximum_number_of_spots})" for lot in new_lots])
            message = (
                "<users/all> *New Parking Lots Available!*\n\n"
                "Heads up! We've added new parking locations:\n"
                f"{lot_details}\n\n"
                "Book a spot if you need one!"
            )
            send_google_chat_notification(message)
            notifications_sent = True

        # --- Part 2: Check for inactive users (who haven't booked in 3 days) ---
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
        active_user_ids_query = db.session.query(ReservedParkingSpot.user_id).filter(
            ReservedParkingSpot.parking_timestamp >= three_days_ago
        ).distinct()
        
        inactive_users = User.query.filter(
            User.role != UserRole.ADMIN,
            ~User.id.in_(active_user_ids_query)
        ).all()

        if inactive_users:
            inactive_user_names = ", ".join([user.username for user in inactive_users])
            message = (
                f"<users/all> *Friendly Reminder*\n\n"
                f"Just a friendly nudge for: *{inactive_user_names}*.\n"
                f"We've noticed you haven't booked a parking spot with us recently. "
                f"If you need a place to park, we're here to help!"
            )
            send_google_chat_notification(message)
            notifications_sent = True

        # --- Final Logging ---
        if not notifications_sent:
            logger.info("No new lots or inactive users to notify about today.")
            return "No reminders sent."
        
        logger.info("Daily reminder task for Google Chat completed.")
        return "Task completed. Notifications sent to Google Chat."

    except Exception as e:
        logger.error(f"Error in send_daily_reminders task: {e}", exc_info=True)
        return "An error occurred."

