import serial
from pymongo import MongoClient
import datetime as dt
from time import sleep
import schedule

# set up connection with mongodb
client = MongoClient('mongodb+srv://pablodm:<password>@cluster0.qzcor.mongodb.net') # password censored
db=client.siot_weather
col = db["esp_data"]

# set up connection with serial monitor
arduino_port = "COM4" #s erial port of Arduino
baud = 9600 # esp32 running at 9600 baud
ser = serial.Serial(arduino_port, baud)
print("Connected to Arduino port:" + arduino_port)

def read_and_publish():
    time_stamp = dt.datetime.now() # get time
    data=str(ser.readline()) # read serial monitor
    data=data[2:-5] # delete unneeded characters

    # format data appropriately
    sample = {
        'datetime' : time_stamp,
        'temp' :    float(data.split(",")[0]),
        'hum' :     float(data.split(",")[1]),
        'heat_i' :  float(data.split(",")[2]),
        'rain' :    float(data.split(",")[3]),
    }
    
    # publish to mongodb
    pub = col.insert_one(sample)
    print(sample)

# do read_and_publish() every hour at minutes 01, 21 and 41 (1 minute after the values are printed to the serial monitor)
schedule.every().hour.at(":01").do(read_and_publish) 
schedule.every().hour.at(":21").do(read_and_publish)
schedule.every().hour.at(":41").do(read_and_publish)
while True:
    schedule.run_pending()
    sleep(30) # nyquist frequency 