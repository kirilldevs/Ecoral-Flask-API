# IMAGES
from PIL import Image
from io import BytesIO
import requests
import json
from flask import jsonify
from flask import current_app
import requests


# MODELS AND RELATED
import numpy as np
from tensorflow.keras.preprocessing.image import load_img, img_to_array


# HTML
from bs4 import BeautifulSoup

# GEMINI
import google.generativeai as genai
from google.api_core.exceptions import InternalServerError
from google.generativeai.types.generation_types import BlockedPromptException


# # ------------- IMPORT VIRTUAL VARIABLES -------------
from dotenv import dotenv_values
config = dotenv_values(".env")

TEST = config['TEST']
print(TEST)

GEMINI_KEY = config['GEMINI_KEY']
genai.configure(api_key=GEMINI_KEY)


# ------------- TEXT AND IMAGE ANALYZE - GEMINI -------------
def analyze_data_gemini(dive_text, img):
    print("IN GEMINI")
    json_structure = '{"date": ,"time":, "diveSite": ,"objectGroup":, "specie":, "imageLocation":, "AR":}'
    json_not_usefull = '{"no data": "No usefull data"}'
    json_no_images = '{"no data": "No images in this post"}'
    json_no_images = '{"no data": "No images in this post"}'
    json_no_data = '{"no data": "The post is not about diving"}'
    json_no_israelOrSales = '{"no data": "The post is not about diving in Israel region or advertisement"}'
    json_no_israelOrSales = '{"no data": "The post is not about diving in Israel region or advertisement"}'
    parameters_explanation_before = '''date - date of the dive,
        time - light/night,
        diveSite - site name,
        objectGroup - one of this options (Cephalopods, Artificial Reef, Coral Reef, Divers, Dolphins, Invertebrate, Large Reef Fish, Medium Reef Fish, Small ReefFish, Mollusca and Worms, Rays, Sea Turtles, Sharks, NA),
        specie-the exact animal specie,
        imageLocation-image location choose one of (Artificial Reef, Blue, Coral reef, NA,Patched reef, Sandy Bottom, Sea Grass),
        AR - Yes/NO if there is an artificial reef in the image,
        '''

    parameters_explanation = parameters_explanation_before.replace('\n', ' ')

    promt_instructions = f'return a json file in the next format: {json_structure}, explanation of each parameter: {parameters_explanation}. if some information is missing type "null", if all information is missing return {json_not_usefull}, if the text is not about diving at all return {json_no_data}, if there is a region in the text and it is not Israel or the text is advertisement return {json_no_israelOrSales}.'
    
    print("DIVE TEXT",dive_text)

    try:
        if isinstance(img, Image.Image):
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([f'I am giving you a text and an image about diving, {promt_instructions} the text: {dive_text}', img], stream=True)
            response.resolve()
            print("RESPONSE:")
            print(response.text)
        else:
            # model = genai.GenerativeModel('gemini-pro')
            # response = model.generate_content(f'I am giving you a text about diving, {promt_instructions} the text: {dive_text}')
            response = json_no_images

        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
        print("\nCLEANED TEXT:")
        print(cleaned_text)

        try:
            json_data = json.loads(cleaned_text)
            return json_data
        
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e.msg}, at position {e.pos}")
            json_data = json.loads('{"no data": "Some error occured 1"}')
            return json_data 
        
    except BlockedPromptException as e:
        print(f"promt error: {e.msg}, at position {e.pos}")
        json_data = json.loads('{"no data": "Some error occured 2"}')
        return json_data 
    
    except Exception as e:
        print(f"some error: {str(e)}")
        json_data = json.loads('{"no data": "Some error with GEMINI service"}')
        return json_data 

