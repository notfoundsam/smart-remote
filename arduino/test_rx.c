#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(9, 10);
int radio_retries = 5;
int radio_delay = 10;

const uint64_t pipes[3] = { 0xAABBCCDD44LL, 0xAABBCCDD44LL, 0xAABBCCDD55LL };
byte data3[10] {48,95,50,50,50,50,50,50,50,10};

void setup() {
  Serial.begin(9600);
  // Serial.setTimeout(50);
  radio.begin();
  delay(100);
  radio.powerUp();
  // radio.setAutoAck(false);
  radio.setAutoAck(false);
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
  byte data[32];
  boolean ended = false;
  unsigned long started_at = millis();
  byte package = 48;

  while (millis() - started_at <= radio_retries * radio_delay) {
    if (radio.available()) {
      radio.read(&data, sizeof(data));

      if (data[0] == 6) {
        continue;
      }

      sendACK();

      if (data[0] == package) {
        started_at = millis();
        package++;

        for (int i = 0; i < sizeof(data); i++) {
          Serial.write(data[i]);
          if (data[i] == 10) {
            ended = true;
            break;
          }
        }
        Serial.write(10);
      } else {
        Serial.println("same package");
      }
    }
  }

  if (ended){
    Serial.println("try to send back");
    if (!sendWithACK(data3, sizeof(data3))) {
      Serial.println("fail data3");
    }
  } else {
    Serial.println("oops");
  }
}

boolean sendWithACK(byte * data, int size) {
  byte income_pipe;
  byte response[32];
  unsigned long ack_started_at;

  for (int i = 0; i <= radio_retries; i++) {
    radio.stopListening();
    radio.write(data, size);
    radio.startListening();

    ack_started_at = millis();
    // Wait 15ms for responce
    while (millis() - ack_started_at <= 15) {
      if (radio.available(&income_pipe)) {
        if (income_pipe == 1) {
          radio.read(&response, sizeof(response));

          if (response[0] == 6) {
            return true;
          } else {
            continue;
          }
        }
      }
    }
  }

  return false;
}

void sendACK() {
  byte one[1] = {6};
  radio.stopListening();
  radio.write(one, sizeof(one));
  radio.startListening();
}
