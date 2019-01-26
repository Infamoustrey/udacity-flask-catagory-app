import sqlite3
import bcrypt


def create_connection():
    try:
        connection = sqlite3.connect('catalog.sqlite')
        return connection
    except IOError as e:
        print(e)
        return None


def init_database():
    database = create_connection()

    with open('schema.sql', "r") as f:
        database.executescript(f.read().decode('utf8'))
        database.commit()

    # Create My User
    query = "insert into users (email, name, password_hash) VALUES (?, ?, ?);"
    data = (
        'treybfoster@gmail.com',
        'Trey Foster',
        bcrypt.hashpw('secret', bcrypt.gensalt())
    )
    database.execute(query, data)
    database.commit()
