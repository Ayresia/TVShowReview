from flask import render_template
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template("error.html", message="Page not found")

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", message="Error has occured, please try again")

@main.app_errorhandler(AttributeError)
def attribute_error(e):
    return render_template("error.html", message="Show not found")
