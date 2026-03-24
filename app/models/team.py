from datetime import datetime
from app.extensions import db

class Team(db.Model):
    """Команда-участник конкурса"""
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)
    contest_id = db.Column(db.Integer, db.ForeignKey("contests.id"), nullable=False, index=True)

    contest = db.relationship("Contest", back_populates="teams")
    grades = db.relationship("Grade", back_populates="team", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'contest_id': self.contest_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Team {self.name}>'
