from app.models import Show
from . import main
from flask import render_template, request

@main.route("/")
def index():
    return render_template("search.html")

@main.route("/search")
def search():
    query = str(request.args.get("query"))
    shows = Show().search_show(query)

    return render_template("search-results.html", shows=shows)
