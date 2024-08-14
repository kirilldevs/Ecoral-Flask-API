from dotenv import dotenv_values
from app import forms
from app.views import views
from flask import Flask
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Dropout
import requests
from flask_cors import CORS

# ------------- IMPORT VIRTUAL VARIABLES -------------
config = dotenv_values(".env")
MY_SECRET_KEY = config['SECRET_KEY']

# ------------- APP INIT + SECRET KEY -------------
app = Flask(__name__)
app.config['SECRET_KEY'] = MY_SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'uploads'

# ------------- ENABLE CORS -------------
CORS(app)  # This will allow all origins by default

# ------------- REGISTER BLUEPRINTS -------------
app.register_blueprint(views, url_prefix='/')

if __name__ == "__main__":
    app.run(debug=True)
