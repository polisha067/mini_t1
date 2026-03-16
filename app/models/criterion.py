from app.extensions import db

class Criterion(db.Model):
    """Критерий оценивания внутри конкурса"""
    __tablename__ = "criteria"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    max_score = db.Column(db.Integer, nullable=False, default=10)

    contest_id = db.Column(db.Integer, db.ForeignKey("contests.id"), nullable=False, index=True)

    contest = db.relationship("Contest", back_populates="criteria")
    grades = db.relationship("Grade", back_populates="criterion", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'max_score': self.max_score,
            'contest_id': self.contest_id
        }

    def __repr__(self):
        return f'<Criterion {self.name}>'