#include "main.h"

const char* SSID = "xxx";
const char* PASS = "xxx";
/* --------------------------------------------- */


// CoAP server endpoint url callback
void coap_change_settings(CoapPacket &packet, IPAddress ip, int port) {
  

  set(packet, ip, port);

  coap.sendResponse(ip, port, packet.messageid, "ok");
  //coap.sendResponse(ip, port, packet.messageid, p);
  
}


// CoAP client response callback
void callback_response(CoapPacket &packet, IPAddress ip, int port) {
  
  
  char p[packet.payloadlen + 1];
  memcpy(p, packet.payload, packet.payloadlen);
  p[packet.payloadlen] = NULL;
  unsigned long time_stop = millis();
  Serial.print("R, "); Serial.print(packet.messageid); Serial.print(", "); Serial.println(time_stop);
  /*if (packet.payloadlen){
    
    
  }*/
}

void connect() {
  WiFi.begin(SSID, PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  } 

}

TaskHandle_t CoapTask;

void CoapTaskCode(void * parameter){
  coap.start();
  for(;;) {
    coap.loop();
    delay(500);
  }
}

void setup() {
  
  Serial.begin(9600);  

  connect();

  /*
  //set time
  configTime(0, 0, "pool.ntp.org");
  setenv("TZ","CET-1CEST,M3.5.0,M10.5.0/3",1);  tzset(); //set timezone
  */

  dht.begin();
  
  coap.server(coap_change_settings, "set");
  
  coap.response(callback_response);

  xTaskCreatePinnedToCore(
      CoapTaskCode, /* Function to implement the task */
      "TaskCoap", /* Name of the task */
      10000,  /* Stack size in words */
      NULL,  /* Task input parameter */
      0,  /* Priority of the task */
      &CoapTask,  /* Task handle. */
      0); /* Core where the task should run */

}

int packet_counter = 1500;

void loop() {

  
  if (packet_counter == 0){
    Serial.println("done");
    delay(60000);
  } else {
    get_data();
    if (TIME_WINDOW[4] >= 0){
      
      send_data();
      packet_counter--;
    }
  }
  //delay(SAMPLE_FREQUENCY);
  delay(1000);



}
