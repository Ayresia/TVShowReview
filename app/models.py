from app.providers import get_metacritic_provider
from app.database import db
from enum import Enum

class ReviewType(Enum):
    CRITIC = 1
    USER = 2

class ReviewScore(Enum):
    POSITIVE = 1
    NEGATIVE = 2
    NEUTRAL = 3
    UNKNOWN = 4

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    created_by = db.Column(db.Enum(ReviewType), nullable=False)
    text = db.Column(db.String(5000), nullable=False)
    score = db.Column(db.Enum(ReviewScore), nullable=False)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(255), nullable=True)
    release_date = db.Column(db.String(255), nullable=True)
    overall_score = db.Column(db.Enum(ReviewScore), nullable=True)
    reviews = db.relationship('Review', backref='show', lazy=True)
    genres = db.relationship('Genre', backref='show', lazy=True)

    def get_show(self, id: int):
        show: Show = db.session.query(Show).filter_by(id=id).first()

        if not show.reviews:
            overall_score = 0

            critic_reviews = get_metacritic_provider().get_critic_reviews(show.id, show.provider_id)
            user_reviews = get_metacritic_provider().get_user_reviews(show.id, show.provider_id)

            show.reviews = critic_reviews + user_reviews

            for review in show.reviews:
                overall_score += review.score.value

            print(overall_score)

            if overall_score > 0:
                show.overall_score = ReviewScore(round(overall_score / len(show.reviews)))
            else:
                show.overall_score = ReviewScore.UNKNOWN

        db.session.commit()
        return show

