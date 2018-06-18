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
  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1, pipes[2]);
  radio.startListening();
}

void loop() {
  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1,pipes[2]);
  radio.stopListening();
  delay(1000);
  send();
  radio.openWritingPipe(pipes[2]);
  radio.openReadingPipe(1,pipes[0]);
  radio.startListening();
  radio.flush_rx();
  radio.flush_tx();
  delay(1000);
  radio.stopListening();
  radio.startListening();
  recive();
  delay(3000);
}

void send() {
  if (!radio.write(data1, sizeof(data1))) {
    fifo();
    Serial.println("fail data1");
    return ;
  }
  fifo();
  delay(1200);
  if (!radio.write(data2, sizeof(data2))) {
    fifo();
    Serial.println("fail data2");
    return ;
  }
  fifo();
  delay(1200);
  if (!radio.writeFast(data3, sizeof(data3))) {
    fifo();
    Serial.println("fail data3");
    return ;
  }
  fifo();
  delay(1200);
}

void recive() {
  byte income_pipe;
  byte signal[32];
  unsigned long responce_started_at = millis();
  boolean timeout = true;

  // Wait 5 seconds for responce
  while (millis() - responce_started_at < 5000) {
    if (radio.available(&income_pipe)) {
      if (income_pipe == 1) {
        radio.read(&signal, sizeof(signal));
        timeout = false;
        break;
      }
    }
  }

  if (!timeout) {
    for (int i = 0; i < sizeof(signal); i++) {
      Serial.write(signal[i]);
    }
    Serial.write(10);
  } else {
    Serial.println("RADIO RESPONCE TIMEOUT");
  }
}

void fifo() {
  if(!radio.txStandBy()){
    Serial.println("fail fifo");
  }
}
