from dotenv import dotenv_values
from app import forms
from app.views import views
from flask import Flask
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Dropout
import requests

# ------------- IMPORT VIRTUAL VARIABLES -------------
config = dotenv_values(".env")
MY_SECRET_KEY = config['SECRET_KEY']
new=""
# ------------- APP INIT + SECRET KEY -------------
app = Flask(__name__)
app.config['SECRET_KEY'] = MY_SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'uploads'

# ------------- REGISTER BLUEPRINTS -------------
app.register_blueprint(views, url_prefix='/')

# ------------- MODEL INITIALIZATION -------------
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

for layer in base_model.layers[-10:]:
    layer.trainable = True

model = Sequential([
    base_model,
    Flatten(),
    Dense(256, activation='relu', name='dense_6'),
    Dense(128, activation='relu', name='dense_7'),
    Dropout(0.5, name='dropout_8'),
    Dense(31, activation='softmax', name='dense_8')
])

input_shape = (224, 224, 3)
model.build(input_shape=(None, *input_shape))
# model.load_weights('../ecoralVGG16.weights.h5')
# model.summary()
# app.config['MODEL'] = model
app.config['LABELS'] = {
    0: 'Abudefduf vaigiensis',
    1: 'Acanthurus sohal',
    2: 'Acropora sp',
    3: 'Amphiprion bicinctus',
    4: 'Aurelia aurita',
    5: 'Caesio suevica',
    6: 'Caranx sp',
    7: 'Carcharhinus amblyrhynchos',
    8: 'Cephalopholis miniata',
    9: 'Chaetodon auriga',
    10: 'Chelidonura flavolobata',
    11: 'Chelonia mydas',
    12: 'Choriaster granulatus',
    13: 'Cyclichthys spilostylus',
    14: 'Epinephelus fasciatus',
    15: 'Epinephelus polyphekadion',
    16: 'Goniobranchus annulatus',
    17: 'Heniochus intermedius',
    18: 'Heterocentrotus mamillatus',
    19: 'Holacanthus ciliaris',
    20: 'Holothuria atra',
    21: 'Iago omanensis',
    22: 'Millepora dichotoma',
    23: 'Myrichthys maculosus',
    24: 'Octopus vulgaris',
    25: 'Plotosus lineatus',
    26: 'Rhincodon typus',
    27: 'Scarus sp',
    28: 'Seriolina nigrofasciata',
    29: 'Sphyraena barracuda',
    30: 'Stegostoma tigrinum'
    }

if __name__ == "__main__":
    app.run(debug=True)
