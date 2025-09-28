from models import db, parking_spot_get_model, EnumField, display_user_model
from datetime import datetime,timezone
import enum
from flask_restx import fields


class ReservationStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"


class ReservedParkingSpot(db.Model):
    __tablename__ = "reserved_parking_spots"
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(
        db.Integer,
        db.ForeignKey("parking_spots.id", ondelete="Set NULL"),
        nullable=True, index=True
    )
    user_id = db.Column(
        db.String(50), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vehicle_number = db.Column(
        db.String(20), db.ForeignKey("vehicles.vehicle_number", ondelete="CASCADE")
    )
    location = db.Column(db.String(100), nullable=False)
    parking_timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost_per_hour = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(ReservationStatus), default=ReservationStatus.ACTIVE)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    user = db.relationship("User", back_populates="reservations")
    parking_spot = db.relationship("ParkingSpot", back_populates="reservations")
    vehicle = db.relationship("Vehicle", back_populates="reservations", uselist=False)
    payment = db.relationship("Payment", back_populates="reservation", uselist=False)

    def __repr__(self):
        return f"<Reservation ID={self.id} Spot={self.spot_id} User={self.user_id}>"
    


def reservation_post_model(ns):
    return ns.model('ReservationPost', {
        'spot_id': fields.Integer(required=True, description='Parking Spot ID'),
        'user_id': fields.String(required=True, description='User ID'),
        'parking_cost_per_hour': fields.Float(required=True, description='Parking Cost Per Hour'),
        'vehicle_number': fields.String(required=True, description='Vehicle Number'),
    })

def reservation_get_model(ns):
    return ns.inherit('ReservationGet', {
        'id' : fields.Integer(required=True, description='Reservation ID'),
        'location' : fields.String(requied=True, description='Location'),
        'parking_cost_per_hour': fields.Float(required=True, description='Parking Cost Per Hour'),
        'vehicle_number': fields.String(required=True, description='Vehicle Number'),
        'parking_timestamp': fields.DateTime(required=True, description='Parking Timestamp'),
        'leaving_timestamp': fields.DateTime(required=True, description='Leaving Timestamp'),
        'status' : EnumField(required=True, description='Status'),
        'user': fields.Nested(display_user_model(ns)),
        'parking_spot': fields.Nested(parking_spot_get_model(ns)),
    })

def reservation_put_model(ns):
    return ns.model('ReservationPut', {
        'leaving_timestamp': fields.DateTime(required=True, description='Leaving Timestamp'),
    })