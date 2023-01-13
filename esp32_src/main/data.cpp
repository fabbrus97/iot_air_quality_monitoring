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
  Serial.print("GAS: "); Serial.println(mq2);
  Serial.print("DEBUG: TW_POS vale "); Serial.println(TW_POS);
  TIME_WINDOW[(TW_POS++)%5] = mq2;
  Serial.print("DEBUG: TW_POS adesso vale "); Serial.println(TW_POS);
  
  if (TW_POS > 4){
    TW_POS = TW_POS == 10 ? 5 : TW_POS ; //avoid overflow
    float avg = 0;
    for (int i = 0; i < 5; i++) avg += TIME_WINDOW[i]; avg /= 5;
    Serial.print("Avg: "); Serial.println(avg);
    aqi = avg >= MAX_GAS_VALUE ? 0 : 2;
    aqi = avg < MAX_GAS_VALUE && avg >= MIN_GAS_VALUE ? 1 : aqi;
    Serial.print("MIN GAS: "); Serial.println(MIN_GAS_VALUE);
    Serial.print("MAX GAS: "); Serial.println(MAX_GAS_VALUE);
    Serial.print("Aqi: "); Serial.println(aqi);
  }

  int ret = snprintf(DATA2SEND.temperature, 64, "%f", temp);
  ret = snprintf(DATA2SEND.humidity, 64, "%f", hum);
  ret = snprintf(DATA2SEND.AQI, 32, "%i", aqi); 
  ret = snprintf(DATA2SEND.gas_conc, 32, "%i", mq2);
  ret = snprintf(DATA2SEND.RSSI, 32, "%i", WiFi.RSSI());
  
}

void send_data(){
  /*struct tm tm; char capture_hour[28]; 
  if(!getLocalTime(&tm)){
    Serial.println("Failed to obtain time 1");
    return;
  }
  else {
    //2018-03-28T8:01:00Z
    int ret = snprintf(capture_hour, 28, 
        "%i-%i-%iT%i:%i:%iZ+01:00", 
        (tm.tm_year + 1900), (tm.tm_mon+1), tm.tm_mday, 
        tm.tm_hour, tm.tm_min, tm.tm_sec);
  }

  Serial.print("L'ora registrata è:");
  Serial.println(capture_hour);*/
  
  if (PROTOCOL==COAP){
      char tagged_data[50];
      //"tag" the data with gps and device id
      snprintf(tagged_data, 50, "%s;%s;%s", DATA2SEND.temperature, DATA2SEND.gps, DATA2SEND.device_id);
      int msgid = coap.put(IPAddress(COAP_SERVER_IP[0], COAP_SERVER_IP[1], 
                  COAP_SERVER_IP[2], COAP_SERVER_IP[3]),
                  COAP_PORT, "env/temp", tagged_data);
      snprintf(tagged_data, 50, "%s;%s;%s", DATA2SEND.humidity, DATA2SEND.gps, DATA2SEND.device_id);
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
      
  } else {
      Serial.println("Protocol: http");
      Serial.print("Temperature: ");
      Serial.println(DATA2SEND.temperature);
      char postData[150];   
      /* int ret = snprintf(postData, 150, "{\"temp\":%s,\"hum\":%s,\"AQI\":%s,\"gas\":%s,\"rssi\":%s,\"gps\":\"%s\",\"ts\":\"%s\",\"id\":\"%s\"}",
        DATA2SEND.temperature, DATA2SEND.humidity, DATA2SEND.AQI, DATA2SEND.gas_conc, DATA2SEND.RSSI,
        DATA2SEND.gps, capture_hour, DATA2SEND.device_id);
      */
      int ret = snprintf(postData, 150, "{\"temp\":%s,\"hum\":%s,\"AQI\":%s,\"gas\":%s,\"rssi\":%s,\"gps\":\"%s\",\"id\":\"%s\"}",
        DATA2SEND.temperature, DATA2SEND.humidity, DATA2SEND.AQI, DATA2SEND.gas_conc, DATA2SEND.RSSI,
        DATA2SEND.gps, DATA2SEND.device_id);
      Serial.print("DEBUG ho scritto "); Serial.print(ret); Serial.println(" bytes");
      Serial.print("DEBUG invio: "); Serial.println(postData);

      Serial.println("Sending post request...");
      http.begin("http://192.168.43.6:8080/data");
      //http.begin("http://192.168.1.17:8080/data");
      http.POST(postData);
      Serial.println("post done");
      // read the status code and body of the response
      /*int statusCode = client.responseStatusCode();
      String response = client.responseBody();
      Serial.print("Status code: ");
      Serial.println(statusCode);*/
  }
  
}
