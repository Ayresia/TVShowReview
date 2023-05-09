from flask import render_template
from . import show
from ..models import Show, ReviewScore

@show.route('/<int:id>')
def get_show(id):
    show = Show().get_show(id)
    
    positive_reviews, negative_reviews, neutral_reviews = 0, 0, 0 

    for review in show.reviews:
        match review.score:
            case ReviewScore.POSITIVE: positive_reviews += 1
            case ReviewScore.NEGATIVE: negative_reviews += 1
            case ReviewScore.NEUTRAL: neutral_reviews += 1
            
    return render_template(
        'show.html',
        show=show,
        positive_reviews=positive_reviews,
        negative_reviews=negative_reviews,
        neutral_reviews=neutral_reviews
    )

@show.route("/<int:id>/reviews")
def get_all_show_reviews(id):
    show = Show().get_show(id)
    return render_template('show-reviews.html', show=show)
