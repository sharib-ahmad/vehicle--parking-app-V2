import io
import csv
from datetime import datetime, timedelta, timezone
from celery import shared_task
from models import db, User, ReservedParkingSpot, ParkingLot, Payment, UserRole
from mail import send_email
from jinja2 import Template
from collections import Counter
from tasks import logger

# --- Helper Functions ---
def get_last_month_dates():
    """Calculates the start and end dates for the previous month."""
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)
    return first_day_of_last_month, last_day_of_last_month


@shared_task(ignore_results = False ,name="tasks.send_monthly_report")
def send_monthly_report():
    """
    Generates and sends a monthly activity report to all users.
    This task is scheduled to run on the first day of every month.
    """
    logger.info("Executing monthly report task...")
    try:
        users = User.query.filter(User.role != UserRole.ADMIN).all()
        start_date, end_date = get_last_month_dates()
        month_name = start_date.strftime("%B %Y")

        for user in users:
            reservations = ReservedParkingSpot.query.filter(
                ReservedParkingSpot.user_id == user.id,
                ReservedParkingSpot.parking_timestamp.between(start_date, end_date)
            ).all()

            if not reservations:
                continue  # Skip users with no reservations in the last month

            total_reservations = len(reservations)
            total_spent = sum(res.parking_cost_per_hour for res in reservations if res.parking_cost_per_hour is not None)

            # Find the most used parking lot
            lot_ids = [res.parking_spot.lot_id for res in reservations if res.parking_spot]
            if lot_ids:
                most_common_lot_id = Counter(lot_ids).most_common(1)[0][0]
                most_used_lot = ParkingLot.query.get(most_common_lot_id)
                most_used_lot_name = most_used_lot.prime_location_name if most_used_lot else "N/A"
            else:
                most_used_lot_name = "N/A"

            # Create HTML report from a template string
            html_template = """
            <html>
            <body>
                <h2>Your Monthly Parking Report for {{ month_name }}</h2>
                <p>Hi {{ username }}, here's your activity summary:</p>
                <ul>
                    <li><strong>Total Bookings:</strong> {{ total_bookings }}</li>
                    <li><strong>Total Amount Spent:</strong> ${{ "%.2f"|format(total_spent) }}</li>
                    <li><strong>Most Used Parking Lot:</strong> {{ most_used_lot_name }}</li>
                </ul>
                <p>Thank you for using our service!</p>
            </body>
            </html>
            """
            template = Template(html_template)
            report_html = template.render(
                username=user.username,
                month_name=month_name,
                total_bookings=total_reservations,
                total_spent=total_spent,
                most_used_lot_name=most_used_lot_name
            )

            subject = f"Your Parking Report for {month_name}"
            send_email(user.email, subject, report_html)

        logger.info("Monthly reports sent successfully.")
        return "Monthly reports completed."
    except Exception as e:
        logger.error(f"Error in send_monthly_report task: {e}")
        return "An error occurred."


# --- User-Triggered Async Task ---

@shared_task(ignore_results=False, name="tasks.export_user_parking_data_to_csv")
def export_user_parking_data_to_csv(user_id):
    """
    Exports user parking data to a CSV in memory and emails it as an attachment.
    This avoids creating and deleting temporary files, preventing race conditions.
    """
    logger.info(f"Starting CSV export for user_id: {user_id}")
    try:
        user = User.query.get(user_id)
        
        if not user:
            logger.warning(f"User with id {user_id} not found.")
            return "User not found."

        reservations = ReservedParkingSpot.query.filter_by(user_id=user.id).order_by(ReservedParkingSpot.parking_timestamp.desc()).all()

        if not reservations:
            subject = "Your Parking Data Export"
            message = f"Hi {user.username},\n\nYou requested an export of your parking data, but you have no reservations to export."
            send_email(user.email, subject, message, content="plain")
            logger.info(f"No reservations found for user {user.id}. Email sent.")
            return "No reservations to export."

        # --- Generate CSV in memory ---
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Updated headers to match the new requirements
        headers = ['slot_id', 'spot_id', 'parking_timestamp', 'leaving_timestamp', 'cost', 'remarks']
        writer.writerow(headers)

        for res in reservations:
            writer.writerow([
                res.parking_spot.lot_id if res.parking_spot else 'N/A',
                res.parking_spot.spot_number if res.parking_spot else 'N/A',
                res.parking_timestamp.isoformat() if res.parking_timestamp else '',
                res.leaving_timestamp.isoformat() if res.leaving_timestamp else '',
                res.payment.amount if res.payment else 0.0,
                '' # Remarks column - currently empty as it's not in the model
            ])
        
        csv_data = output.getvalue()
        output.close()
        
        # Define the filename for the attachment
        filename = f"parking_export_{user.uuid}_{datetime.now().strftime('%Y%m%d')}.csv"

        # --- Send email with the CSV data as an attachment ---
        subject = "Your Parking Data Export is Ready"
        message = f"Hi {user.username},\n\nPlease find your parking history attached."
        
        send_email(
            user.email,
            subject,
            message,
            content="plain",
            attachment_data=csv_data,
            attachment_filename=filename
        )
        
        logger.info(f"Successfully exported and sent data for user {user.username}.")
        return f"CSV export successful for user {user.id}."
    except Exception as e:
        logger.error(f"Error in export_user_parking_data_to_csv task: {e}", exc_info=True)
        return "An error occurred during export."