from flask import request
from datetime import datetime, timedelta
from flask_restx import Resource, Namespace, abort, fields
from flask_jwt_extended import jwt_required, current_user
from models import ( 
    db ,
    User, UserRole, display_user_model,
    ParkingLot, SpotStatus, parking_lot_get_model,
    ParkingSpot,
    Vehicle, vehicle_model,
    ReservedParkingSpot, reservation_post_model, reservation_get_model,reservation_put_model,ReservationStatus,
    Payment, payment_post_model, PaymentStatus
    )
from sqlalchemy import or_
from collections import Counter
from .admin import admin_required 
from routes import cache # Import the cache object

# --- Setup ---
user_ns = Namespace('users', description='User related operations')

# --- Models for Swagger Documentation ---
display_user_model = display_user_model(user_ns)
parking_lot_get_model = parking_lot_get_model(user_ns)
vehicle_model = vehicle_model(user_ns)
reservation_post_model = reservation_post_model(user_ns)
reservation_get_model = reservation_get_model(user_ns)
reservation_put_model = reservation_put_model(user_ns)
payment_post_model = payment_post_model(user_ns)

# Models for the new user summary endpoint
favorite_spots_model = user_ns.model('FavoriteSpots', {
    'lot_name': fields.String,
    'spot_number': fields.String
})

user_summary_model = user_ns.model('UserSummary', {
    'monthly_bookings': fields.Raw(description="Bookings over the last 3 months"),
    'favorite_lots': fields.Raw(description="Most frequently used lots"),
    'favorite_spots': fields.List(fields.Nested(favorite_spots_model))
})


# --- Service Layer for User Logic ---
class UserService:
    @staticmethod
    def get_current_user():
        """
        Retrieves the user object associated with the current JWT.
        (No caching needed here as it's handled by current_user proxy per request)
        """
        if not current_user:
            abort(401, "Unauthorized: No valid user session found.")
        return current_user

    @staticmethod
    def get_all_users():
        """
        Retrieves a list of all non-admin users.
        """
        return User.query.filter(User.role != UserRole.ADMIN).order_by(User.full_name).all()
    
    @staticmethod
    def find_parking_lots(search_query):
        """
        Finds all active parking lots by pincode or location name.
        """
        return ParkingLot.query.filter(
            ParkingLot.is_active == True,
            or_(
                ParkingLot.pin_code.like(f"%{search_query}%"),
                ParkingLot.address.like(f"%{search_query}%")
            )
        ).all()

    @staticmethod
    def get_register_vehicle_details(vehicle_number):
        """
        Retrieves vehicle details by vehicle number.
        """
        vehicle = Vehicle.query.filter_by(vehicle_number=vehicle_number).first()
        if not vehicle:
            abort(404, 'No vehicle registered with this vehicle number.')
        return vehicle
    
    @staticmethod
    def book_parking_spot(data):
        """
        Book a parking spot for a vehicle.
        """
        if ReservedParkingSpot.query.filter_by(vehicle_number=data['vehicle_number'], status=ReservationStatus.ACTIVE).first():
            abort(409, f'Vehicle {data["vehicle_number"]} is already have reservation.')
        
        spot = ParkingSpot.query.filter_by(id=data['spot_id']).first()
        spot.status = SpotStatus.OCCUPIED
        
        if not Vehicle.query.filter_by(vehicle_number=data['vehicle_number']).first():
            new_vehicle = Vehicle(
                vehicle_number=data['vehicle_number'],
                user_id=current_user.id,
                fuel_type=data.get('fuel_type'),
                brand=data.get('brand'),
                model=data.get('model'),
                color=data.get('color'),
            )
            db.session.add(new_vehicle)
        
        reservation = ReservedParkingSpot(
            user_id=current_user.id,
            vehicle_number=data['vehicle_number'],
            location = spot.parking_lot.address,
            spot_id=spot.id,
            parking_cost_per_hour=spot.parking_lot.price_per_hour,
        )
        db.session.add(reservation)
        db.session.commit()
        # Invalidate the current user's summary cache since they made a new booking
        cache.delete_memoized(UserService.get_user_summary, current_user.id)
    
    @staticmethod
    def get_all_reservations():
        """
        Get all reservations for the current user.
        """
        return ReservedParkingSpot.query.filter_by(user_id=current_user.id).all()
    
    @staticmethod
    def update_reservation(data, res_id):
        """
        Update a reservation.
        """
        reservation = ReservedParkingSpot.query.get(res_id)
        if not reservation:
            abort(404, 'Reservation not found.')
        if reservation.user_id != current_user.id:
            abort(403, 'Forbidden: You are not authorized to update this reservation.')
        
        reservation.leaving_timestamp = datetime.fromisoformat(data['leaving_timestamp'].replace('Z', '+00:00'))
        reservation.status = ReservationStatus.COMPLETED
        reservation.parking_spot.status = SpotStatus.AVAILABLE
        reservation.parking_spot.revenue += reservation.parking_cost_per_hour
        reservation.parking_spot.parking_lot.revenue += reservation.parking_cost_per_hour
        db.session.commit()
        # Invalidate the current user's summary cache since their reservation history changed
        cache.delete_memoized(UserService.get_user_summary, current_user.id)
    
    @staticmethod
    def process_payment(data):
        """
        Process a payment for a reservation.
        """
        payment = Payment(
            reservation_id=data['reservation_id'],
            amount=data['amount'],
            payment_method=data['payment_method'],
        )
        payment.payment_status = PaymentStatus.PAID
        db.session.add(payment)
        db.session.commit()
        # Invalidate the current user's summary cache in case payment affects summary data
        cache.delete_memoized(UserService.get_user_summary, current_user.id)

    @staticmethod
    @cache.memoize(timeout=900) # Cache per user for 15 minutes
    def get_user_summary(user_id):
        """
        Generates summary data for a specific user's dashboard over the last 3 months.
        """
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        
        reservations = ReservedParkingSpot.query.filter(
            ReservedParkingSpot.user_id == user_id,
            ReservedParkingSpot.parking_timestamp >= three_months_ago
        ).all()

        monthly_counts = Counter(res.parking_timestamp.strftime('%B') for res in reservations)
        lot_locations = [res.parking_spot.parking_lot.prime_location_name for res in reservations if res.parking_spot and res.parking_spot.parking_lot]
        favorite_lots = Counter(lot_locations)

        top_lots = [lot[0] for lot in favorite_lots.most_common(5)]
        favorite_spots_data = []
        for lot_name in top_lots:
            spots_in_lot = [res.parking_spot.spot_number for res in reservations if res.parking_spot and res.parking_spot.parking_lot.prime_location_name == lot_name]
            if spots_in_lot:
                most_common_spot = Counter(spots_in_lot).most_common(1)[0][0]
                favorite_spots_data.append({"lot_name": lot_name, "spot_number": most_common_spot})

        return {
            "monthly_bookings": dict(monthly_counts),
            "favorite_lots": dict(favorite_lots.most_common(5)),
            "favorite_spots": favorite_spots_data
        }

    
