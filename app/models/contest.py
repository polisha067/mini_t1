from datetime import datetime, UTC, timezone
from app.extensions import db
from flask import current_app

class Contest(db.Model):
    """Конкурс (хакатон)"""
    __tablename__ = "contests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    logo_path = db.Column(db.String(255), nullable=True)
    is_finished = db.Column(db.Boolean, nullable=False, default=False)
    is_reopened = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    access_key = db.Column(db.String(64), unique=True, nullable=True, default=None)

    organizer = db.relationship("User", back_populates="contests")
    teams = db.relationship("Team", back_populates="contest", cascade="all, delete-orphan")
    criteria = db.relationship("Criterion", back_populates="contest", cascade="all, delete-orphan")
    assigned_experts = db.relationship("ContestExpert", back_populates="contest", lazy="dynamic", cascade="all, delete-orphan")

    def _format_dt(self, dt):
        if not dt:
            return None
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt.isoformat() + "Z"

    def to_dict(self):
        logo_url = None
        if self.logo_path:
            # Формируем полный URL через Nginx
            uploads_url = current_app.config.get('UPLOADS_URL', '/uploads')
            logo_url = f"{uploads_url}/{self.logo_path}"

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self._format_dt(self.start_date),
            "end_date": self._format_dt(self.end_date),
            "logo_path": self.logo_path,
            "logo_url": logo_url,
            "organizer_id": self.organizer_id,
            "is_finished": self.is_finished,
            "is_reopened": self.is_reopened,
            "created_at": self._format_dt(self.created_at),
        }
    def __repr__(self):
        return f'<Contest {self.name}>'

