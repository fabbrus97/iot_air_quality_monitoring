#include "settings.h"

//const int COAP_SERVER_IP[] = {192, 168, 43, 6}; 
const int COAP_SERVER_IP[] = {192, 168, 1, 19}; 
const int COAP_PORT = 5683;
//const char* HTTP_SERVER = "http://192.168.43.6:8080/data";
const char* HTTP_SERVER = "http://192.168.1.19:8080/data";
int SAMPLE_FREQUENCY = 5 * 1000; // seconds - can be changed at runtime
int PROTOCOL = HTTP;
//for gas computations:
int MIN_GAS_VALUE    = 500;  // can be changed at runtime
int MAX_GAS_VALUE    = 1500; // can be changed at runtime

void set(CoapPacket &packet, IPAddress ip, int port){
  // set value
  char p[packet.payloadlen + 1];
  memcpy(p, packet.payload, packet.payloadlen);
  p[packet.payloadlen] = NULL;

  //p[0] is a number (0 - 9)
  if (p[0] >= 48 && p[0] <= 57){ 
    SAMPLE_FREQUENCY = atoi(p);

    
    
    
    
  } else { //p[0] is another character, like 'c'    
    char tmp[packet.payloadlen-1];
    switch(p[0]){
      case 'c': //set coap protocol
        PROTOCOL = COAP;
        break;
      case 'h': //set http protocl
        PROTOCOL = HTTP;
        break;
      case 'x': //set gas max value
        for (int i = 1; i < packet.payloadlen; i++) tmp[i-1] = p[i];
        MAX_GAS_VALUE = atoi(tmp);
        break;
      case 'm': //set gas min value
        for (int i = 1; i < packet.payloadlen; i++) tmp[i-1] = p[i];
        MIN_GAS_VALUE = atoi(tmp);
        break;
      default:
        break;
    }
    if (p[0] == 'c')
      PROTOCOL = COAP;
    else if (p[0] == 'h')
      PROTOCOL = HTTP; 
  }

  //return p;
}
