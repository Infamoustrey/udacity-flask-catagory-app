import bcrypt
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from db import create_connection

bp = Blueprint('auth', __name__, url_prefix='/auth')


def hash_pass(password_plain_text):
    return bcrypt.hashpw(password_plain_text.encode('utf-8'), bcrypt.gensalt())


def check_pass(pwd, hash):
    return bcrypt.checkpw(pwd.encode('utf-8'), hash.encode('utf-8'))


def login_required(view):
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        return view


@bp.before_app_request
def serialize_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = create_connection().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        db = create_connection()
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not name:
            error = 'Name is required.'
        elif db.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        ).fetchone() is not None:
            error = 'Email {0} is already registered.'.format(email)

        if error is None:
            # input is valid, register the user, redirect to login
            db.execute(
                'INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)',
                (email, name, hash_pass(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('register.jinja2')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    # Validate login info against db
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = create_connection()
        error = None
        user = db.execute(
            'SELECT id, password_hash FROM users WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'No user associated with that email.'
        elif not check_pass(password, user[1]):
            error = 'Incorrect login information.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index'))

        # Send some feedback to the user about what went wrong
        flash(error)

    return render_template('login.jinja2')


@bp.route('/logout')
def logout():
    # Log User Out
    session.clear()
    return redirect(url_for('index'))
