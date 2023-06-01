from os import path
from app import create_app
from dotenv import load_dotenv

dotenv_path = path.join(path.dirname(__file__), '.env')

if path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from nltk import download

download('vader_lexicon')
download('stopwords')
download('punkt')
download('wordnet')

app = create_app()
app.run() 
