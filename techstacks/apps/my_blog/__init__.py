from flask import Flask
from techstacks.apps.my_blog.templates import bp_hello

app = Flask(
    __name__,
    static_folder="./public",
    template_folder="./static",
)

app.register_blueprint(bp_hello)
