# import sqlite3
# import time
#
# from celery import Celery
# from flask import Flask, render_template_string, request, redirect, url_for, render_template
#
# app = Flask(__name__)
# app.config.update(
#     CELERY_BROKER_URL='redis://localhost:6379/0',
#     CELERY_RESULT_BACKEND='redis://localhost:6379/0'
# )
# celery = Celery(
#     app.import_name,
#     broker='redis://localhost:6379/0',
#     backend='redis://localhost:6379/0',
# )
#
#
# def init_db():
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS users
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
#                   name TEXT NOT NULL,
#                   email TEXT NOT NULL)''')
#     conn.commit()
#     conn.close()
#
#
# init_db()
#
#
# @celery.task()
# def add_user_to_db(name, email):
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
#     conn.commit()
#     conn.close()
#
#
# @app.route('/')
# def index():
#     return render_template('form.html')
#
#
# @app.route('/submit', methods=['POST'])
# def submit():
#     name = request.form['name']
#     email = request.form['email']
#
#     add_user_to_db.delay(name, email)
#
#     return redirect(url_for('index'))
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
import sqlite3
import logging
from celery import Celery
from flask import Flask, render_template_string, request, redirect, url_for
from tasks import add_user_to_db  # Importowanie zadania Celery

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0',
    SQL_ALCHEMY_DATABASE_URL = 'sqlite:///db.sqlite3'
)
celery = Celery(
    app.import_name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND'],
)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL)''')
    conn.commit()
    conn.close()
    logger.info("Database initialized")

init_db()

@app.route('/')
def index():
    return render_template_string('''
        <form action="{{ url_for('submit') }}" method="post">
            Name: <input type="text" name="name"><br>
            Email: <input type="text" name="email"><br>
            <input type="submit" value="Submit">
        </form>
    ''')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    logger.info(f"Received submission: name={name}, email={email}")
    add_user_to_db.apply_async((name, email))
    logger.info(f"Task to add user {name} with email {email} sent to Celery")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

