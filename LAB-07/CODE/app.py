import os
import requests
from flask import Flask, render_template, request, jsonify, flash

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'earth-theme-secret')

# Configuration - Replace with your actual API key
API_KEY = os.environ.get('OPENWEATHER_API_KEY', 'c7f8a54be442d2ce457076f410730800')
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# In-memory history
history = []

class WeatherService:
    @staticmethod
    def get_icon_url(code):
        return f"https://openweathermap.org/img/wn/{code}@4x.png"

    @classmethod
    def fetch(cls, city):
        try:
            params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
            response = requests.get(BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            weather_main = data['weather'][0]
            
            # EXTRACTING MORE DATA AS REQUESTED
            result = {
                "city": data.get("name"),
                "type": weather_main.get("main"), # e.g., Rain, Clouds, Clear
                "desc": weather_main.get("description").capitalize(),
                "temp": round(data.get("main", {}).get("temp")),
                "feels_like": round(data.get("main", {}).get("feels_like")),
                "humidity": data.get("main", {}).get("humidity"),
                "pressure": data.get("main", {}).get("pressure"), # Atmospheric pressure
                "wind": data.get("wind", {}).get("speed"),
                "icon": cls.get_icon_url(weather_main.get("icon"))
            }
            
            entry = f"{result['city']} - {result['type']} ({result['temp']}°C)"
            if entry not in history:
                history.insert(0, entry)
            
            return result, None
        except Exception:
            return None, "Location not found or API error."

@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    if request.method == 'POST':
        city = request.form.get('city', '').strip()
        if not city:
            flash("Please enter a location", "warning")
        else:
            weather, error = WeatherService.fetch(city)
            if error:
                flash(error, "danger")
                
    return render_template('index.html', weather=weather, history=history[:5])

@app.route('/clear', methods=['POST'])
def clear():
    global history
    history = []
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)