# --- API Endpoints ---
@user_ns.route('/me')
class MeResource(Resource):
    @jwt_required()
    @user_ns.marshal_with(display_user_model)
    def get(self):
        """Get the profile of the currently logged-in user."""
        return UserService.get_current_user()

@user_ns.route('/')
class UserListResource(Resource):
    @admin_required
    @cache.cached(timeout=300) # Cache this list for 5 minutes
    @user_ns.marshal_list_with(display_user_model)
    def get(self):
        """Get a list of all users (Admin only)."""
        return UserService.get_all_users()

@user_ns.route('/search')
class ParkingSearchResource(Resource):
    @jwt_required()
    @cache.cached(timeout=120, query_string=True) # Cache based on query parameters for 2 minutes
    @user_ns.marshal_list_with(parking_lot_get_model)
    def get(self):
        """Search for available parking lots by pincode or location."""
        query = request.args.get('q', '')
        if not query:
            abort(400, "A search query ('q' parameter) is required.")
        return UserService.find_parking_lots(query)
    
@user_ns.route('/booking/<string:vehicle_number>')
class BookingResourceGet(Resource):
    @jwt_required()
    @cache.cached(timeout=300) # Cache vehicle details for 5 minutes
    @user_ns.marshal_with(vehicle_model)
    def get(self, vehicle_number):
        """Get details of a specific vehicle."""
        return UserService.get_register_vehicle_details(vehicle_number)
    
@user_ns.route('/booking_spot')
class BookingResourcePost(Resource):
    '''Book a parking spot for a vehicle'''
    @jwt_required()
    @user_ns.expect(vehicle_model)
    @user_ns.marshal_with(vehicle_model)
    def post(self):
        """Book a parking spot."""
        data = request.get_json()
        UserService.book_parking_spot(data)
        return {'message': 'Parking spot booked successfully'}, 201
    
@user_ns.route('/reservations')
class ReservationsResource(Resource):
    @jwt_required()
    @user_ns.marshal_list_with(reservation_get_model)
    def get(self):
        """Get all reservations for the current user."""
        return UserService.get_all_reservations()
    
    @jwt_required()
    @user_ns.expect(reservation_put_model)
    def put(self):
        """Update a reservation."""
        res_id = request.args.get('res_id')
        data = request.get_json()
        UserService.update_reservation(data, res_id)
        return {'message': 'Reservation updated successfully'}, 200
    
@user_ns.route('/payments')
class PaymentsResource(Resource):
    @jwt_required()
    @user_ns.expect(payment_post_model)
    def post(self):
        """Process a payment for a reservation."""
        data = request.get_json()
        UserService.process_payment(data)
        return {'message': 'Payment processed successfully'}, 200

@user_ns.route('/summary')
class UserSummaryResource(Resource):
    @jwt_required()
    @user_ns.marshal_with(user_summary_model)
    def get(self):
        """Get summary data for the current user."""
        # The service method is memoized, so this will hit the cache
        return UserService.get_user_summary(current_user.id)
    
from tasks.reports import export_user_parking_data_to_csv

@user_ns.route('/export-csv')
class ExportDataResource(Resource):
    @jwt_required()
    def post(self):
        """Trigger an asynchronous export of the user's parking data to CSV."""
        try:
            task = export_user_parking_data_to_csv.delay(current_user.id)
            return {
                'message': 'Your data export has started. You will receive an email with the CSV file shortly.',
                'task_id': task.id
            }, 202
        except Exception as e:
            abort(500, f"Failed to start the export task: {e}")

