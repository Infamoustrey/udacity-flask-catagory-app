from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from db import create_connection

bp = Blueprint('categories', __name__, url_prefix='/categories')


def login_required(view):
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        return view


@bp.route('/', methods=('GET', 'POST'))
def index():
    get_categories = create_connection().execute(
            'SELECT id, name FROM categories'
        ).fetchall()
    return render_template('categories/index.jinja2', categories=get_categories)


@bp.route('/<category_name>')
def show(category_name):
    category = create_connection().execute(
            'SELECT id, name FROM categories where name = ?', (category_name,)
        ).fetchone()
    return render_template('categories/show.jinja2', category=category)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        db = create_connection()
        error = None

        if not name:
            error = 'Name is required.'
        elif db.execute(
            'SELECT name FROM categories WHERE name = ?', (name,)
        ).fetchone() is not None:
            error = 'Category {0} already exists.'.format(name)

        if error is None:
            # input is valid, register the user, redirect to login
            db.execute('INSERT INTO categories (name) VALUES (?)', (name,))
            db.commit()
            return redirect(url_for('categories.index'))

        flash(error)

    return render_template('categories/create.jinja2')
