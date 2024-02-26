import os

from app import create_app, db
from dotenv import load_dotenv

load_dotenv('./.env')

app = create_app(os.getenv('FLASK_ENV') or 'default')