# IMAGES
from PIL import Image
from io import BytesIO
import requests
import json
from flask import jsonify

# HTML
from bs4 import BeautifulSoup

# GEMINI
import google.generativeai as genai
from google.api_core.exceptions import InternalServerError
from google.generativeai.types.generation_types import BlockedPromptException


# # ------------- IMPORT VIRTUAL VARIABLES -------------
from dotenv import dotenv_values
config = dotenv_values(".env")
GEMINI_KEY = config['GEMINI_KEY']
genai.configure(api_key=GEMINI_KEY)

# ------------- TEXT AND IMAGE ANALYZE - GEMINI -------------
def analyze_data_gemini(dive_text, img):
    print("IN GEMINI")
    json_structure = '{"date": ,"time":, "diveSite": ,"objectGroup":, "specie":, "imageLocation":, "AR":}'
    json_not_usefull = '{"no data": "No usefull data"}'
    json_no_data = '{"no data": "The post is not about diving"}'
    parameters_explanation_before = '''date - date of the dive,
        time - light/night,
        diveSite - site name,
        objectGroup - one of this options (Cephalopods, Artificial Reef, Coral Reef, Divers, Dolphins, Invertebrate, Large Reef Fish, Medium Reef Fish, Small ReefFish, Mollusca and Worms, Rays, Sea Turtles, Sharks, NA),
        specie-the exact animal specie,
        imageLocation-image location choose one of (Artificial Reef, Blue, Coral reef, NA,Patched reef, Sandy Bottom, Sea Grass),
        AR - Yes/NO if there is an artificial reef in the image,
        '''

    parameters_explanation = parameters_explanation_before.replace('\n', ' ')

    promt_instructions = f'return a json file in the next format: {json_structure}, explanation of each parameter: {parameters_explanation}. if some information is missing type "null", if all information is missing return {json_not_usefull}, if the text is not about diving return {json_no_data}. if there is a short text with date or location and an image of marine life, count it as about diving that occured in that time and place and analyze it as explained before.'
    
    print("DIVE TEXT",dive_text)

    try:
        if isinstance(img, Image.Image):
            model = genai.GenerativeModel('gemini-pro-vision')
            response = model.generate_content([f'I am giving you a text and an image about diving, {promt_instructions} the text: {dive_text}', img], stream=True)
            response.resolve()
        else:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(f'I am giving you a text about diving, {promt_instructions} the text: {dive_text}')

        cleaned_text = response.text.replace('```json', '').replace('```', '').strip()

        print('-----------------------------')
        print('CLEANED TEXT: ', cleaned_text)
        print('-----------------------------')

        try:
            json_data = json.loads(cleaned_text)
            return json_data
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e.msg}, at position {e.pos}")
            json_data = json.loads('{"no data": "Some error occured"}')
            return json_data 
        
    except BlockedPromptException as e:
        print(f"promt error: {e.msg}, at position {e.pos}")
        json_data = json.loads('{"no data": "Some error occured"}')
        return json_data 

    except ValueError as e:
        print("VALUE ERROR")
        json_data = json.loads('{"no data": "Some error occured"}')
        return json_data 


# ------------- CONVERT IMAGE URL TO IMAGE FILE -------------
def url_to_image(url):
    response = requests.get(url) 
    if response.status_code == 200:
        img_bytes = BytesIO(response.content)
        img = Image.open(img_bytes).convert('RGB')
        return img
    else:
        raise Exception(f"Failed to fetch image from URL. Status code: {response.status_code}")
   
def process_json(data):
        print("IN PROCESS JSON")
        arr = data.get('arr', [])
        number_of_posts = len(arr)
        successful_posts = 0
        results = []

        if not arr:
            return jsonify({'status': 'error', 'message': 'Data Is Empty'}), 400
        
        elif not isinstance(arr, list):
            return jsonify({'status': 'error', 'message': 'Wrong JSON structure, arr must be an array'}), 400

        for post in arr:
            print('*************************************************')
            print(post)
            print('*************************************************')
 
            text = post.get('text', "")
            image_url = post.get('image', 'No Image')
            img = 'No Image'

            if image_url != 'No Image':
                try:
                    img = url_to_image(image_url)
                except Exception as e:
                    print(f"Error getting image: {e}")

            try:        
                answer = analyze_data_gemini(text, img)
                answer["url"] = post.get('url', 'url not found')
                answer["video"] = post.get('video', 'no video in this post')
                results.append(answer)
                successful_posts += 1
            except Exception as e:
                return jsonify({'status': 'partial_success', 'message': 'Some data fragments were not retrieved due to internal server errors.', 'successfulData': results, 'errors': arr[successful_posts:], 'nextSteps': 'try again in 60 seconds', 'results':successful_posts/number_of_posts}), 206
   
        return jsonify({'status': 'success', 'message': 'Data processed', 'data': results, 'number of posts': successful_posts}), 200

