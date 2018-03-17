#include <DHT.h>
#include <IRremote.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// Radio setting
RF24 radio(9, 10); // For nano pin 9 and 10
uint64_t address = 0xAABBCCDD33LL;
int radioSpeedPin = 2;
int radioChannelPin1 = 3;
int radioChannelPin2 = 4;
int radio_retries = 20;
int radio_delay = 20;
byte radioSpeedState = 0; // 0 is RF24_250KBPS and 1 is RF24_1MBPS

// IRremote setting
IRsend irsend;
unsigned char khz = 38;

// DHT setting
#define DHTTYPE DHT11 // DHT 11
const byte dht_pin = 8;
DHT dht(dht_pin, DHTTYPE);
unsigned long started_waiting_at_dht = 0;               // Set up a timeout period, get the current microseconds
float hum;
float temp;

// Battery setting
unsigned long started_waiting_at_battery = 0;               // Set up a timeout period, get the current microseconds
int bat_pin = A1;
// float max_v = 4.1;
// float min_v = 2.5;
float Vin = 0;

// Program setting
unsigned int code;
unsigned long started_waiting_at;               // Set up a timeout period, get the current microseconds
boolean timeout;

void setup() {
  analogReference(INTERNAL);
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
  radio.openWritingPipe(address);
  radio.openReadingPipe(1, address);
  radio.startListening();
}

void loop() {
  checkRadioSetting();
  getDhtParams();
  getBatteryVoltage();
  
  if (radio.available()) {
    radio.read(&code, sizeof(code));
    
    if (code == 105) {
      // Recived IR signal (starts with i)
      readIrSignal();
    } else if (code == 99) {
      // Recived command (starts with c)
      readCommand();
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

  while (timeout == true && (micros() - started_waiting_at < 100000)) {
    if (radio.available()) {
      started_waiting_at = micros();
      radio.read(&signal, sizeof(signal));

      if (signal == 10) {
        irsend.sendRaw(irSignal, index, khz);
        Serial.println("signal sent");
        
        delay(30);
        radio.stopListening();

        String responce = "ok";
        int rsize = responce.length();
        
        for (int i = 0; i < rsize; i++) {
          if (responce[i] == 0)
            break;

          if (!sendSignal(responce[i])) {
            return;
          }
        }

        sendSignal(10);
        delay(30);
        radio.startListening();
        
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
        timeout = false;
        break;
      } else {
        command[index] = signal;
        index++;
      }
    }
  }

  if (!timeout) {
    Serial.println(command);

    // This delay is necessary
    delay(30);
    
    if (areEqual(command, "status")) {
      Serial.println("exec status command");
      sendStatus();
    }
    
    delay(30);
    radio.startListening();
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

void getDhtParams() {
  // 10 seconds
  if (started_waiting_at_dht == 0 || micros() - started_waiting_at_dht > 10000000) {
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (!isnan(t) && !isnan(h)) {
      hum = h;
      temp = t;

      started_waiting_at = micros();
    }
  }
}

void getBatteryVoltage() {
  // 20 seconds
  if (started_waiting_at_battery == 0 || micros() - started_waiting_at_battery > 20000000) {
    Vin = (analogRead(bat_pin) * 1.1) / 1023;
    started_waiting_at_battery = micros();
  }
}

void sendStatus() {
  // Add DHT params
  String responce = "hum ";
  responce += hum;
  responce += "temp ";
  responce += temp;

  // Add Battery voltage
  responce += ",bat ";
  responce += Vin;

  int rsize = responce.length();

  radio.stopListening();

  for (int i = 0; i < rsize; i++) {
    if (responce[i] == 0)
      break;

    if (!sendSignal(responce[i])) {
      return;
    }
  }
  // Debug
  Serial.println(responce);
  
  if (!sendSignal(10))
    return;
}

boolean sendSignal(int code) {
  for (int i = 0; i < radio_retries; i++) {
    if (radio.write(&code, sizeof(code))) {
      return true;
    }

    delay(radio_delay);
  }

  return false;
}

boolean areEqual(char s1[], char s2[]) {
  if (strlen(s1) != strlen(s2))
    return false; // They must be different

  for (int i = 0; i < strlen(s1); i++) {
    if (s1[i] != s2[i])
      return false;  // They are different
  }

  return true;  // They must be the same
}
