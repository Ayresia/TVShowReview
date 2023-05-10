from codecs import BOM_UTF8
from io import StringIO
from app.providers import get_metacritic_provider
from app.database import db
from enum import Enum
from csv import writer as CsvWriter

class ReviewType(Enum):
    CRITIC = 1
    USER = 2

class ReviewScore(Enum):
    POSITIVE = 1
    NEGATIVE = 2
    NEUTRAL = 3
    UNKNOWN = 4

class Review(db.Model):
    id: db.Integer = db.Column(db.Integer, primary_key=True)
    show_id: db.Integer = db.Column(db.Integer, db.ForeignKey('show.id'))
    created_by: ReviewType = db.Column(db.Enum(ReviewType), nullable=False)
    text: db.String = db.Column(db.String(5000), nullable=False)
    score: ReviewScore = db.Column(db.Enum(ReviewScore), nullable=False)

class Genre(db.Model):
    id: db.Integer = db.Column(db.Integer, primary_key=True)
    name: db.String = db.Column(db.String(100), nullable=False)
    show_id: db.Integer = db.Column(db.Integer, db.ForeignKey('show.id'))

class Show(db.Model):
    id: db.Integer = db.Column(db.Integer, primary_key=True)
    provider_id: db.String = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    thumbnail: db.String = db.Column(db.String(100), nullable=False)
    summary: db.String = db.Column(db.String(255), nullable=True)
    release_date: db.String = db.Column(db.String(255), nullable=True)
    overall_score: ReviewScore = db.Column(db.Enum(ReviewScore), nullable=True)
    reviews: db.Mapped[list[Review]] = db.relationship('Review', backref='show', lazy=True)
    genres: db.Mapped[list[Genre]] = db.relationship('Genre', backref='show', lazy=True)

    def get_show(self, id: int, count_reviews: bool):
        show: Show = db.session.query(Show).filter_by(id=id).first()

        if not show.reviews:
            critic_reviews = get_metacritic_provider().get_critic_reviews(show.id, show.provider_id)
            user_reviews = get_metacritic_provider().get_user_reviews(show.id, show.provider_id)

            show.reviews = critic_reviews + user_reviews

        positive_reviews, negative_reviews, neutral_reviews = 0, 0, 0

        if count_reviews or show.overall_score is None:
            for review in show.reviews:
                match review.score:
                    case ReviewScore.POSITIVE: positive_reviews += 1
                    case ReviewScore.NEGATIVE: negative_reviews += 1
                    case ReviewScore.NEUTRAL: neutral_reviews += 1

        if show.overall_score is None:
            if positive_reviews > negative_reviews:
                show.overall_score = ReviewScore.POSITIVE
            elif negative_reviews > positive_reviews:
                show.overall_score = ReviewScore.NEGATIVE
            elif neutral_reviews > positive_reviews and neutral_reviews > negative_reviews:
                show.overall_score = ReviewScore.NEUTRAL
            else:
                show.overall_score = ReviewScore.UNKNOWN

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

    def export_show(self, id) -> bytes:
        get_show_response = self.get_show(id, True);

        output = StringIO()
        csv_writer = CsvWriter(output)

        csv_writer.writerow(["TV Show Title", get_show_response.show.title])
        csv_writer.writerow(["Overall Sentiment Score", get_show_response.show.overall_score.name.capitalize()])

        csv_writer.writerows([
            ["Total Positive Reviews", get_show_response.positive_reviews],
            ["Total Negative Reviews", get_show_response.negative_reviews],
            ["Total Neutral Reviews", get_show_response.neutral_reviews],
        ])

        csv_writer.writerow([])

        csv_writer.writerow(["Created By", "Review Text", "Sentiment Score"])
        csv_writer.writerows([
            [review.created_by.name.capitalize(), review.text, review.score.name.capitalize()]
            for review in get_show_response.show.reviews
        ])

        return BOM_UTF8 + output.getvalue().encode("utf-8-sig")

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
