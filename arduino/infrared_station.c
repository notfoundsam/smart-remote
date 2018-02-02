#include <IRremote.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
IRsend irsend;
RF24 radio(9, 10); // For nano pin 9 and 10
byte pipe;
unsigned int irSignal[500];
unsigned char khz = 38;
unsigned short index = 0;
unsigned int code;
unsigned long started_waiting_at;               // Set up a timeout period, get the current microseconds
boolean timeout = false;

void setup() {
  Serial.begin(9600);
  radio.begin();
  delay(1000);
  radio.powerUp();
  radio.setChannel(75);                 // (0 - 127)
  radio.setRetries(15,15);
  radio.setDataRate(RF24_250KBPS);      // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);        // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.setAutoAck(1);
  radio.openReadingPipe(1, 0xAABBCCDD11LL);
  radio.openReadingPipe(2, 0xAABBCCDD22LL);
  radio.startListening();
}

void loop() {
  
  if (radio.available(&pipe)) {
    started_waiting_at = micros();
    timeout = true;
    
    radio.read(&code, sizeof(code));
    // if (pipe == 1) {
    
    // }

    if (code == '\n') {
      irsend.sendRaw(irSignal, index, khz);
      index = 0;
      timeout = false;
      // DEBUG
      Serial.println("signal sent");
    } else {
      irSignal[index] = code;
      index++;
    }
  } else {
    if (timeout == true && (micros() - started_waiting_at > 200000)) {
      index = 0;
      timeout = false;
    }
  }
}

