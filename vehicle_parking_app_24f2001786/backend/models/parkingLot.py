from models import db, parking_spot_get_model
from datetime import datetime, timezone
from flask_restx import fields
from .parkingSpot import SpotStatus

class ParkingLot(db.Model):
    __tablename__ = "parking_lots"
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(20), nullable=False, index=True)
    city = db.Column(db.String(50), nullable=False, index=True)
    state = db.Column(db.String(50), nullable=False, index=True)
    district = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    floor_level = db.Column(db.String(10),default='Ground')
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    open_time = db.Column(db.Time)
    close_time = db.Column(db.Time)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
       db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    parking_spots = db.relationship(
        "ParkingSpot",
        back_populates="parking_lot",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def available_spots_count(self):
        return self.parking_spots.filter_by(status=SpotStatus.AVAILABLE).count()

    @property
    def occupied_spots(self):
        return self.parking_spots.filter_by(status=SpotStatus.OCCUPIED).count()

    def total_spots_info(self):
        return f"Occupied: {self.occupied_spots}/{self.maximum_number_of_spots}"

    def __repr__(self):
        return f"<ParkingLot {self.prime_location_name}>"


def parking_lot_get_model(ns):
    return ns.model("ParkingLotGet", {
        "id": fields.Integer(required=True, description="ID"),
        "prime_location_name": fields.String(required=True, description="Prime Location Name"),
        "pin_code": fields.String(required=True, description="Pin Code"),
        "city": fields.String(required=True, description="City"),
        "state": fields.String(required=True, description="State"),
        "district": fields.String(required=True, description="District"),
        "address": fields.String(required=True, description="Address"),
        "price_per_hour": fields.Float(required=True, description="Price Per Hour"),
        "floor_level": fields.String(description="Floor Level"),
        "maximum_number_of_spots": fields.Integer(required=True, description="Maximum Number of Spots"),
        "open_time": fields.String(description="Open Time"),
        "close_time": fields.String(description="Close Time"),
        "is_active": fields.Boolean(description="Is Active"),
        "revenue": fields.Float(description="Revenue"),
        "occupied_spots": fields.Integer(description="Occupied Spot"),
        "parking_spots": fields.List(fields.Nested(parking_spot_get_model(ns)), description="Parking Spots"),
    })

def parking_lot_post_model(ns):
    return ns.model("ParkingLotPost", {
        "prime_location_name": fields.String(required=True, description="Prime Location Name"),
        "pin_code": fields.String(required=True, description="Pin Code"),
        "city": fields.String(required=True, description="City"),
        "state": fields.String(required=True, description="State"),
        "district": fields.String(required=True, description="District"),
        "price_per_hour": fields.Float(required=True, description="Price Per Hour"),
        "floor_level": fields.String(description="Floor Level"),
        "maximum_number_of_spots": fields.Integer(required=True, description="Maximum Number of Spots"),
        "open_time": fields.String(description="Open Time"),
        "close_time": fields.String(description="Close Time"),
    })

def parking_lot_put_model(ns):
    return  ns.model('ParkingLotUpdate', {
    'price_per_hour': fields.Float(required=False),
    'maximum_number_of_spots': fields.Integer(required=False),
    'open_time': fields.String(required=False),
    'close_time': fields.String(required=False),
})