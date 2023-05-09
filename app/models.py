from requests import get
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
            critic_reviews = get_metacritic_provider().get_critic_reviews(show.id, show.provider_id)
            user_reviews = get_metacritic_provider().get_user_reviews(show.id, show.provider_id)

            show.reviews = critic_reviews + user_reviews

            db.session.commit()

        positive_reviews, negative_reviews, neutral_reviews = 0, 0, 0

        for review in show.reviews:
            match review.score:
                case ReviewScore.POSITIVE: positive_reviews += 1
                case ReviewScore.NEGATIVE: negative_reviews += 1
                case ReviewScore.NEUTRAL: neutral_reviews += 1

        old_overall_score = show.overall_score

        if positive_reviews > negative_reviews:
            show.overall_score = ReviewScore.POSITIVE
        elif negative_reviews > positive_reviews:
            show.overall_score = ReviewScore.NEGATIVE
        elif neutral_reviews > positive_reviews and neutral_reviews > negative_reviews:
            show.overall_score = ReviewScore.NEUTRAL
        else:
            show.overall_score = ReviewScore.UNKNOWN

        if old_overall_score is not show.overall_score:
            db.session.commit()

        return GetShowResponse(show, positive_reviews, negative_reviews, neutral_reviews) 
    
    def search_show(self, query: str):
        shows = db.session.query(Show).filter(Show.title.contains(query)).all()

        if not shows:
            shows = get_metacritic_provider().search_tv_shows(query)

            if len(shows) == 0:
                return []

            for show in shows:
                show_info = get_metacritic_provider().get_tv_show_info(show)
                db.session.add(show_info)

        db.session.commit()
        return shows

class GetShowResponse:
    show = Show
    positive_reviews = int
    negative_reviews = int
    neutral_reviews = int

    def __init__(self, show: Show, positive_reviews: int, negative_reviews: int, neutral_reviews: int):
        self.show = show
        self.positive_reviews = positive_reviews
        self.negative_reviews = negative_reviews
        self.neutral_reviews = neutral_reviews