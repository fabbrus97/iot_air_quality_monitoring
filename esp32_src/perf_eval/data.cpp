#include "data.h"

int TIME_WINDOW[] = {-1, -1, -1, -1, -1};
int TW_POS = 0;

DHT dht(DHTPIN, DHTTYPE);

WiFiUDP udp;

Coap coap(udp);

HTTPClient http;

void get_data(){
  float hum = dht.readHumidity();
  float temp = dht.readTemperature();
  int mq2 = analogRead(34), aqi = -1; //value between 0 - 4095
  
  
  TIME_WINDOW[(TW_POS++)%5] = mq2;
  
  
  if (TW_POS > 4){
    TW_POS = TW_POS == 10 ? 5 : TW_POS ; //avoid overflow
    float avg = 0;
    for (int i = 0; i < 5; i++) avg += TIME_WINDOW[i]; avg /= 5;
    
    aqi = avg >= MAX_GAS_VALUE ? 0 : 2;
    aqi = avg < MAX_GAS_VALUE && avg >= MIN_GAS_VALUE ? 1 : aqi;
    
    
    
  }

  int ret = snprintf(DATA2SEND.temperature, 64, "%f", temp);
  ret = snprintf(DATA2SEND.humidity, 64, "%f", hum);
  ret = snprintf(DATA2SEND.AQI, 32, "%i", aqi); 
  ret = snprintf(DATA2SEND.gas_conc, 32, "%i", mq2);
  ret = snprintf(DATA2SEND.RSSI, 32, "%i", WiFi.RSSI());
  
}

void send_data(){
  
  if (PROTOCOL==COAP){
      char tagged_data[50];
      //"tag" the data with gps and device id
      snprintf(tagged_data, 50, "%s;%s;%s", DATA2SEND.temperature, DATA2SEND.gps, DATA2SEND.device_id);
      unsigned long time_start = millis();
      int msgid = coap.put(IPAddress(COAP_SERVER_IP[0], COAP_SERVER_IP[1], 
                  COAP_SERVER_IP[2], COAP_SERVER_IP[3]),
                  COAP_PORT, "env/temp", tagged_data);
      Serial.print("S, "); Serial.print(msgid); Serial.print(", "); Serial.println(time_start);
      
      /*snprintf(tagged_data, 50, "%s;%s;%s", DATA2SEND.humidity, DATA2SEND.gps, DATA2SEND.device_id);
      msgid = coap.put(IPAddress(COAP_SERVER_IP[0], COAP_SERVER_IP[1], 
                  COAP_SERVER_IP[2], COAP_SERVER_IP[3]),
                  COAP_PORT, "env/hum", tagged_data);
      snprintf(tagged_data, 50, "%s;%s;%s", DATA2SEND.AQI, DATA2SEND.gps, DATA2SEND.device_id);
      msgid = coap.put(IPAddress(COAP_SERVER_IP[0], COAP_SERVER_IP[1], 
                  COAP_SERVER_IP[2], COAP_SERVER_IP[3]),
                  COAP_PORT, "env/aqi", tagged_data);
      snprintf(tagged_data, 50, "%s;%s;%s", DATA2SEND.gas_conc, DATA2SEND.gps, DATA2SEND.device_id);
      msgid = coap.put(IPAddress(COAP_SERVER_IP[0], COAP_SERVER_IP[1], 
                  COAP_SERVER_IP[2], COAP_SERVER_IP[3]),
                  COAP_PORT, "env/gas_conc", tagged_data);
      snprintf(tagged_data, 50, "%s;%s;%s", DATA2SEND.RSSI, DATA2SEND.gps, DATA2SEND.device_id);
      msgid = coap.put(IPAddress(COAP_SERVER_IP[0], COAP_SERVER_IP[1], 
                  COAP_SERVER_IP[2], COAP_SERVER_IP[3]),
                  COAP_PORT, "data/rssi", tagged_data);
      */
  } else {
      
      
      
      char postData[150];   
      /* int ret = snprintf(postData, 150, "{\"temp\":%s,\"hum\":%s,\"AQI\":%s,\"gas\":%s,\"rssi\":%s,\"gps\":\"%s\",\"ts\":\"%s\",\"id\":\"%s\"}",
        DATA2SEND.temperature, DATA2SEND.humidity, DATA2SEND.AQI, DATA2SEND.gas_conc, DATA2SEND.RSSI,
        DATA2SEND.gps, capture_hour, DATA2SEND.device_id);
      */
      int ret = snprintf(postData, 150, "{\"temp\":%s,\"hum\":%s,\"AQI\":%s,\"gas\":%s,\"rssi\":%s,\"gps\":\"%s\",\"id\":\"%s\"}",
        DATA2SEND.temperature, DATA2SEND.humidity, DATA2SEND.AQI, DATA2SEND.gas_conc, DATA2SEND.RSSI,
        DATA2SEND.gps, DATA2SEND.device_id);
      
      long _start = millis();
      http.begin(HTTP_SERVER);
      //http.begin("http://192.168.1.18:8080/data");
      int statusCode = http.POST(postData);
      long _stop = millis();
      Serial.print(statusCode); Serial.print(","); Serial.println(_stop - _start);
      http.end();

     
      
  }
  
}
