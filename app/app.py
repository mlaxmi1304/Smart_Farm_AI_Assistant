# Inside folder, run this using: 
# python app.py


from flask import Flask, render_template,  request
import numpy as np
import pickle
import os
import requests
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from plant_doctor import get_plant_advice

app = Flask(__name__)

# Load the Random Forest model for crop recommendation
with open('model/RandomForest.pkl', 'rb') as model_file:
    crop_model = pickle.load(model_file)

# Load the CNN model for plant disease prediction
plant_disease_model = load_model('model/trained_plant_disease_model.keras')

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = os.getenv("WEATHER_API_KEY")
    base_url = "https://api.openweathermap.org/data/2.5/weather?" 

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None

@ app.route('/crop')
def crop():
    title = 'Crop Recommendation'
    return render_template('crop.html', title=title)

#render crop recommendation page
@ app.route('/crop_result', methods=['POST','GET'])
def crop_result():
    title = 'Crop Recommendation'

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # state = request.form.get("stt")
        city = request.form.get("city")

        if weather_fetch(city) != None:
            temperature, humidity = weather_fetch(city)
            data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            my_prediction = crop_model.predict(data)
            final_prediction = my_prediction[0]

            return render_template('crop_result.html', prediction=final_prediction, title=title)

        else:

            return render_template('try_again.html', title=title)


# Plant Disease Prediction Page
@app.route('/plant', methods=['GET', 'POST'])
def plant():
    if request.method == 'POST':
        try:
            file = request.files['file']
            if file:
                upload_folder = 'static/uploads'
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                upload_path = os.path.join(upload_folder, file.filename)
                file.save(upload_path)

                img = image.load_img(upload_path, target_size=(128, 128))
                img_array = image.img_to_array(img)
                img_array = np.expand_dims(img_array, axis=0)
                img_array = img_array / 255.0

                prediction = plant_disease_model.predict(img_array)
                predicted_index = np.argmax(prediction)

                # Full class labels from PlantVillage dataset
                class_labels = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
                                'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
                                'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
                                'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot',
                                'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
                                'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
                                'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight',
                                'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
                                'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
                                'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight',
                                'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot',
                                'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
                                'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy']

                predicted_label = class_labels[predicted_index] if predicted_index < len(class_labels) else 'Unknown Disease'
                predicted_label = predicted_label.replace("__", " ").title()
                
                 # NEW PART (AI Plant Doctor)
                advice = get_plant_advice(predicted_label)

                return render_template(
                    'plant_result2.html',
                    prediction=predicted_label,
                    advice=advice   
                )

                # OLD: return render_template('plant_result.html', prediction=predicted_label)
        except Exception as e:
            print("Error in plant disease prediction:", e)
            return render_template('try_again.html')

    return render_template('plant.html')

# Retry Page
@app.route('/try_again')
def try_again():
    return render_template('try_again.html')

if __name__ == '__main__':
    app.run(debug=True)
