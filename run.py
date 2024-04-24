from dotenv import dotenv_values

from app.utils import url_to_image, analyze_data_gemini
from app import forms
from app.views import views

# FLASK
from flask import Flask

# ------------- IMPORT VIRTUAL VARIABLES -------------
config = dotenv_values(".env")
MY_SECRET_KEY = config['SECRET_KEY']
GOOGLE_API_KEY = config['GOOGLE_API_KEY']

# ------------- APP INIT + SECRET KEY -------------
app = Flask(__name__)

app.config['SECRET_KEY'] = MY_SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'uploads'

# ------------- REGISTER BLUEPRINTS -------------
app.register_blueprint(views, url_prefix='/')

if __name__ == "__main__":
    app.run(debug=True)
