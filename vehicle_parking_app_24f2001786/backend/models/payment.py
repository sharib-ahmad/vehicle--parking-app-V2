from models import db
from datetime import datetime, timezone
import enum
from flask_restx import fields


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(
        db.Integer,
        db.ForeignKey("reserved_parking_spots.id", ondelete="CASCADE"),
        nullable=False,
    )
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    reservation = db.relationship("ReservedParkingSpot", back_populates="payment")

    def __repr__(self):
        return f"<Payment ID={self.id} Reservation={self.reservation_id}>"
    


def payment_post_model(ns):
    return ns.model('PaymentPost', {
        'reservation_id': fields.Integer(required=True, description='Reservation ID'),
        'amount': fields.Float(required=True, description='Amount'),
        'payment_method': fields.String(required=True, description='Payment Method'),
    })  