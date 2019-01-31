from flask import Flask, render_template, g, session
import jinja2
from db import create_connection

# Modules
import auth, categories, items

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='hDx=M[)6s6B%x}E8p,Ro3Y*NR',
    DATABASE='catalog.sqlite',
)

# I Like the views over templates
app.jinja_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('./views'),
])


@app.before_request
def serialize_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = create_connection().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


# Index
@app.route('/')
def index():
    return render_template('home.jinja2', user=g.user)


app.register_blueprint(auth.bp)
app.register_blueprint(categories.bp)
app.register_blueprint(items.bp)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)