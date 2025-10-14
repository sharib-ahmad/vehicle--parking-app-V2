from flask import request
from flask_restx import Resource, Namespace, abort, fields
from flask_jwt_extended import jwt_required, current_user
from models import (
    db,
    ParkingLot,parking_lot_get_model, parking_lot_put_model,
    ParkingSpot, SpotStatus, parking_lot_post_model,
    ReservedParkingSpot,reservation_get_model,ReservationStatus,
    User, Vehicle,display_user_model, vehicle_model,
    Payment, PaymentStatus
    )
from functools import wraps
from datetime import datetime
from werkzeug.exceptions import HTTPException
import uuid
from routes import cache # Import the cache object

# --- Setup ---
admin_ns = Namespace('admin', description='Admin related operations for managing parking lots')

# --- Decorators ---
def admin_required(f):
    """Decorator to ensure the user is an admin."""
    @wraps(f)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if not hasattr(current_user, 'role_value') or current_user.role_value != 'admin':
            abort(403, 'Forbidden: Administrator access required.')
        return f(*args, **kwargs)
    return wrapper

# --- Helper Functions ---
def parse_time(time_str: str):
    """
    Parses a time string from multiple possible formats (HH:MM:SS or HH:MM)
    into a Python time object.
    """
    if not time_str:
        return None
    for fmt in ("%H:%M:%S.%f", "%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    abort(400, f"Invalid time format for '{time_str}'. Please use HH:MM or HH:MM:SS format.")

# --- Models for Swagger Documentation ---
parking_lot_get_model = parking_lot_get_model(admin_ns)
parking_lot_post_model = parking_lot_post_model(admin_ns)
parking_lot_put_model = parking_lot_put_model(admin_ns)
reservation_get_model = reservation_get_model(admin_ns)
display_user_model = display_user_model(admin_ns)
vehicle_model = vehicle_model(admin_ns)

# New model for the payment summary
payment_summary_model = admin_ns.model('PaymentSummary', {
    'paid': fields.Integer(description='Total number of paid transactions'),
    'pending': fields.Integer(description='Total number of pending transactions')
})

# New model for the combined summary response
summary_response_model = admin_ns.model('SummaryResponse', {
    'lots': fields.List(fields.Nested(parking_lot_get_model)),
    'payment_summary': fields.Nested(payment_summary_model)
})


# --- Service Layer for Business Logic ---
class AdminServices:
    @staticmethod
    def get_all_lots():
        """Fetches all parking lots from the database."""
        return ParkingLot.query.order_by(ParkingLot.prime_location_name).all()

    @staticmethod
    def get_lot_by_id(lot_id):
        """Fetches a single parking lot by its ID."""
        return ParkingLot.query.get(lot_id)

    @staticmethod
    def create_lot(data):
        """Creates a new parking lot and its associated spots."""
        try:
            new_lot = ParkingLot(
                prime_location_name=data['prime_location_name'],
                city=data['city'],
                state=data['state'],
                pin_code=data['pin_code'],
                district=data['district'],
                address=f"{data['prime_location_name']}, {data['city']}, {data['district']}, {data['pin_code']}, {data['state']}",
                price_per_hour=data['price_per_hour'],
                floor_level=data.get('floor_level', 'Ground'),
                maximum_number_of_spots=data['maximum_number_of_spots'],
                open_time=parse_time(data.get('open_time')),
                close_time=parse_time(data.get('close_time')),
            )
            db.session.add(new_lot)
            db.session.flush()

            for i in range(1, new_lot.maximum_number_of_spots + 1):
                spot = ParkingSpot(spot_number=f"{new_lot.id}-{i}", lot_id=new_lot.id)
                db.session.add(spot)
            
            db.session.commit()
            cache.clear() # Clear cache after creating a lot
            return new_lot
        except HTTPException:
            raise
        except Exception as e:
            db.session.rollback()
            print(f"Error creating parking lot: {e}")
            abort(500, "An internal error occurred while creating the parking lot.")

    @staticmethod
    def update_lot(lot, data):
        """Updates an existing parking lot's editable fields and spot count."""
        try:
            current_spots = lot.maximum_number_of_spots
            new_spots = data['maximum_number_of_spots']
            
            occupied_count = lot.parking_spots.filter_by(status=SpotStatus.OCCUPIED).count()
            if new_spots < occupied_count:
                abort(400, f"Cannot reduce spots to {new_spots}. At least {occupied_count} spots are currently occupied.")

            if new_spots < current_spots:
                spots_to_delete = lot.parking_spots.filter_by(status=SpotStatus.AVAILABLE).order_by(ParkingSpot.id.desc()).limit(current_spots - new_spots)
                for spot in spots_to_delete:
                    db.session.delete(spot)
            elif new_spots > current_spots:
                ava_spot_num = [int(spot.spot_number.split('-')[1])
                                 for spot in lot.parking_spots]
               
                for i in range(1, new_spots + 1):
                    if i in ava_spot_num:
                        continue
                    
                    spot = ParkingSpot(spot_number=f"{lot.id}-{i}", lot_id=lot.id)
                    db.session.add(spot)
            
            lot.price_per_hour = data['price_per_hour']
            lot.maximum_number_of_spots = new_spots
            lot.open_time = parse_time(data.get('open_time'))
            lot.close_time = parse_time(data.get('close_time'))
            
            db.session.commit()
            cache.clear() # Clear cache after updating a lot
            return lot
        except HTTPException:
            raise
        except Exception as e:
            db.session.rollback()
            print(f"Error updating parking lot {lot.id}: {e}")
            abort(500, "An internal error occurred while updating the parking lot.")

    @staticmethod
    def delete_lot(lot):
        """Deletes a parking lot if it has no occupied spots."""
        occupied_count = lot.parking_spots.filter_by(status=SpotStatus.OCCUPIED).count()
        if occupied_count > 0:
            abort(400, f"Cannot delete lot. It has {occupied_count} occupied spot(s).")
        
        try:
            db.session.delete(lot)
            db.session.commit()
            cache.clear() # Clear cache after deleting a lot
        except HTTPException:
            raise
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting parking lot {lot.id}: {e}")
            abort(500, "An internal error occurred while deleting the parking lot.")

    @staticmethod
    def reservation_info(spot_id):
        """Fetch reservation by spot_id"""
        return ReservedParkingSpot.query.filter_by(spot_id=spot_id,status=ReservationStatus.ACTIVE).first()
    
    @staticmethod
    def delete_spot(spot_id):
        """Delete spot by spot_id"""
        try:
            spot = ParkingSpot.query.filter_by(id=spot_id).first()
            spot.parking_lot.maximum_number_of_spots -= 1
            db.session.delete(spot)
            db.session.commit()
            cache.clear() # Clear cache after deleting a spot
        except HTTPException:
            raise
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting spot {spot_id}: {e}")
            abort(500, "An internal error occurred while deleting the spot.")

    @staticmethod
    def search(search_type, params):
        """Performs a search based on type and parameters."""
        if not params:
            abort(400, "Search parameters are required.")
        
        param_key = list(params.keys())[0]
        query_val = params[param_key]

        if search_type == 'lot':
            if param_key == 'location':
                return ParkingLot.query.filter(ParkingLot.prime_location_name.ilike(f'%{query_val}%')).all()
            elif param_key == 'pincode':
                return ParkingLot.query.filter_by(pin_code=query_val).all()
        
        elif search_type == 'user':
            if param_key == 'user_id' or param_key == 'username':
                return User.query.filter(User.username.ilike(f'%{query_val}%')).all()
            elif param_key == 'phone':
                return User.query.filter_by(phone_number=query_val).all()
            elif param_key == 'pincode':
                return User.query.filter_by(pincode=query_val).all()

        elif search_type == 'vehicle':
            if param_key == 'vehicle_number':
                vehicle = Vehicle.query.filter(Vehicle.vehicle_number.ilike(f'%{query_val}%')).first()
                return [vehicle] if vehicle else []

        abort(400, f"Invalid search parameter '{param_key}' for type '{search_type}'.")

    @staticmethod
    @cache.cached(timeout=300, key_prefix='admin_summary') # Cache for 5 minutes
    def get_summary_data():
        """Aggregates data for the summary dashboard including payment statuses."""
        lots_data = ParkingLot.query.all()
        
        paid_count = Payment.query.filter_by(payment_status=PaymentStatus.PAID).count()
        pending_count = Payment.query.filter_by(payment_status=PaymentStatus.PENDING).count()
        
        payment_summary = {
            "paid": paid_count,
            "pending": pending_count
        }
        
        return {
            "lots": lots_data,
            "payment_summary": payment_summary
        }

# --- API Endpoints ---
@admin_ns.route('/parking-lots')
class ParkingLotListResource(Resource):
    @admin_ns.marshal_list_with(parking_lot_get_model)
    def get(self):
        """Get a list of all parking lots."""
        return AdminServices.get_all_lots()

    @admin_required
    @admin_ns.expect(parking_lot_post_model, validate=True)
    @admin_ns.marshal_with(parking_lot_get_model, code=201)
    def post(self):
        """Create a new parking lot."""
        data = request.get_json()
        return AdminServices.create_lot(data), 201

@admin_ns.route('/parking-lot/<int:lot_id>')
@admin_ns.param('lot_id', 'The unique identifier of the parking lot')
class ParkingLotResource(Resource):
    @admin_ns.marshal_with(parking_lot_get_model)
    def get(self, lot_id):
        """Get details of a specific parking lot."""
        lot = AdminServices.get_lot_by_id(lot_id)
        if not lot:
            abort(404, f"Parking lot with ID {lot_id} not found.")
        return lot

    @admin_required
    @admin_ns.expect(parking_lot_put_model, validate=True)
    @admin_ns.marshal_with(parking_lot_get_model)
    def put(self, lot_id):
        """Update an existing parking lot."""
        lot = AdminServices.get_lot_by_id(lot_id)
        if not lot:
            abort(404, f"Parking lot with ID {lot_id} not found.")
        data = request.get_json()
        return AdminServices.update_lot(lot, data)

    @admin_required
    @admin_ns.response(204, 'Parking lot deleted successfully.')
    def delete(self, lot_id):
        """Delete a parking lot."""
        lot = AdminServices.get_lot_by_id(lot_id)
        if not lot:
            abort(404, f"Parking lot with ID {lot_id} not found.")
        AdminServices.delete_lot(lot)
        return '', 204

@admin_ns.route('/reservation/spot/<int:spot_id>')
class ReservationResourse(Resource):
    
    @admin_required
    @admin_ns.marshal_with(reservation_get_model)
    def get(self, spot_id):
        spot_info = AdminServices.reservation_info(spot_id)
        if not spot_info:
            abort(404, f'Spot info with spod_id: {spot_id} is not found' )
        return spot_info

@admin_ns.route('/spot/<int:spot_id>')
class SpotResource(Resource):
    
    @admin_required
    @admin_ns.response(204, 'Spot deleted successfully.')
    def delete(self, spot_id):
        AdminServices.delete_spot(spot_id)
        return '', 204

@admin_ns.route('/search/<string:search_type>')
@admin_ns.param('search_type', 'The type of entity to search for (lot, user, vehicle)')
class SearchResource(Resource):

    @admin_required
    def get(self, search_type):
        """Search for lots, users, or vehicles based on query parameters."""
        if search_type not in ['lot', 'user', 'vehicle']:
            abort(400, "Invalid search type specified.")
            
        results = AdminServices.search(search_type, request.args.to_dict())

        if search_type == 'lot':
            return admin_ns.marshal(results, parking_lot_get_model)
        elif search_type == 'user':
            return admin_ns.marshal(results, display_user_model)
        elif search_type == 'vehicle':
            return admin_ns.marshal(results, vehicle_model)

        return [], 200

@admin_ns.route('/summary')
class SummaryResource(Resource):
    
    @admin_required
    @cache.cached(timeout=300) # Cache this response for 5 minutes
    @admin_ns.marshal_with(summary_response_model)
    def get(self):
        """Get summary data for the admin dashboard."""
        return AdminServices.get_summary_data()

