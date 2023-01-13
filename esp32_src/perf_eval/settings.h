#ifndef SETTINGS_H
#define SETTINGS_H

#include <HardwareSerial.h>
#include <coap-simple.h>

#define COAP 0
#define HTTP 1

extern const int COAP_SERVER_IP[4];
extern const int COAP_PORT;
extern const char* HTTP_SERVER;
extern int SAMPLE_FREQUENCY;
extern int PROTOCOL;
//for gas computations:
extern int MIN_GAS_VALUE;
extern int MAX_GAS_VALUE;

extern void set(CoapPacket &packet, IPAddress ip, int port);

#endif
