#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <avr/wdt.h>
#include <avr/sleep.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

// Radio setting
RF24 radio(9, 10); // For nano pin 9 and 10
int radioSpeedPin = 2;
int radioChannelPin1 = 3;
int radioChannelPin2 = 4;
int radio_retries = 3;
int radio_delay = 8;
byte radioSpeedState = 0; // 0 is RF24_250KBPS and 1 is RF24_1MBPS

String pipe_str = "AABBCCCC22"; // Keep the format

// BME280 setting
float humi;
float temp;
float pres;
Adafruit_BME280 bme; // I2C

// Battery setting
int bat_pin = A0;
float bat;

void setup() {
  delay(3000); // Sleep 3s before loop.

  analogReference(INTERNAL);
  pinMode(radioSpeedPin, INPUT);
  // Serial.begin(9600);
  radio.begin();
  delay(100);
  radio.powerUp();
  radio.setAutoAck(false); // Disable hardware ACK, use program ACK
  radio.setChannel(90); // (0 - 127)
  // radio.setRetries(15,15);
  radio.setPayloadSize(32);
  radio.setCRCLength(RF24_CRC_8);
  radio.setDataRate(RF24_1MBPS); // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX); // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.openWritingPipe(0xAABBCCDD88LL);
  radio.openReadingPipe(1, 0xAABBCCCC22LL);
  
  bme.begin(0x76); // 0x76 or 0x77 for bme280

  readBMP();
  getBatteryVoltage();
}

void loop() {
  // checkRadioSetting();
  radio.powerDown();
  wdt_enable(WDTO_8S); // WDT interval WDTO_15MS, WDTO_30MS, WDTO_60MS, WDTO_120MS, WDTO_250MS, WDTO_500MS, WDTO_1S, WDTO_2S, WDTO_4S, WDTO_8S
  WDTCSR |= (1 << WDIE); // Enable WDT
  set_sleep_mode(SLEEP_MODE_PWR_DOWN); // Set sleep mode
  sleep_mode(); // Go to sleep
  getBatteryVoltage();
  readBMP();
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

void readBMP() {
  humi = bme.readHumidity();
  temp = bme.readTemperature();
  pres = bme.readPressure() / 100.0F;
}

void getBatteryVoltage() {
  bat = ((analogRead(bat_pin) * 1.1) / 1023) * 11;
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
  payload_1 += ",p ";
  payload_1 += pres;

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
    while (millis() - ack_started_at <= radio_delay) {
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
