from os import path
from app import create_app
from dotenv import load_dotenv

dotenv_path = path.join(path.dirname(__file__), '.env')

if path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app()
app.run() 
