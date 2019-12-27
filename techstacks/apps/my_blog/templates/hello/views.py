from flask import Blueprint, render_template

bp_hello = Blueprint("hello", __name__)


@bp_hello.route("/")
@bp_hello.route("/hello")
def index():
    return render_template("index.html")
