import os
from dotenv import load_dotenv
from langchain_community.utilities import OpenWeatherMapAPIWrapper

load_dotenv()

api_key = os.getenv("OPENWEATHERMAP_API_KEY")
if not api_key:
    print("Warning: Using development API key. Set OPENWEATHERMAP_API_KEY in environment.")
    api_key = "5b6a77a7f38c40a0ea77a22dd281f69c"  # Fallback for development only

weather = OpenWeatherMapAPIWrapper(openweathermap_api_key=api_key)

weather_data = weather.run("Bhubaneswar,IN")
print(weather_data)