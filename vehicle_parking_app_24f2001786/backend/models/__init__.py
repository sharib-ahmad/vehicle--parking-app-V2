from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from flask_restx import fields
import enum

class EnumField(fields.Raw):
    def format(self, value):
        return value.value if isinstance(value, enum.Enum) else value


from .user import User, UserRole, user_register_model, user_login_model, display_user_model
from .userProfile import UserProfile
from .parkingSpot import ParkingSpot, parking_spot_get_model, SpotStatus
from .parkingLot import ParkingLot, parking_lot_get_model, parking_lot_post_model, parking_lot_put_model
from .reservation import ReservedParkingSpot, reservation_post_model, reservation_get_model, reservation_put_model, ReservationStatus
from .payment import Payment, payment_post_model, PaymentStatus
from .vehicle import Vehicle, vehicle_model
from .tokens import TokenBlocklist

def create_admin(app,email,password):
    with app.app_context():
        admin = User.query.filter_by(email=email).first()
        if not admin:
            try:
                admin = User(
                    email=email,
                    password=password,
                    role=UserRole.ADMIN,
                    full_name="Admin",
                    username="admin",
                    phone_number="1234567890",
                    address="Admin Address",
                    pincode="123456",
                )
                db.session.add(admin)
                db.session.commit(
                )
                print("Admin created successfully")
            except Exception as e:
                print(e)
                db.session.rollback()
            finally:
                db.session.close()
