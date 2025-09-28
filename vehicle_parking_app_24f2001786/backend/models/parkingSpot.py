from models import db, EnumField
from datetime import datetime, timezone
from flask_restx import fields
import enum

class SpotStatus(enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"



class ParkingSpot(db.Model):
    __tablename__ = "parking_spots"
    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(20), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lots.id"), nullable=False)
    status = db.Column(
        db.Enum(SpotStatus), default=SpotStatus.AVAILABLE, nullable=False
    )
    revenue = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    parking_lot = db.relationship("ParkingLot", back_populates="parking_spots")
    reservations = db.relationship(
        "ReservedParkingSpot",
        back_populates="parking_spot",
        lazy="dynamic",
        cascade="save-update",
    )

    def __repr__(self):
        return f"<ParkingSpot {self.spot_number} in Lot {self.lot_id}>"
    

def parking_spot_get_model(ns):
    return ns.model("ParkingSpot", {
        "id": fields.Integer(required=True, description="Spot ID"),
        "spot_number": fields.String(required=True, description="Spot Number"),
        "lot_id": fields.Integer(required=True, description="Parking Lot ID"),
        "status": EnumField(required=True, description="Status"),
    })