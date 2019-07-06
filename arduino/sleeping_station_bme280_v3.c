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
int radio_retries = 15;
int radio_delay = 15;
byte radioSpeedState = 0; // 0 is RF24_250KBPS and 1 is RF24_1MBPS

uint8_t radio_id = 49;
// String pipe_str = "AABBCCCC22"; // Keep the format

// BME280 setting
float humi;
float temp;
float pres;
Adafruit_BME280 bme; // I2C

// Battery setting
int bat_pin = A0;
float bat;

unsigned long status_timer;

void setup() {
  delay(3000); // Sleep 3s before loop.

  analogReference(INTERNAL);
  pinMode(radioSpeedPin, INPUT);
  // Serial.begin(9600);
  radio.begin();
  delay(100);
  radio.powerUp();
  radio.setChannel(90); // (0 - 127)
  radio.setAutoAck(false); // Disable hardware ACK, use program ACK
  radio.setPayloadSize(32);
  radio.setCRCLength(RF24_CRC_8);
  radio.setDataRate(RF24_1MBPS); // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX); // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.openWritingPipe(0xAAAAAAAA22LL);
  radio.openReadingPipe(1, 0xAAAAAAAA11LL);
  
  bme.begin(0x76); // 0x76 or 0x77 for bme280
  delay(50);
  readBMP();
  getBatteryVoltage();
}

void loop() {
  // Serial.println("start");
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

  // if (millis() - status_timer > 2000) {
  //   sendStatus();
  //   status_timer = millis();
  // }
}

void readBMP() {
  humi = bme.readHumidity();
  temp = bme.readTemperature();
  pres = bme.readPressure() / 100.0F;

  // humi = 42.00;
  // temp = 23.20;
  // pres = 1030.00;
}

void getBatteryVoltage() {
  bat = ((analogRead(bat_pin) * 1.1) / 1023) * 11;
}

void sendStatus() {
  // Serial.print("status\n");
  uint8_t radio_buff[32];
  uint8_t radio_buff_index = 2;
  uint8_t radio_package = 48;

  // Max payload size in one package is 32 bytes
  String payload = "tp ev,";
  payload += "h ";
  payload += humi;
  payload += ",t ";
  payload += temp;
  payload += ",p ";
  payload += pres;
  payload += ",b ";
  payload += bat;
  payload += "\n";

  int rsize = payload.length();

  radio_buff[0] = radio_id;
  radio_buff[1] = radio_package;

  for (int i = 0; i < rsize; i++) {
    radio_buff[radio_buff_index] = payload[i];
    radio_buff_index++;

    if (radio_buff_index == 32 || payload[i] == 10) {
      radio_buff[1] = radio_package;

      if (!sendWithACK(radio_buff, radio_buff_index)) {
        // Serial.print("fail\n");
        return;
      } else {
        // delay(15);
        // Serial.print("success\n");
      }

      radio_package++;
      radio_buff_index = 2;
    }
  }
}

boolean sendWithACK(uint8_t *data, uint8_t size) {
  uint8_t response[32];
  unsigned long ack_started_at;

  for (int i = 0; i <= radio_retries; i++) {
    radio.stopListening();
    radio.writeFast(data, size);
    radio.txStandBy();
    radio.startListening();

    ack_started_at = millis();
    // Wait 15ms for responce
    while (millis() - ack_started_at <= radio_delay) {
      if (radio.available()) {
        radio.read(&response, sizeof(response));

        if (data[0] == response[0] && response[1] == 6) {
          return true;
        }
      }
    }
  }

  return false;
}

void sendACK() {
  uint8_t ack[1] = {6};
  radio.stopListening();
  radio.write(ack, sizeof(ack));
  radio.startListening();
}

ISR (WDT_vect) {
  wdt_disable();
}
