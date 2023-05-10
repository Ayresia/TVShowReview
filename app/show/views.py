from flask import render_template
from flask.wrappers import Response

from . import show
from ..models import Show

@show.route("/<int:id>")
def get_show(id):
    get_show_response = Show().get_show(id, True)
    
    return render_template(
        "show.html",
        show=get_show_response.show,
        positive_reviews=get_show_response.positive_reviews,
        negative_reviews=get_show_response.negative_reviews,
        neutral_reviews=get_show_response.neutral_reviews
    )

@show.route("/<int:id>/reviews")
def get_all_show_reviews(id):
    get_show_response = Show().get_show(id, False)
    return render_template('show-reviews.html', show=get_show_response.show)

@show.route("/<int:id>/export")
def export_show(id):
    exported_show = Show().export_show(id)

    return Response(
        response= exported_show,
        mimetype= "text/csv; charset=utf-8-sig",
        headers= { "Content-Disposition": f"attachment; filename={id}-analysis.csv" }
    )
