#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(9, 10);
int radio_retries = 5;
int radio_delay = 10;

const uint64_t pipes[3] = { 0xAABBCCDD44LL, 0xAABBCCDD44LL, 0xAABBCCDD55LL };
byte data1[32] {48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48};
byte data2[32] {49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49};
byte data3[10] {50,50,50,50,50,50,50,50,50,50};

void setup() {
  Serial.begin(9600);
  // Serial.setTimeout(50);
  radio.begin();
  delay(100);
  radio.powerUp();
  // radio.setAutoAck(false);
  radio.setAutoAck(true);
  radio.setChannel(90);
  radio.setRetries(15,15);
  radio.setPayloadSize(32);
  radio.setCRCLength(RF24_CRC_8);
  radio.setDataRate(RF24_1MBPS);     // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);       // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.openWritingPipe(pipes[2]);
  radio.openReadingPipe(1, pipes[0]);
  radio.startListening();
}

void loop() {
  if (radio.available()) {
    listen();
  }
}

void listen() {
  byte code[32];
  boolean isData = false;
  unsigned long started_at = millis();

  while (millis() - started_at < 1500) {
    if (radio.available()) {
      radio.read(&code, sizeof(code));
      radio.stopListening();
      radio.startListening();

      for (int i = 0; i < sizeof(code); i++) {
        Serial.write(code[i]);
      }
      Serial.write(10);
      started_at = millis();
      isData = true;
    }
  }

  if (isData){
    radio.flush_rx();
    radio.flush_tx();
    delay(2000);
    Serial.println("try to send back");
    radio.openWritingPipe(pipes[0]);
    radio.openReadingPipe(1,pipes[2]);
    radio.stopListening();
    delay(100);
    if (!radio.write(data3, sizeof(data3))) {
      Serial.println("fail data3");
    }
    radio.openWritingPipe(pipes[2]);
    radio.openReadingPipe(1,pipes[0]);
    radio.startListening();
  }
}
