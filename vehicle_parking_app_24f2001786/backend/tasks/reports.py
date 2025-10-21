import io
import csv
from datetime import datetime, timedelta, timezone
from celery import shared_task
from models import db, User, ReservedParkingSpot, ParkingLot, Payment, UserRole
from mail import send_email
from jinja2 import Template
from collections import Counter
from tasks import logger
from weasyprint import HTML

# --- Helper Functions ---
def get_last_month_dates():
    """Calculates the start and end dates for the previous month."""
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)
    return first_day_of_last_month, last_day_of_last_month


@shared_task(ignore_results=False, name="tasks.send_monthly_report")
def send_monthly_report():
    """
    Generates and sends a monthly activity report with an attached PDF to all users.
    The report includes enhanced insights like peak usage days and average duration.
    """
    if HTML is None:
        logger.error("WeasyPrint is not installed. PDF reports cannot be generated.")
        return "Error: WeasyPrint is not installed."

    logger.info("Executing monthly report task with PDF attachment...")
    try:
        users = User.query.filter(User.role != UserRole.ADMIN).all() 
        start_date, end_date = get_last_month_dates()
        # end_date = datetime.utcnow()
        # start_date = end_date - timedelta(days=30)
        month_name = start_date.strftime("%B %Y")

        logger.info(f"Found {len(users)} user(s) to process for the period: {start_date.date()} to {end_date.date()}.")

        if not users:
            logger.info("No users found to send reports to.")
            return "No users in the system."

        reports_sent_count = 0
        for user in users:
            reservations = ReservedParkingSpot.query.filter(
                ReservedParkingSpot.user_id == user.id,
                ReservedParkingSpot.parking_timestamp.between(start_date, end_date)
            ).all()

            logger.info(f"Processing user '{user.username}': Found {len(reservations)} reservations for the period.")

            if not reservations:
                continue  # Skip users with no activity

            # --- Enhanced Insights ---
            total_reservations = len(reservations)
            total_spent = sum(res.parking_cost_per_hour for res in reservations if res.parking_cost_per_hour)

            # Most used parking lot
            lot_ids = [res.parking_spot.lot_id for res in reservations if res.parking_spot]
            most_used_lot_name = "N/A"
            if lot_ids:
                most_common_lot_id = Counter(lot_ids).most_common(1)[0][0]
                most_used_lot = ParkingLot.query.get(most_common_lot_id)
                most_used_lot_name = most_used_lot.prime_location_name if most_used_lot else "N/A"

            # Peak usage day of the week
            peak_day_counter = Counter(res.parking_timestamp.strftime('%A') for res in reservations)
            peak_day = peak_day_counter.most_common(1)[0][0] if peak_day_counter else "N/A"
            
            # Average parking duration
            total_duration_hours = 0
            completed_reservations = 0
            for res in reservations:
                if res.leaving_timestamp and res.parking_timestamp:
                    duration = res.leaving_timestamp - res.parking_timestamp
                    total_duration_hours += duration.total_seconds() / 3600
                    completed_reservations += 1
            
            avg_duration_hours = (total_duration_hours / completed_reservations) if completed_reservations > 0 else 0
            avg_duration_formatted = f"{avg_duration_hours:.1f} hours"


            # --- Create HTML for both email body and PDF ---
            html_template = """
            <html>
            <head>
                <style>
                    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; }
                    .container { padding: 20px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0,0,0,0.05); }
                    h2 { color: #0056b3; }
                    ul { list-style-type: none; padding: 0; }
                    li { margin-bottom: 10px; }
                    strong { color: #0056b3; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Your Monthly Parking Report: {{ month_name }}</h2>
                    <p>Hi {{ username }}, here are your parking insights for the past month:</p>
                    <h3>Summary</h3>
                    <ul>
                        <li><strong>Total Bookings:</strong> {{ total_bookings }}</li>
                        <li><strong>Total Spent:</strong> ${{ "%.2f"|format(total_spent) }}</li>
                        <li><strong>Favorite Parking Lot:</strong> {{ most_used_lot_name }}</li>
                    </ul>
                    <h3>Usage Patterns</h3>
                    <ul>
                        <li><strong>Busiest Day:</strong> You parked most often on <strong>{{ peak_day }}s</strong>.</li>
                        <li><strong>Average Stay:</strong> Your average parking duration was about <strong>{{ avg_duration }}</strong>.</li>
                    </ul>
                    <p>Thank you for using our service! Your detailed report is attached as a PDF.</p>
                </div>
            </body>
            </html>
            """
            template = Template(html_template)
            report_html = template.render(
                username=user.username,
                month_name=month_name,
                total_bookings=total_reservations,
                total_spent=total_spent,
                most_used_lot_name=most_used_lot_name,
                peak_day=peak_day,
                avg_duration=avg_duration_formatted
            )

            # --- Generate PDF in memory ---
            pdf_data = HTML(string=report_html).write_pdf()
            filename = f"Parking_Report_{month_name.replace(' ', '_')}.pdf"
            
            subject = f"Your Parking Report for {month_name}"
            
            # --- Send the email with the PDF attachment ---
            send_email(
                user.email,
                subject,
                report_html,  # The HTML report is the body of the email
                attachment_data=pdf_data,
                attachment_filename=filename
            )
            reports_sent_count += 1

        if reports_sent_count > 0:
            logger.info(f"Monthly reports with PDF attachments sent successfully to {reports_sent_count} user(s).")
            return f"Monthly reports completed. Sent {reports_sent_count} report(s)."
        else:
            logger.info("Monthly report task finished. No users had activity in the last month, so no reports were sent.")
            return "Task completed. No reports sent as there was no user activity."
            
    except Exception as e:
        logger.error(f"Error in send_monthly_report task: {e}", exc_info=True)
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