import schedule
from time import sleep
import requests
import json
from datetime import datetime
from pymongo import MongoClient

# mongodb setup
client = MongoClient('mongodb+srv://pablodm:evaLARAmon1!@cluster0.qzcor.mongodb.net')
db=client.siot_weather
col = db["owm_data"]

# api setup
api_key = "ef399883830e2112b32db2de8f084e42"
lat = "51.49172012646749"
lon = "-0.1953124719660753"
url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)

print("running")
def check_and_publish():
    # get data from the api
    response = requests.get(url)
    print(response)

    # format data as json
    data = json.loads(response.text)

    # create variable for each data field
    c_time = datetime.utcfromtimestamp(data["current"]["dt"])
    c_temp            = data["current"]["temp"]
    c_feels           = data["current"]["feels_like"]
    c_pressure        = data["current"]["pressure"]
    c_humidity        = data["current"]["humidity"]
    c_clouds          = data["current"]["clouds"]
    c_wind_speed      = data["current"]["wind_speed"]
    c_weather_main    = data["current"]["weather"][0]["main"]
    c_weather_desc    = data["current"]["weather"][0]["description"]
    p_time = datetime.utcfromtimestamp(data["hourly"][-1]["dt"])
    p_temp            = data["hourly"][-1]["temp"]
    p_feels           = data["hourly"][-1]["feels_like"]
    p_pressure        = data["hourly"][-1]["pressure"]
    p_humidity        = data["hourly"][-1]["humidity"]
    p_clouds          = data["hourly"][-1]["clouds"]
    p_wind_speed      = data["hourly"][-1]["wind_speed"]
    p_weather_main    = data["hourly"][-1]["weather"][0]["main"]
    p_weather_desc    = data["hourly"][-1]["weather"][0]["description"]
    
    # create dictionary with all the data
    sample = {
        "c_time": c_time, 
        "c_temp": c_temp, 
        "c_feels": c_feels, 
        "c_pressure": c_pressure, 
        "c_humidity": c_humidity, 
        "c_clouds": c_clouds, 
        "c_wind_speed": c_wind_speed, 
        "c_weather_main": c_weather_main, 
        "c_weather_desc": c_weather_desc, 
        "p_time": p_time, 
        "p_temp": p_temp, 
        "p_feels": p_feels, 
        "p_pressure": p_pressure, 
        "p_humidity": p_humidity, 
        "p_clouds": p_clouds, 
        "p_wind_speed": p_wind_speed, 
        "p_weather_main": p_weather_main, 
        "p_weather_desc": p_weather_desc
        }
    print(sample)

    # publish to mongodb
    pub = col.insert_one(sample)

    return sample

# run every hour on the dot
schedule.every().hour.at(":00").do(check_and_publish)
while True:
    schedule.run_pending()
    sleep(30) # nyquist frequency