#include <DHT.h>
#include <IRremote.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
IRsend irsend;
RF24 radio(9, 10); // For nano pin 9 and 10
int radioSpeedPin = 2;
int radioChannelPin1 = 3;
int radioChannelPin2 = 4;
#define DHTTYPE DHT11 // DHT 11
const byte dht_pin = 8;
DHT dht(dht_pin, DHTTYPE);

// Radio Address
uint64_t address = 0xAABBCCDD33LL;
unsigned char khz = 38;

unsigned int code;
unsigned long started_waiting_at;               // Set up a timeout period, get the current microseconds
boolean timeout;


byte radioSpeedState = 0; // 0 is RF24_250KBPS and 1 is RF24_1MBPS

void setup() {
  pinMode(radioSpeedPin, INPUT);
  Serial.begin(9600);
  radio.begin();
  delay(1000);
  radio.powerUp();
  radio.setChannel(75);                 // (0 - 127)
  radio.setRetries(15,15);
  radio.setDataRate(RF24_250KBPS);      // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);        // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.setAutoAck(1);
  radio.openReadingPipe(1, address);
  radio.startListening();
}

void loop() {
  checkRadioSetting();

  float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (isnan(t) || isnan(h)) {
        Serial.println("Failed to read from DHT");
    } else {
        Serial.print("Humidity: "); 
        Serial.print(h);
        Serial.print(" %\t");
        Serial.print("Temperature: "); 
        Serial.print(t);
        Serial.println(" *C");
    }
  
  if (radio.available()) {
    
    radio.read(&code, sizeof(code));
    
    if (code == 105) {
      // Recived IR signal (starts with i)
      readIrSignal();
    } else if (code == 99) {
      // Recived command (starts with i)
      readCommand();
      Serial.println("comm");
    }
  }
}

void readIrSignal() {
  // buffer with 800 elements doesn't work
  unsigned int irSignal[700];
  unsigned int index = 0;
  unsigned int signal;
  started_waiting_at = micros();
  timeout = true;

  while (timeout == true && (micros() - started_waiting_at < 200000)) {
    if (radio.available()) {
      started_waiting_at = micros();
      radio.read(&signal, sizeof(signal));
      Serial.println(signal);

      if (signal == 10) {
        irsend.sendRaw(irSignal, index, khz);
        Serial.println("signal sent");
        return;
      } else {
        irSignal[index] = signal;
        index++;
      }
    }
  }
}

void readCommand() {
  char command[20] = {0};
  unsigned int index = 0;
  unsigned int signal;
  started_waiting_at = micros();
  timeout = true;

  while (timeout == true && (micros() - started_waiting_at < 200000)) {
    if (radio.available()) {
      started_waiting_at = micros();
      radio.read(&signal, sizeof(signal));

      if (signal == 10) {
        Serial.println(command);
        return;
      } else {
        Serial.println(signal);
        command[index] = signal;
        index++;
      }
    }
  }
}

void checkRadioSetting() {
  byte currentSpeed = 0;

  if (digitalRead(radioSpeedPin) == HIGH) {
    currentSpeed = 1;
  }

  if (radioSpeedState != currentSpeed)
  {
    if (currentSpeed == 0) {
      radioSpeedState = 0;
      Serial.println("RF24_250KBPS");
      radio.setDataRate(RF24_250KBPS);
    } else {
      radioSpeedState = 1;
      Serial.println("RF24_1MBPS");
      radio.setDataRate(RF24_1MBPS);
    }
  }
}