def extract_data_from_HTML(txt):
    print("IN EXTRACT HTML")

    soup = BeautifulSoup(txt, 'html.parser')

    feed_divs = soup.find_all('div', role="feed")

    initial_classes = ["x1yztbdb", "x1n2onr6", "xh8yej3", "x1ja2u2z"]
    nested_classes_for_text = "xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs".split()
    nested_classes_for_images = "x1ey2m1c xds687c x5yr21d x10l6tqk x17qophe x13vifvy xh8yej3 xl1xv1r".split()
    alternate_classes_for_images = "xz74otr x1ey2m1c xds687c x5yr21d x10l6tqk x17qophe x13vifvy xh8yej3".split()
    nested_a_classes_for_videos = "x1i10hfl x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 xe8uvvx x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1n2onr6 x87ps6o x1lku1pv xjbqb8w x76ihet xwmqs3e x112ta8 xxxdfa6 x1ypdohk x1rg5ohu x1qx5ct2 x1k70j0n x1w0mnb xzueoph x1mnrxsn x1iy03kw xexx8yu x4uap5 x18d9i69 xkhd6sd x1o7uuvo x1a2a7pz".split()
    classes_a_for_url = ["x1i10hfl", "xjbqb8w", "x1ejq31n", "xd10rxx", "x1sy0etr", "x17r0tee", "x972fbf", "xcfux6l", "x1qhh985", "xm0m39n", "x9f619", "x1ypdohk", "xt0psk2", "xe8uvvx", "xdj266r", "x11i5rnm", "xat24cr", "x1mh8g0r", "xexx8yu", "x4uap5", "x18d9i69", "xkhd6sd", "x16tdsg8", "x1hl2dhg", "xggy1nq", "x1a2a7pz", "x1heor9g", "xt0b8zv", "xo1l8bm"]

    collected_data = []

    # --------------- V1 - more than 1 image ---------------
    for feed_div in feed_divs:
        found_divs = feed_div.find_all('div', class_=lambda class_: class_ and all(c in class_.split() for c in initial_classes))

        for div in found_divs:
            text = None
            nested_div_1 = div.find('div', class_=lambda class_: class_ and all(c in class_.split() for c in nested_classes_for_text))
            if nested_div_1 and nested_div_1.text:
                text = nested_div_1.text

            nested_imgs = div.find_all('img', class_=lambda class_: class_ and all(c in class_.split() for c in nested_classes_for_images))
            if not nested_imgs:  
                nested_imgs = div.find_all('img', class_=lambda class_: class_ and all(c in class_.split() for c in alternate_classes_for_images))

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

    with open('file.txt', 'w', encoding='utf-8') as file:
        file.write(json.dumps(collected_data, ensure_ascii=False))
            
    response, status_code = process_json({"arr": collected_data})
    # print("COLLECTED DATA:", collected_data)
    print(response)
    return response, status_code


    # V2 - one image per post

    # for feed_div in feed_divs:
        
    #     found_divs = feed_div.find_all('div', class_=lambda class_: class_ and all(c in class_.split() for c in initial_classes))

    #     for div in found_divs:
    #         entry = {}
            
    #         nested_div_1 = div.find('div', class_=lambda class_: class_ and all(c in class_.split() for c in nested_classes_for_text))
    #         if nested_div_1 and nested_div_1.text:
    #             entry['text'] = nested_div_1.text
            
    #         nested_img = div.find('img', class_=lambda class_: class_ and all(c in class_.split() for c in nested_classes_for_images))
    #         if not nested_img:
    #             nested_img = div.find('img', class_=lambda class_: class_ and all(c in class_.split() for c in alternate_classes_for_images))
            
    #         if nested_img and nested_img.get('src'):
    #             entry['image'] = nested_img['src']
            
    #         nested_a_video = div.find('a', class_=lambda class_: class_ and all(c in class_.split() for c in nested_a_classes_for_videos))
    #         if nested_a_video and nested_a_video.get('href'):
    #             entry['video'] = nested_a_video['href']
            
    #         url_a_tag = div.find('a', class_=lambda class_: class_ and all(c in class_.split() for c in classes_a_for_url))

    #         if url_a_tag:
    #             entry['url'] = url_a_tag['href']

    #         if entry:
    #             collected_data.append(entry)

    # response, status_code = process_json({"arr": collected_data})
    # # print("COLLECTED DATA:", collected_data)
    # print(response)
    # return response, status_code

