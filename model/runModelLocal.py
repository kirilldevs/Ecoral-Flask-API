from flask import Flask, request, jsonify, current_app
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Dropout
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

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
model.load_weights('ecoralVGG16.weights.h5')

species_data = {
    'Abudefduf vaigiensis': 'Sharks & Rays',
    'Acanthurus sohal': 'Sharks & Rays',
    'Acropora sp': 'Sharks & Rays',
    'Amphiprion bicinctus': 'Sharks & Rays',
    'Aurelia aurita': 'Sharks & Rays',
    'Caesio suevica': 'Sharks & Rays',
    'Caranx sp': 'Sharks & Rays',
    'Carcharhinus amblyrhynchos': 'Sharks & Rays',
    'Cephalopholis miniata': 'Sharks & Rays',
    'Chaetodon auriga': 'Sharks & Rays',
    'Chelidonura flavolobata': 'Sharks & Rays',
    'Chelonia mydas': 'Sharks & Rays',
    'Choriaster granulatus': 'Sharks & Rays',
    'Cyclichthys spilostylus': 'Sharks & Rays',
    'Epinephelus fasciatus': 'Sharks & Rays',
    'Epinephelus polyphekadion': 'Sharks & Rays',
    'Goniobranchus annulatus': 'Sharks & Rays',
    'Heniochus intermedius': 'Sharks & Rays',
    'Heterocentrotus mamillatus': 'Sharks & Rays',
    'Holacanthus ciliaris': 'Sharks & Rays',
    'Holothuria atra': 'Sharks & Rays',
    'Iago omanensis': 'Sharks & Rays',
    'Millepora dichotoma': 'Sharks & Rays',
    'Myrichthys maculosus': 'Sharks & Rays',
    'Octopus vulgaris': 'Sharks & Rays',
    'Plotosus lineatus': 'Sharks & Rays',
    'Rhincodon typus': 'Sharks & Rays',
    'Scarus sp': 'Sharks & Rays',
    'Seriolina nigrofasciata': 'Sharks & Rays',
    'Sphyraena barracuda': 'Sharks & Rays',
    'Stegostoma tigrinum': 'Sharks & Rays'
}

app.config['MODEL'] = model
app.config['SPECIES_DATA'] = species_data

def url_to_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        print("CONVERTING URL TO IMAGE")
        img_bytes = BytesIO(response.content)
        img = Image.open(img_bytes).convert('RGB')
        return img
    else:
        raise Exception(f"Failed to fetch image from URL. Status code: {response.status_code}")

def predict_image_class(image_url):
    try:
        img = url_to_image(image_url)
        img = img.resize((224, 224))

        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0 

        model = current_app.config['MODEL']
        species_data = current_app.config.get('SPECIES_DATA')

        predictions = model.predict(img_array)
        top_prediction_idx = np.argmax(predictions[0])
        top_prediction_class = list(species_data.keys())[top_prediction_idx]
        object_group = species_data.get(top_prediction_class)

        return {
            "specie": top_prediction_class,
            "objectGroup": object_group
        }

    except Exception as e:
        return {"error": str(e)}

# Flask route for prediction
@app.route('/predict', methods=['POST'])
def predict():
    print("IN PREDICT")
    
    image_url = request.json.get('image_url')
    print(image_url)

    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400

    result = predict_image_class(image_url)
    
    return jsonify(result)

@app.route('/', methods=['GET'])
def home():
    return jsonify('Hello World!')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6500)
