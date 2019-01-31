from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from db import create_connection

bp = Blueprint('items', __name__, url_prefix='/items')


def login_required(view):
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        return view


@bp.route('/', methods=('GET', 'POST'))
def index():
    get_categories = create_connection().execute(
            'SELECT * FROM items'
        ).fetchall()
    return render_template('categories/index.jinja2', categories=get_categories)


@bp.route('/<item_title>')
def show(item_title):
    item = create_connection().execute(
            'SELECT * FROM items where title = ?', (item_title,)
        ).fetchone()
    return render_template('items/show.jinja2', item=item)


@bp.route('/create', methods=('GET', 'POST'))
def create():
    db = create_connection()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']

        errors = []

        if not title:
            errors.append('Title is required.')
        elif not description:
            errors.append('Description is required.')
        elif not category:
            errors.append('Category is required.')
        elif not g.user:
            errors.append('You must be logged in to add an item.')

        if not errors:
            db.execute('insert into items (title, description, category, owner) values (?, ?, ?, ?)', (title, description, category, g.user[0],))
            db.commit()
            return redirect(url_for('item.show', item_title=title))

        flash(errors)

    categories = db.execute('select id, name from categories').fetchall()

    return render_template('items/create.jinja2', categories=categories)


@bp.route('/<string:item_title>/update', methods=('GET', 'POST'))
def update(item_title):
    db = create_connection()
    item = db.execute('select * from items where title = ?', (item_title,)).fetchone()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']

        errors = []

        if not title:
            errors.append('Title is required.')
        elif not description:
            errors.append('Description is required.')
        elif not category:
            errors.append('Category is required.')
        elif not g.user:
            errors.append('You must be logged in to add an item.')
        elif g.user[0] is not item[4]:
            errors.append('You do not have permission to update this post.')

        if not errors:
            db.execute('update items set title = ?, description = ?, category = ? where title = ?',
                       (title, description, category, item_title,))
            db.commit()
            return redirect(url_for('items.show', item_title=title))

        flash(errors)

    categories = db.execute('select id, name from categories').fetchall()

    return render_template('items/update.jinja2', item=item, categories=categories)