# ------------- MODEL PREDICTIONS TOP 5-------------
def predict_top_5_classes(image_path):
    model = current_app.config['MODEL']
    labels = current_app.config.get('LABELS')

    img = load_img(image_path, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    predictions = model.predict(img_array)
    top_5_indices = np.argsort(predictions[0])[-5:][::-1]
    top_5_classes = [(labels[i], predictions[0][i]) for i in top_5_indices]

    return top_5_classes


def predict_image_class(image_url):
    try:
        img, encoded_img = url_to_image(image_url)
        img = img.resize((224, 224))

        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)  #
        img_array = img_array / 255.0 

        model = current_app.config['MODEL']
        labels = current_app.config.get('LABELS')

        predictions = model.predict(img_array)
        top_prediction_idx = np.argmax(predictions[0])
        top_prediction_class = labels[top_prediction_idx]

        return {
            "label": top_prediction_class
        }

    except Exception as e:
        return {"error": str(e)}

# ------------- MY MODEL - PREDICT SPECIE AND OBJGROUP -------------
def get_specie_objGroup(image_url):
    url = "https://d1e9-147-235-202-80.ngrok-free.app/predict"
    data = {
        "image_url": image_url
    }
    
    response = requests.post(url, json=data)
    response_data = response.json()
    
    # Extract and return the specie and objectGroup
    specie = response_data.get('specie')
    object_group = response_data.get('objectGroup')
    
    return specie, object_group

# ------------- CONVERT IMAGE URL TO IMAGE FILE -------------
def url_to_image(url):
    print("IN URL IMAGE")
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        print("CONVERTING URL TO IMAGE")
        img_bytes = BytesIO(response.content)
        img = Image.open(img_bytes).convert('RGB')
        return img
    else:
        raise Exception(f"Failed to fetch image from URL. Status code: {response.status_code}")
   
def process_json(data):
        print("IN PROCESS JSON")
        arr = data.get('arr', [])
        arr_error_posts = []
        number_of_posts = len(arr)
        successful_posts = 0
        results = []
        answer = {}

        if not arr:
            return jsonify({'status': 'error', 'message': 'Data Is Empty'}), 400
        
        elif not isinstance(arr, list):
            return jsonify({'status': 'error', 'message': 'Wrong JSON structure, arr must be an array'}), 400

        for post in arr:
            try:
                print('\n\n*************************************************')
                print("POST:", post)
                print("IMAGE:", post['image'])
                print("TEXT:", post['text'])
                print('*************************************************\n\n')
    
                text = post.get('text', "")
                image_url = post.get('image', False)
                print("IMAGE URL from POST post.GET", image_url)
                video = post.get('video', False)

                if (image_url or video):
                    if (image_url):
                        try:
                            print("OK")
                            img = url_to_image(image_url)
                        except Exception as e:
                            print(f"Error getting image: {e}")
                    else:
                        img = None

                    try:        
                        # answer = analyze_data_gemini(text, img)
                        successful_posts += 1
                        results.append(answer)
                    except Exception as e:
                        print(f"Error adding post to results data: {e}")
                        arr_error_posts.append(post)
                        answer = {}
                        
                    try:
                        answer['spicie'],answer['objGroup']=get_specie_objGroup(image_url)
                    except Exception as e:
                        print(f"Error getting predictions: {e}")



                    answer["file"] = post.get('url', 'url not found')
                    if(video):
                        answer["video"] = post.get('video')
                        answer["documentation"] = "v"
                        
                    answer["media"] = "Facebook"
                    answer["image"] = post['image']
                    if post['image']!="Error getting image URL":
                        answer["documentation"] = "p"
            except Exception as e:
                print(post)
                print(f"Error processing POST: {e}")
        print("\n\n\n")
                
                
        if (successful_posts/len(results) == 1):
            return jsonify({'status': 'success', 'message': 'Data processed', 'data': results, 'number of posts': successful_posts}), 200
        elif(successful_posts == 0):
            return jsonify({'status': 'partial_success', 'message': 'The data wasnt analyzed, you can check the posts manually.', 'Unanalyzed Posts': arr_error_posts, 'nextSteps': 'Try again in 60 seconds or Contact the admin', 'results':successful_posts/number_of_posts}), 206
        else:
            return jsonify({'status': 'artial_success', 'message': 'Some data fragments were not retrieved due to internal server errors.', 'successfulData': results, 'Unanalyzed Posts': arr_error_posts, 'nextSteps': 'try again in 60 seconds', 'results':successful_posts/number_of_posts}), 206

