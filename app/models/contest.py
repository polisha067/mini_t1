from datetime import datetime
from app.extensions import db

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    access_key = db.Column(db.String(64), unique=True, nullable=True, default=None)

    organizer = db.relationship("User", back_populates="contests")
    teams = db.relationship("Team", back_populates="contest", cascade="all, delete-orphan")
    criteria = db.relationship("Criterion", back_populates="contest", cascade="all, delete-orphan")
    assigned_experts = db.relationship("ContestExpert", back_populates="contest", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'logo_path': self.logo_path,
            'is_finished': self.is_finished,
            'organizer_id': self.organizer_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Contest {self.name}>'

