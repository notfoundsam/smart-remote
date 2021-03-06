#include <DHT.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <avr/wdt.h>
#include <avr/sleep.h>

// Radio setting
RF24 radio(9, 10); // For nano pin 9 and 10
int radioSpeedPin = 2;
int radioChannelPin1 = 3;
int radioChannelPin2 = 4;
int radio_retries = 5;
int radio_delay = 10;
byte radioSpeedState = 0; // 0 is RF24_250KBPS and 1 is RF24_1MBPS

// DHT setting
#define DHTTYPE DHT22 // DHT 11
const byte dht_pin = 8;
DHT dht(dht_pin, DHTTYPE);
float humi;
float temp;

// Battery setting
int bat_pin = A0;
// float max_v = 4.1;
// float min_v = 2.5;
float bat = 0;

String pipe_str = "AABBCCDD11"; // Keep the format

void setup() {
  analogReference(INTERNAL);
  pinMode(radioSpeedPin, INPUT);
  // Serial.begin(9600);
  radio.begin();
  delay(100);
  radio.powerUp();
  radio.setAutoAck(false);
  radio.setChannel(90);                 // (0 - 127)
  radio.setRetries(15,15);
  radio.setPayloadSize(32);
  radio.setCRCLength(RF24_CRC_8);
  radio.setDataRate(RF24_1MBPS);      // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);        // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.openWritingPipe(0xAABBCCDD88LL);
  radio.openReadingPipe(1, 0xAABBCCDD11LL);
  // radio.startListening();
  getDhtParams();
  getBatteryVoltage();

  delay(5000); // Sleep 5s before loop. It's Important!
}

void loop() {
  // checkRadioSetting();
  wdt_enable(WDTO_8S); //Задаем интервал сторожевого таймера (30ms) WDTO_15MS, WDTO_30MS, WDTO_60MS, WDTO_120MS, WDTO_250MS, WDTO_500MS etc.
  WDTCSR |= (1 << WDIE); //Устанавливаем бит WDIE регистра WDTCSR для разрешения прерываний от сторожевого таймера
  set_sleep_mode(SLEEP_MODE_PWR_DOWN); //Устанавливаем интересующий нас режим
  radio.powerDown();

  sleep_mode(); // Переводим МК в спящий режим

  getBatteryVoltage();
  getDhtParams();
  delay(300);
  getDhtParams();
  radio.powerUp();
  sendStatus();
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
      // Serial.println("RF24_1MBPS");
      radio.setDataRate(RF24_1MBPS);
    } else {
      radioSpeedState = 1;
      // Serial.println("RF24_1MBPS");
      // radio.setDataRate(RF24_1MBPS);
      // Serial.println("RF24_2MBPS");
      radio.setDataRate(RF24_2MBPS);
    }
  }
}

void getDhtParams() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (!isnan(t) && !isnan(h)) {
    humi = h;
    temp = t;
  }
}

void getBatteryVoltage() {
  bat = ((analogRead(bat_pin) * 1.1) / 1023) * 10.86;
}

void sendStatus() {
  // Max payload size in one package is 32 bytes
  String payload_0 = "0"; // Package nubber
  payload_0 += pipe_str; // Reading pipe of the station
  payload_0 += "type e,";
  payload_0 += "h ";
  payload_0 += humi;

  int rsize = payload_0.length();

  byte byte_arr[rsize+1];
  payload_0.getBytes(byte_arr, rsize+1);

  if (!sendWithACK(byte_arr, rsize)) {
    // Serial.println("sendStatus failed");
    return;
  }

  String payload_1 = "1"; // Package nubber
  payload_1 += ",t ";
  payload_1 += temp;

  // Add Battery voltage
  payload_1 += ",b ";
  payload_1 += bat;
  payload_1 += "\n";

  rsize = payload_1.length();

  byte byte_arr_2[rsize+1];
  payload_1.getBytes(byte_arr_2, rsize+1);

  if (!sendWithACK(byte_arr_2, rsize)) {
    // Serial.println("sendStatus failed2");
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
  byte ack[1] = {6};
  radio.stopListening();
  radio.write(ack, sizeof(ack));
  radio.startListening();
}

ISR (WDT_vect) {
  wdt_disable();
}
