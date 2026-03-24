from datetime import datetime
from app.extensions import db

class Grade(db.Model):
    """Оценка эксперта за конкретную команду по конкретному критерию"""
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    expert_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False, index=True)
    criterion_id = db.Column(db.Integer, db.ForeignKey("criteria.id"), nullable=False, index=True)

    expert = db.relationship("User", back_populates="grades")
    team = db.relationship("Team", back_populates="grades")
    criterion = db.relationship("Criterion", back_populates="grades")

    __table_args__ = (
        db.UniqueConstraint("expert_id", "team_id", "criterion_id", name="uix_grade_expert_team_criterion"),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'comment': self.comment,
            'expert_id': self.expert_id,
            'team_id': self.team_id,
            'criterion_id': self.criterion_id,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Grade {self.value} (Expert {self.expert_id} -> Team {self.team_id})>'