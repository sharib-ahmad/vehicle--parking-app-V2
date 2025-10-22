from models import db, EnumField
from flask_restx import fields
import enum
import uuid
from sqlalchemy.dialects.sqlite import BLOB
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash


class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(BLOB, primary_key=True, default=lambda: uuid.uuid4().bytes)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    reservations = db.relationship(
        "ReservedParkingSpot",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    vehicles = db.relationship(
        "Vehicle", back_populates="user", cascade="all, delete-orphan"
    )
    # Password handling
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Helper: return UUID as string
    @property
    def uuid(self):
        return str(uuid.UUID(bytes=self.id))
    
    # Helper: return user role as string
    @property
    def role_value(self):
        return self.role.value

    def __repr__(self):
        return f"<User {self.username}>"
    
def user_register_model(ns):
    return ns.model('UserRegister', {
        'full_name': fields.String(required=True, description='Full Name'),
        'username': fields.String(required=True, description='Username'),
        'email': fields.String(required=True, description='Email'),
        'password': fields.String(required=True, description='Password'),
        'phone_number': fields.String(required=True, description='Phone Number'),
        'address': fields.String(required=True, description='Address'),
        'pincode': fields.String(required=True, description='Pincode'),
    })

def user_login_model(ns):
    return ns.model('UserLogin', {
        'email': fields.String(required=True, description='Email'),
        'password': fields.String(required=True, description='Password'),
    })

def display_user_model(ns):
    return ns.model('DisplayUser', {
        'full_name': fields.String(required=True, description='Full Name'),
        'username': fields.String(required=True, description='Username'),
        'email': fields.String(required=True, description='Email'),
        'phone_number': fields.String(required=True, description='Phone Number'),
        'address': fields.String(required=True, description='Address'),
        'pincode': fields.String(required=True, description='Pincode'),
        'role': EnumField(required=True, description='Role'),
        'created_at': fields.DateTime(required=True, description='Created At'),

    })