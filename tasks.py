import sqlite3
import logging
from celery import Celery

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)

@celery.task(bind=True)
def add_user_to_db(self, name, email):
    logger.info(f"Starting task {self.request.id}")
    try:
        logger.info(f"Connecting to the database...")
        conn = sqlite3.connect('database.db', timeout=10)
        c = conn.cursor()
        logger.info(f"Inserting user {name} with email {email} into database")
        c.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        logger.info("Executing commit")
        conn.commit()
        logger.info("Closing connection")
        conn.close()
        logger.info(f"User {name} with email {email} added to database successfully")
    except Exception as e:
        logger.error(f"Error adding user to database: {e}")
        raise self.retry(exc=e, countdown=5, max_retries=3)
