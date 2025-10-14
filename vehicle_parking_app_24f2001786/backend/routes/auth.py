from flask import request, jsonify
from flask_restx import Resource, Namespace, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    set_refresh_cookies,
    unset_jwt_cookies,
    current_user,
)
from models import User, UserRole, TokenBlocklist, user_register_model, user_login_model, db, display_user_model
from tasks import send_welcome_email

# --- Setup ---
auth_ns = Namespace('auth', description='Authentication related operations')

# --- Models for Swagger Documentation ---
user_register_model = user_register_model(auth_ns)
user_login_model = user_login_model(auth_ns)
display_user_model = display_user_model(auth_ns)

# --- Service Layer ---
class AuthService:
    @staticmethod
    def register_user(data):
        """Handles new user registration."""
        if User.query.filter_by(email=data['email']).first():
            abort(409, 'Conflict: An account with this email already exists.')
        if User.query.filter_by(username=data['username']).first():
            abort(409, 'This username is already taken.')

        try:
            new_user = User(
                email=data['email'],
                password=data['password'],
                full_name=data['full_name'],
                username=data['username'],
                role=UserRole.USER,
                phone_number=data.get('phone_number'),
                address=data.get('address'),
                pincode=data.get('pincode'),
            )
            db.session.add(new_user)
            db.session.commit()
            send_welcome_email.delay(data['email'])
            return new_user
        except Exception as e:
            db.session.rollback()
            print(f"Error during user registration: {e}")
            abort(500, "An internal error occurred while creating the user.")

    @staticmethod
    def login_user(data):
        """Handles user login and token generation."""
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)

            user_data = {
                "username": user.username,
                "email": user.email,
                "role": user.role.value
            }
            response = jsonify({
                "access_token": access_token,
                "user": user_data
            })
            set_refresh_cookies(response, refresh_token)
            return response
        abort(401, 'Unauthorized: Invalid email or password.')

    @staticmethod
    def logout_user():
        """Handles user logout by blocklisting the refresh token and clearing cookies."""
        try:
            jti = get_jwt()["jti"]
            db.session.add(TokenBlocklist(jti=jti))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error during logout: {e}")

        response = jsonify({"message": "Successfully logged out"})
        unset_jwt_cookies(response)
        return response


# --- API Endpoints ---
@auth_ns.route('/register')
class RegisterResource(Resource):
    @auth_ns.expect(user_register_model, validate=True)
    @auth_ns.marshal_with(display_user_model, code=201)
    def post(self):
        """Create a new user account."""
        data = request.get_json()
        return AuthService.register_user(data), 201


@auth_ns.route('/login')
class LoginResource(Resource):
    @auth_ns.expect(user_login_model, validate=True)
    def post(self):
        """Log in and set refresh token in cookie."""
        data = request.get_json()
        return AuthService.login_user(data)


@auth_ns.route('/refresh')
class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """Refresh access token using refresh token (from cookie)."""
        new_access_token = create_access_token(identity=current_user)
        return {"access_token": new_access_token}, 200


@auth_ns.route('/logout')
class LogoutResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """Logout user and revoke refresh token."""
        return AuthService.logout_user()

