#ifndef DATA_H
#define DATA_H

#include "settings.h"

#include <DHT.h>
#include <WiFiUdp.h>
#include <HTTPClient.h>
//#include <time.h>


#define DHTPIN 4 //temperature/humidity
#define DHTTYPE DHT22 //temperature/humidity sensor
#define MQ2PIN 34

struct {
  char temperature[64];
  char humidity[64];
  char AQI[32];
  char gas_conc[32];
  char RSSI[32];
  const char gps[16] = "44.4948,11.3426"; //bologna's coordinates
  const char device_id[18] = "30:C6:F7:22:83:F4"; //use mac address as device id
} DATA2SEND;

extern DHT dht;
extern WiFiUDP udp;
extern Coap coap;
extern HTTPClient http;

extern int TIME_WINDOW[5];
extern int TW_POS;

extern void get_data();

extern void send_data();

#endif
