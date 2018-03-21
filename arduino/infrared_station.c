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
int radio_retries = 10;
int radio_delay = 15;
byte radioSpeedState = 0; // 0 is RF24_250KBPS and 1 is RF24_1MBPS

// IRremote setting
IRsend irsend;
unsigned char khz = 38;

// DHT setting
#define DHTTYPE DHT22 // DHT 11
const byte dht_pin = 8;
DHT dht(dht_pin, DHTTYPE);
unsigned long started_waiting_at_dht = 0;
float hum;
float temp;

// Battery setting
unsigned long started_waiting_at_battery = 0;
int bat_pin = A1;
// float max_v = 4.1;
// float min_v = 2.5;
float Vin = 0;

void setup() {
  analogReference(INTERNAL);
  pinMode(radioSpeedPin, INPUT);
  Serial.begin(500000);
  radio.begin();
  delay(1000);
  radio.powerUp();
  radio.setChannel(75);                 // (0 - 127)
  radio.setRetries(15,15);
  radio.setDataRate(RF24_1MBPS);      // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);        // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.openWritingPipe(address);
  radio.openReadingPipe(1, address);
  radio.startListening();
}

void loop() {
  checkRadioSetting();
  getDhtParams();
  getBatteryVoltage();

  if (radio.available()) {
    byte code;
    radio.read(&code, sizeof(code));

    // If recive IR signal (it starts with i)
    if (code == 105) {
      if (readIrSignal()) {
        radio.stopListening();
        responseSuccess();
        radio.startListening();
      } else {
        Serial.println("recieve timeout");
      }
    }
    // If recive comand (it starts with c)
    else if (code == 99) {
      readCommand();
    }
    // radio.flush_rx();
    // radio.flush_tx();
  }
}

boolean readIrSignal() {
  byte b;
  int index = 0;
  char buffer[20];
  byte buffer_index = 0;
  unsigned int raw_signal[500];
  int raw_index = 0;
  unsigned long started_waiting_at = micros();

  // set timeout to 500ms
  while (micros() - started_waiting_at < 500000) {
    if (radio.available()) {
      started_waiting_at = micros();
      radio.read(&b, sizeof(b));

      if (b > 47 && b < 58) {
        buffer[buffer_index] = b;
        buffer_index++;
      } else if (b == 32) {
        raw_signal[raw_index] = atoi(buffer);
        raw_index++;
        memset(buffer, 0, sizeof(buffer));
        buffer_index = 0;
      } else if (b == 10) {
        irsend.sendRaw(raw_signal, raw_index, khz);
        return true;
      }
    }
  }

  return false;
}

void responseSuccess() {
  // Serial.println("ir signal sent");
  String responce = "ok\n";
  int rsize = responce.length();
  
  for (int i = 0; i < rsize; i++) {
    if (responce[i] == 0)
      break;

    if (!sendSignal(responce[i])) {
      Serial.println("sendIrSignal failed");
      return;
    }
  }
}

void readCommand() {
  byte b;
  boolean timeout = true;
  char buffer[100] = "";
  int buffer_index = 0;
  unsigned long started_waiting_at = micros();

  // set timeout to 50ms
  while (micros() - started_waiting_at < 50000) {
    if (radio.available()) {
      started_waiting_at = micros();
      radio.read(&b, sizeof(b));
      
      if (b == 10) {
        timeout = false;
        break;
      } else {
        buffer[buffer_index] = b;
        buffer_index++;
      }
    }
  }

  if (!timeout) {
    // This delay is important. Some time ACK brake when listening stops
    delay(30);
    radio.stopListening();

    if (strcmp(buffer, "status") == 0) {
      Serial.println("exec status command");
      sendStatus();
    } else {
      Serial.println("unsupportedCommand");
      Serial.println(buffer);
      unsupportedCommand();
    }

    radio.startListening();
  } else {
    Serial.println("recieve timeout");
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
      // Serial.println("RF24_250KBPS");
      // radio.setDataRate(RF24_250KBPS);
      Serial.println("RF24_1MBPS");
      radio.setDataRate(RF24_1MBPS);
    } else {
      radioSpeedState = 1;
      // Serial.println("RF24_1MBPS");
      // radio.setDataRate(RF24_1MBPS);
      Serial.println("RF24_2MBPS");
      radio.setDataRate(RF24_2MBPS);
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

      started_waiting_at_dht = micros();
    }
  }
}

void getBatteryVoltage() {
  // 10 seconds
  if (started_waiting_at_battery == 0 || micros() - started_waiting_at_battery > 10000000) {
    // Vin = analogRead(bat_pin);
    Vin = (analogRead(bat_pin) * 1.1) / 1023;
    started_waiting_at_battery = micros();
  }
}

void sendStatus() {
  // Add DHT params
  String responce = "hum ";
  responce += hum;
  responce += ",temp ";
  responce += temp;

  // Add Battery voltage
  responce += ",bat ";
  responce += Vin;
  responce += "\n";

  int rsize = responce.length();

  for (int i = 0; i < rsize; i++) {
    if (responce[i] == 0)
      break;

    if (!sendSignal(responce[i])) {
      Serial.println("sendStatus failed");
      return;
    }
  }
  // Debug
  Serial.println(responce);
}

void unsupportedCommand() {
  String responce = "unsupported command\n";

  int rsize = responce.length();

  for (int i = 0; i < rsize; i++) {
    if (responce[i] == 0)
      break;

    if (!sendSignal(responce[i])) {
      Serial.println("unsupportedCommand failed");
      return;
    }
  }
}

boolean sendSignal(byte code) {
  for (int i = 0; i < radio_retries; i++) {
    if (radio.write(&code, sizeof(code))) {
      return true;
    }

    delay(radio_delay);
  }

  return false;
}
