from datetime import datetime
from app.extensions import db

class ContestExpert(db.Model):
    """Таблица связи для назначения экспертов на конкретные конкурсы"""
    __tablename__ = 'contest_experts'

    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    contest = db.relationship('Contest', back_populates='assigned_experts')
    expert = db.relationship('User', back_populates='contest_assignments')

    __table_args__ = (
        db.UniqueConstraint('contest_id', 'user_id', name='uix_contest_expert'),
    )

    def __repr__(self):
        return f'<ContestExpert User {self.user_id} -> Contest {self.contest_id}>'