def extract_data_from_HTML(txt):
    print("IN EXTRACT HTML")

    soup = BeautifulSoup(txt, 'html.parser')

    # feed_divs = soup.find_all('div', role="feed")
    feed_divs = soup.find_all('div', {'data-pagelet': 'GroupFeed'})

    initial_classes = ["x1yztbdb", "x1n2onr6", "xh8yej3", "x1ja2u2z"]
    nested_classes_for_text = "xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs".split()
    nested_classes_for_images = "x1ey2m1c xds687c x5yr21d x10l6tqk x17qophe x13vifvy xh8yej3 xl1xv1r".split()
    alternate_classes_for_images = "xz74otr x1ey2m1c xds687c x5yr21d x10l6tqk x17qophe x13vifvy xh8yej3".split()
    nested_a_classes_for_videos = "x1i10hfl x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 xe8uvvx x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1n2onr6 x87ps6o x1lku1pv xjbqb8w x76ihet xwmqs3e x112ta8 xxxdfa6 x1ypdohk x1rg5ohu x1qx5ct2 x1k70j0n x1w0mnb xzueoph x1mnrxsn x1iy03kw xexx8yu x4uap5 x18d9i69 xkhd6sd x1o7uuvo x1a2a7pz".split()
    # classes_a_for_url = ["x1i10hfl", "xjbqb8w", "x1ejq31n", "xd10rxx", "x1sy0etr", "x17r0tee", "x972fbf", "xcfux6l", "x1qhh985", "xm0m39n", "x9f619", "x1ypdohk", "xt0psk2", "xe8uvvx", "xdj266r", "x11i5rnm", "xat24cr", "x1mh8g0r", "xexx8yu", "x4uap5", "x18d9i69", "xkhd6sd", "x16tdsg8", "x1hl2dhg", "xggy1nq", "x1a2a7pz", "x1heor9g", "xt0b8zv", "xo1l8bm"]
    classes_a_for_url = "x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1q0g3np x87ps6o x1lku1pv x1a2a7pz x1lliihq x1pdlv7q".split()

    collected_data = []

    # --------------- V1 - more than 1 image ---------------
    for feed_div in feed_divs:
        found_divs = feed_div.find_all('div', class_=lambda class_: class_ and all(c in class_.split() for c in initial_classes))

        for div in found_divs:
            text = ""
            nested_div_1 = div.find('div', class_=lambda class_: class_ and all(c in class_.split() for c in nested_classes_for_text))
            if nested_div_1 and nested_div_1.text:
                text = nested_div_1.text

            # Find images with all classes in nested_classes_for_images
            nested_imgs = div.find_all('img', class_=lambda class_: class_ and all(c in class_.split() for c in nested_classes_for_images))

            # Find images with all classes in alternate_classes_for_images
            alternate_imgs = div.find_all('img', class_=lambda class_: class_ and all(c in class_.split() for c in alternate_classes_for_images))

            # Combine the results
            nested_imgs.extend(alternate_imgs)


            for img in nested_imgs:
                if img and img.get('src'):
                    entry = {'image': img['src']}
                    if text:
                        entry['text'] = text

                    nested_a_video = div.find('a', class_=lambda class_: class_ and all(c in class_.split() for c in nested_a_classes_for_videos))
                    if nested_a_video and nested_a_video.get('href'):
                        entry['video'] = nested_a_video['href']

                    url_a_tag = div.find('a', class_=lambda class_: class_ and all(c in class_.split() for c in classes_a_for_url))
                   
                    if url_a_tag:
                        entry['url'] = url_a_tag['href']

                    collected_data.append(entry)
                    
    # ---- PRINT COLLECTED DATA ----
    # with open('collected_data.txt', 'w') as file:
    #     for item in collected_data:
    #         file.write(f"{item}\n")

    response, status_code = process_json({"arr": collected_data})
    print(response)
    return response, status_code





