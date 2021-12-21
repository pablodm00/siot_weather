#include "DHT.h"
#include <Adafruit_Sensor.h>
#include "WiFi.h"
#include "time.h"
#include <NTPClient.h>
#include <ESP32Time.h>
ESP32Time rtc;

// define the pins for the sensors
#define DHTPIN 4       // digital pin for the temperature and humidity sensor
#define DHTTYPE DHT11  // specifying dht11 sensor type
#define rainAnalog 15  // analog pin for the rain sensor
#define ONBOARD_LED  2 // pin for the onboard led

DHT dht(DHTPIN, DHTTYPE);

// set up ntpclient
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP);

void setup() {
  pinMode(ONBOARD_LED,OUTPUT);
  Serial.begin(9600);
  dht.begin();
}

// read the sensors and print to serial monitor
int read_print(){
  // read humidity
  float h = dht.readHumidity();
  // read temperature (C)
  float t = dht.readTemperature();
  // read rain sensor
  int rain = analogRead(rainAnalog);

  // Compute heat index in Celsius
  float hic = dht.computeHeatIndex(t, h, false);

  // print readings to the serial monitor
  Serial.print(t);
  Serial.print(",");
  Serial.print(h);
  Serial.print(",");
  Serial.print(hic);
  Serial.print(",");
  Serial.println(rain);
}

// connect to wifi network
void connect_wifi(){
  const char* ssid     = "WTH 307-308";
  const char* password = <wifi password>; // wifi password censored
  // Serial.print("Connecting to ");
  // Serial.println(ssid);
  WiFi.begin(ssid, password);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    // Serial.print("attempt number ");
    // Serial.println(attempts);
    attempts = attempts+1;
    delay(500);
    if (attempts >= 15) { // number of attempts capped at 10
      // Serial.print("Could not connect to ");
      // Serial.println(ssid);
      break;
    }
  }
  // Serial.println(WiFi.status());
  if (WiFi.status() != WL_CONNECTED) { // if cannot connect to that wifi, try the other one
    int attempts = 0;
    const char* ssid = "WTH 304-306"; // wifi password is the same as for the other network
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      // Serial.print("attempt number ");
      // Serial.println(attempts);
      attempts = attempts+1;
      delay(500);
      if (attempts >= 15) {
        // Serial.print("Could not connect to ");
        // Serial.println(ssid);
        break; // if cannot connect to either, give up
      }
    }
  }
}

// get the minute reading: if available, from the rtc server (and update local clock). if not, from the local clock
int get_minute(){
  timeClient.begin();
  timeClient.setTimeOffset(0); // set timezone (in s)
  int c_attempts = 0;
  while(!timeClient.update()) {
    c_attempts = c_attempts+1;
    timeClient.forceUpdate(); // sometimes, the first sync needs to be forced due to the big difference with the epoch
    // Serial.print("a");
    if (c_attempts >= 10) {
      break; // try up to 10 times (will only happen when wifi unavailable)
    }
  }
  
  if(!timeClient.getMinutes()){ // if this is unavailable, get reading from local clock
    // Serial.println("Failed to obtain time");
    return rtc.getMinute();
  }

  rtc.setTime(timeClient.getEpochTime()); // update local time from ntp server
  return timeClient.getMinutes(); // get minute from ntp server
}

void loop() {  
  // wait a few seconds between measurements
  delay(30000); // nyquist frequency
  
  // connect to wifi
  connect_wifi();

  // get current minute
  int minute = get_minute();
  
  //disconnect WiFi as it is no longer needed
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);

  static byte lastMinute = 0;

  if(minute == lastMinute){
    return; // if minute is same as the previous one, dont bother continuing
  }
  
  lastMinute = minute;   // remember what minute was last time we looked

  // minute has changed
  if( minute == 00 || minute == 20 || minute == 40 ){ // if minute is one of the ones we want to sample at
    read_print(); // read sensor data and print it to the serial monitor
  }
}
