from models import db 
from datetime import datetime, timezone

class UserProfile(db.Model):
    __tablename__ = "user_profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(50), db.ForeignKey("users.id"), unique=True, nullable=False
    )
    bio = db.Column(db.Text)
    image = db.Column(db.LargeBinary, nullable=True)
    image_mimetype = db.Column(db.String(50), nullable=True)
    date_of_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    user = db.relationship("User", back_populates="profile")