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
int radio_retries = 1;
int radio_delay = 10;
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
byte code;
unsigned long started_waiting_at;               // Set up a timeout period, get the current microseconds
boolean timeout;
int index = 0;

void setup() {
  analogReference(INTERNAL);
  pinMode(radioSpeedPin, INPUT);
  Serial.begin(500000);
  radio.begin();
  delay(1000);
  radio.powerUp();
  radio.setChannel(75);                 // (0 - 127)
  radio.setRetries(15,15);
  radio.setDataRate(RF24_250KBPS);      // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);        // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  // radio.setAutoAck(1);
  // radio.setPayloadSize(1);
  radio.openWritingPipe(0xAABBCCDD55LL);
  radio.openReadingPipe(1, address);
  radio.startListening();
}

void loop() {
  checkRadioSetting();
  getDhtParams();
  getBatteryVoltage();

  if (radio.available()) {
    readRadio();
    radio.flush_rx();
  }
}

void readRadio() {
  byte code;
  timeout = true;
  index = 0;
  byte signal[3000];
  started_waiting_at = micros();

  // set timeout to 50 ms
  while (timeout == true && (micros() - started_waiting_at < 500000)) {
    if (radio.available()) {
      started_waiting_at = micros();

      
      radio.read(&code, sizeof(code));
      signal[index] = code;
      Serial.println(signal[index]);
      index++;

      if (code == 10) {
        timeout = false;
        break;
      }
    }
  }

  if (!timeout) {
    radio.stopListening();

    // If recive IR signal (it starts with i)
    if (signal[0] == 105) {
      sendIrSignal(signal);
    }
    // If recive comand (it starts with c)
    else if (signal[0] == 99) {
      sendCommand(signal);
    }

    // This delay is necessary
    // delay(30);
    
    
    
    delay(30);
    radio.startListening();
  } else {
    Serial.println("recieve timeout");
  }
}

void sendIrSignal(byte signal[]) {
  byte b;
  char buffer[20];
  byte buffer_index = 0;
  unsigned int raw_signal[700];
  int raw_index = 0;
  
  for (int i = 2; i < index; i++) {
    b = signal[i];
    
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

      // delay(30);
      // radio.startListening();
    }
  }
}

void sendCommand(byte signal[]) {
  byte b;
  String buffer = "";
  int buffer_index = 0;

  for (int i = 2; i < index; i++) {
    b = signal[i];

    if (b == 10) {
      break;
    } else {
      buffer += b;
      // char c = b;
      // buffer[buffer_index] = c;
      // buffer_index++;
    }
  }

  // This delay is necessary
  delay(10);
  
  // Serial.println(buffer_index);
  
  if (areEqual(buffer, "status")) {
    Serial.println("exec status command");
    sendStatus();
  } else {
    Serial.println("unsupportedCommand");
    unsupportedCommand();
  }
  
  // radio.startListening();
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
  responce += ",temp ";
  responce += temp;

  // Add Battery voltage
  responce += ",bat ";
  responce += Vin;
  responce += "\n";

  int rsize = responce.length();

  // radio.stopListening();

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
  // Add DHT params
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

boolean areEqual(String s1, String s2) {
  int s1_l = s1.length();
  int s2_l = s2.length();
  Serial.println(s1);
  Serial.println(s2);
  if (s1_l != s2_l) {
    Serial.println("length");
    return false; // They must be different
  }

  for (int i = 0; i < s1_l; i++) {
    if (s1[i] != s2[i]) {
      Serial.println("pos");
      Serial.println(s1[i]);
      Serial.println(s2[i]);
      return false;  // They are different
    }
  }

  return true;  // They must be the same
}
