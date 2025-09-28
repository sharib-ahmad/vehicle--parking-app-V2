from models import db, display_user_model
from datetime import datetime, timezone
from flask_restx import fields

class Vehicle(db.Model):
    __tablename__ = "vehicles"
    vehicle_number = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(
        db.String(50), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    fuel_type = db.Column(db.String(10), nullable=False)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    color = db.Column(db.String(30))
    registration_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user = db.relationship("User", back_populates="vehicles")
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
       db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    reservations = db.relationship(
        "ReservedParkingSpot", back_populates="vehicle", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Vehicle {self.vehicle_number}>"

def vehicle_model(ns):
    return ns.model("Vehicle", {
        "vehicle_number": fields.String(required=True, description="Vehicle Number"),
        "fuel_type": fields.String(required=True, description="Fuel Type"),
        "brand": fields.String(description="Brand"),
        "model": fields.String(description="Model"),
        "color": fields.String(description="Color"),
        "user": fields.Nested(display_user_model(ns)),
    })