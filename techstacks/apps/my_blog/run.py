from techstacks.apps.my_blog import app


@app.route("/")
def hello_world():
    return "hello, world. From flask"


if __name__ == '__main__':
    from techstacks.apps.my_blog import configurations

    app.config.from_object(configurations.DevelopmentConfig)
    app.run()
