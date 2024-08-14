from app.utils import analyze_data_gemini, process_json, extract_data_from_HTML, url_to_image, predict_image_class
from app.utils import predict_top_5_classes
from app import forms
import json
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from PIL import Image

# FLASK
from flask import Flask, Blueprint, render_template, request, url_for, redirect, flash, send_from_directory, jsonify, current_app

# IMAGES
from PIL import Image

views = Blueprint('views', __name__)


# ---------------------------------------------------- WEBSITE ----------------------------------------------------
# ------------- HOME PAGE -------------
@views.route("/")
def home():
    return render_template("index.html")

@views.route('/api-docs/', methods=['GET'])
def api_docs():
    return render_template('api-docs.html')

@views.route('/upload/', methods=['GET', 'POST'])
def upload():
    form = forms.UploadForm()
    answer = request.args.get('answer', "Insert text and Image to recieve JSON")

    if request.method == 'POST':
        if form.validate_on_submit():

            dive_text = form.text_input.data
            image = form.image.data
            if image is None:
                img = 'No Image'
            else:
                img = Image.open(image)

            answer = analyze_data_gemini(dive_text, img)

            flash('File successfully uploaded')
            return redirect(url_for('views.upload', answer=answer))
    
    return render_template('upload.html', form=form, answer=answer)

@views.route('/html-analyze/', methods=['GET', 'POST'])
def html_analyze():
    form = forms.TxtUploadForm()
    if form.validate_on_submit():
        txt_file = form.txt_file.data 
        text = txt_file.read().decode('utf-8') 

        response, status_code = extract_data_from_HTML(text)

        return response, status_code
    return render_template('html-analyze.html', form=form)

@views.route('/about/', methods=['GET'])
def about():
    return render_template('about.html')

# ---------------------------------------------------- API ----------------------------------------------------
@views.route('/api/upload', methods=['POST'])
def api_upload():
    if request.method == 'POST':
        if request.is_json:
            data = request.json
            response, status_code = process_json(data)
            return response, status_code
        else:
            return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400

    else:
        return jsonify({'status': 'error', 'message': 'Use POST method to send JSON data'}), 405
    

@views.route('/api/html-analyze/', methods=['POST'])
def api_html_analyze():
    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'text/plain':
            html = request.data.decode('utf-8')
            response, status_code = extract_data_from_HTML(html)
            return response, status_code
        else:
            return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400

    else:
        return jsonify({'status': 'error', 'message': 'Use POST method to send JSON data'}), 405

