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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

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
            'organizer_id': self.organizer_id
        }

    def __repr__(self):
        return f'<Contest {self.name}>'

