from flask import render_template
from . import show
from ..models import Show

@show.route("/<int:id>")
def get_show(id):
    show_response = Show().get_show(id, True)
    
    return render_template(
        'show.html',
        show=show_response.show,
        positive_reviews=show_response.positive_reviews,
        negative_reviews=show_response.negative_reviews,
        neutral_reviews=show_response.neutral_reviews
    )

@show.route("/<int:id>/reviews")
def get_all_show_reviews(id):
    show_response = Show().get_show(id, False)
    return render_template('show-reviews.html', show=show_response.show)
