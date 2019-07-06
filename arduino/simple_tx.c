#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

boolean isRadioSeted = false;
RF24 radio(9, 10);

int data = 1;

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(50);
  delay(3000);
}

void radioSetup() {
  
  radio.begin();
  delay(100);
  radio.powerUp();
  radio.setChannel(70);

  radio.setAutoAck(false); // Disable hardware ACK, use program ACK

  radio.setPayloadSize(32);
  radio.setCRCLength(RF24_CRC_8);
  radio.setDataRate(RF24_1MBPS);     // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);       // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.openWritingPipe(0xBBBBBBBB11LL);
  radio.openReadingPipe(1, 0xBBBBBBBB22LL);
  radio.startListening();
}

void loop() {
  if (!isRadioSeted) {
    radioSetup();
    isRadioSeted = true;
  }
  radio.stopListening();
  radio.writeFast(&data, sizeof(data));
  radio.txStandBy();
  radio.startListening();
  Serial.println("sent");
  delay(5000);
}
