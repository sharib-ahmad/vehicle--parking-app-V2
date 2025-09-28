from models import db
from datetime import datetime, timedelta ,timezone

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def cleanup_blocklist(cls, days: int = 1):
        """Delete tokens older than `days` (default 1 day)."""
        expiration_time = datetime.now(timezone.utc) - timedelta(days=days)
        deleted = cls.query.filter(cls.created_at < expiration_time).delete()
        db.session.commit()
        return deleted

    def __repr__(self):
        return f"<TokenBlocklist {self.jti}>"