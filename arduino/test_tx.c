#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(9, 10);
int radio_retries = 5;
int radio_delay = 10;

const uint64_t pipes[3] = { 0xAABBCCDD44LL, 0xAABBCCDD44LL, 0xAABBCCDD55LL };
byte data1[32] {48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,10};
byte data2[32] {49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49};
byte data3[32] {50,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49};
byte data4[32] {51,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49,49};
byte data5[10] {52,50,50,50,50,50,50,50,50,10};

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
  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1, pipes[2]);
  radio.startListening();
}

void loop() {
  if (send()) {
    recive();
  }
  
  delay(3000);
}

boolean send() {
  if (!sendWithACK(data1, sizeof(data1))) {
    Serial.println("fail data1");
    return false;
  } else {
    Serial.println("ok data1");
  }
  // if (!sendWithACK(data2, sizeof(data2))) {
  //   Serial.println("fail data2");
  //   return false;
  // } else {
  //   Serial.println("ok data2");
  // }
  // if (!sendWithACK(data3, sizeof(data3))) {
  //   Serial.println("fail data3");
  //   return false;
  // } else {
  //   Serial.println("ok data3");
  // }
  // if (!sendWithACK(data4, sizeof(data4))) {
  //   Serial.println("fail data4");
  //   return false;
  // } else {
  //   Serial.println("ok data4");
  // }
  // if (!sendWithACK(data5, sizeof(data5))) {
  //   Serial.println("fail data5");
  //   return false;
  // } else {
  //   Serial.println("ok data5");
  // }
  return true;
}

void recive() {
  byte income_pipe;
  byte response[32];
  boolean ended = false;
  unsigned long started_at = millis();
  byte package = 48;
  int recive_limit = 500;

  Serial.println("wait for resp");

  while (millis() - started_at <= recive_limit) {
    // Serial.println("o");
    if (radio.available(&income_pipe)) {
      if (income_pipe == 1) {
        radio.read(&response, sizeof(response));

        if (response[0] == 6) {
          continue;
        }

        sendACK();

        if (response[0] == package) {
          started_at = millis();
          package++;

          for (int i = 0; i < sizeof(response); i++) {
            Serial.write(response[i]);
            if (response[i] == 10) {
              ended = true;
              recive_limit = 20;
              break;
            }
          }
        } else {
          Serial.println("same package");
        }
      }
    }
  }

  if (ended){
    Serial.println("it is ok");

  } else {
    Serial.println("RADIO RESPONCE TIMEOUT");
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
