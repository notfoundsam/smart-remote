#include <IRremote.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <avr/wdt.h>
#include <avr/sleep.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

// Radio setting
RF24 radio(9, 10); // For nano pin 9 and 10
// int radioSpeedPin = 2;
// int radioChannelPin1 = 3;
// int radioChannelPin2 = 4;
int radio_retries = 15;
int radio_delay = 10;
byte radioSpeedState = 0; // 0 is RF24_250KBPS and 1 is RF24_1MBPS

uint8_t radio_id = 50;

// IRremote setting
IRsend irsend;
unsigned char khz = 38;

// BME280 setting
float humi;
float temp;
float pres;
Adafruit_BME280 bme; // I2C

// Battery setting
int bat_pin = A0;
float bat;
unsigned long sleep_at;
unsigned long status_timer;

// LED settings
int led_pin_blue = A1;
int led_pin_red = A2;

void setup() {
  delay(3000); // Sleep 3s before loop.

  analogReference(INTERNAL);
  // pinMode(radioSpeedPin, INPUT);
  pinMode(led_pin_red, OUTPUT);
  pinMode(led_pin_blue, OUTPUT);
  Serial.begin(9600);
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
  radio.startListening();
  
  bme.begin(0x76); // 0x76 or 0x77 for bme280

  readBMP();
  getBatteryVoltage();
  sleep_at = millis();
}

void loop() {
  // checkRadioSetting();

  if (radio.available()) {
    byte payload[32];
    radio.read(&payload, sizeof(payload));

    if (payload[0] == radio_id && payload[1] == 48) {
      sendACK(radio_id);

      // If recive IR signal (it starts with i)
      if (payload[2] == 105) {
        // Serial.println("ir");
        readIrSignal(payload);
      }
      // If recive comand (it starts with c)
      else if (payload[2] == 99) {
        // Serial.println("c");
        readCommand(payload);
      } else {
        // Serial.println("wtf");
      }
    }
  }

  // Send status periodically
  // if (millis() - status_timer > 8000) {
  //   readBMP();
  //   getBatteryVoltage();
  //   sendStatus();
  //   status_timer = millis();
  // }

  // Sleep each 20ms to save power
  while (millis() - sleep_at >= 500) {
    radio.stopListening();
    radio.powerDown();

    wdt_enable(WDTO_8S); // WDT interval WDTO_15MS, WDTO_30MS, WDTO_60MS, WDTO_120MS, WDTO_250MS, WDTO_500MS etc.
    WDTCSR |= (1 << WDIE); // Enable WDT
    set_sleep_mode(SLEEP_MODE_PWR_DOWN); // Set sleep mode
    sleep_mode(); // Go to sleep
    sleep_at = millis();

    radio.powerUp();

    sendRequest();
    radio.startListening();
  }
}

void readIrSignal(byte * code) {
  int zero = 0;
  int one = 0;
  char buffer[5];
  byte buffer_index = 0;
  boolean bit_code = false;
  unsigned int raw_signal[300];
  int raw_index = 0;

  // Setup zero length
  buffer[0] = code[4];
  buffer[1] = code[5];
  buffer[2] = code[6];
  buffer[3] = '\0';
  zero = atoi(buffer);
  memset(buffer, 0, sizeof(buffer));

  // Setup one length
  buffer[0] = code[8];
  buffer[1] = code[9];
  buffer[2] = code[10];
  buffer[3] = code[11];
  buffer[4] = '\0';
  one = atoi(buffer);
  memset(buffer, 0, sizeof(buffer));

  for (int i = 13; i < 32; ++i)
  {
    if (code[i] == 91) {
      bit_code = true;
      continue;
    } else if (code[i] == 93) {
      bit_code = false;
      continue;
    }

    if (bit_code) {
      if (code[i] > 47 && code[i] < 58) {
        buffer[buffer_index] = code[i];
        buffer_index++;
        continue;
      } else if (code[i] == 97) {
        int rep = atoi(buffer);

        for (int j = 0; j < rep; ++j)
        {
          raw_signal[raw_index] = zero;
          raw_index++;
        }

        memset(buffer, 0, sizeof(buffer));
        buffer_index = 0;
      } else if (code[i] == 98) {
        int rep = atoi(buffer);

        for (int j = 0; j < rep; ++j)
        {
          raw_signal[raw_index] = one;
          raw_index++;
        }

        memset(buffer, 0, sizeof(buffer));
        buffer_index = 0;
      }
    } else {
      if (code[i] > 47 && code[i] < 58) {
        buffer[buffer_index] = code[i];
        buffer_index++;
      } else if (code[i] == 32 && buffer_index > 0) {
        raw_signal[raw_index] = atoi(buffer);
        raw_index++;
        memset(buffer, 0, sizeof(buffer));
        buffer_index = 0;
      }
    }
  }

  byte package = 49;
  byte ir_code[32];
  boolean timeout = true;
  unsigned long started_at = millis();

  while (millis() - started_at <= radio_retries * radio_delay) {
    if (radio.available()) {
      radio.read(&ir_code, sizeof(ir_code));

      if (ir_code[0] != radio_id) {
        continue;
      }

      sendACK(radio_id);
      started_at = millis();
      
      if (ir_code[1] == package) {
        package++;
      } else {
        continue;
      }

      for (int i = 2; i < 32; ++i)
      {
        if (ir_code[i] == 10) {
          timeout = false;
          // raw_index--;
          break;
        }
        if (ir_code[i] == 91) {
          bit_code = true;
          continue;
        } else if (ir_code[i] == 93) {
          bit_code = false;
          continue;
        }

        if (bit_code) {
          if (ir_code[i] > 47 && ir_code[i] < 58) {
            buffer[buffer_index] = ir_code[i];
            buffer_index++;
            continue;
          } else if (ir_code[i] == 97) {
            int rep = atoi(buffer);

            for (int j = 0; j < rep; ++j)
            {
              raw_signal[raw_index] = zero;
              raw_index++;
            }

            memset(buffer, 0, sizeof(buffer));
            buffer_index = 0;
          } else if (ir_code[i] == 98) {
            int rep = atoi(buffer);

            for (int j = 0; j < rep; ++j)
            {
              raw_signal[raw_index] = one;
              raw_index++;
            }

            memset(buffer, 0, sizeof(buffer));
            buffer_index = 0;
          }
        } else {
          if (ir_code[i] > 47 && ir_code[i] < 58) {
            buffer[buffer_index] = ir_code[i];
            buffer_index++;
          } else if (ir_code[i] == 32 && buffer_index > 0) {
            raw_signal[raw_index] = atoi(buffer);
            raw_index++;
            memset(buffer, 0, sizeof(buffer));
            buffer_index = 0;
          } else if (ir_code[i] == 10) {
            raw_signal[raw_index] = atoi(buffer);
            timeout = false;
            break;
          }
        }
      }
    }
  }

  if (!timeout) {
    // Serial.print("\nok\n");
    irsend.sendRaw(raw_signal, raw_index, khz);
  }
}

void readCommand(byte * code) {
  byte data[32];
  unsigned long started_at = millis();

  char buffer[32] = "";
  int buffer_index = 0;

  for (int i = 3; i < 32; ++i) {
    if (code[i] == 10) {
      break;
    }

    buffer[buffer_index] = code[i];
    buffer_index++;
  }

  // while (millis() - started_at <= radio_retries * radio_delay) {
  //   if (radio.available()) {
  //     radio.read(&data, sizeof(data));

  //     if (data[0] == 6) {
  //       continue;
  //     }

  //     sendACK(radio_id);

  //     if (data[0] == 48) {
  //       started_at = millis();
  //     } else {
  //       // Serial.println("same package");
  //     }
  //   }
  // }

  if (strcmp(buffer, "red_on") == 0) {
    digitalWrite(led_pin_red, HIGH);
    Serial.println("red_on");
  } else if (strcmp(buffer, "red_off") == 0) {
    digitalWrite(led_pin_red, LOW);
    Serial.println("red_off");
  } else if (strcmp(buffer, "blue_on") == 0) {
    digitalWrite(led_pin_blue, HIGH);
    Serial.println("blue_on");
  } else if (strcmp(buffer, "blue_off") == 0) {
    digitalWrite(led_pin_blue, LOW);
    Serial.println("blue_off");
  } else if (strcmp(buffer, "empty") == 0) {
    // Serial.println("go to sleep");
    sleep_at = millis() - 1000;
    readBMP();
    getBatteryVoltage();
    sendStatus();
    return;
  } else {
    unsupportedCommand();
  }

  radio.stopListening();
  sendRequest();
  radio.startListening();
}

// void checkRadioSetting() {
//   byte currentSpeed = 0;

//   if (digitalRead(radioSpeedPin) == HIGH) {
//     currentSpeed = 1;
//   }

//   if (radioSpeedState != currentSpeed)
//   {
//     if (currentSpeed == 0) {
//       radioSpeedState = 0;
//       // Serial.println("RF24_250KBPS");
//       // radio.setDataRate(RF24_250KBPS);
//       // Serial.println("RF24_1MBPS");
//       radio.setDataRate(RF24_1MBPS);
//     } else {
//       radioSpeedState = 1;
//       // Serial.println("RF24_1MBPS");
//       // radio.setDataRate(RF24_1MBPS);
//       // Serial.println("RF24_2MBPS");
//       radio.setDataRate(RF24_2MBPS);
//     }
//   }
// }

void readBMP() {
  humi = bme.readHumidity();
  temp = bme.readTemperature();
  pres = bme.readPressure() / 100.0F;
}

void getBatteryVoltage() {
  bat = ((analogRead(bat_pin) * 1.1) / 1023) * 10.86;
}

void responseSuccess() {
  // Max payload size in one package is 32 bytes
  // String payload_0 = "0"; // Package nubber
  // payload_0 += pipe_str; // Reading pipe of the station
  // payload_0 += "type r,";
  // payload_0 += "ir ok\n";
  
  // int rsize = payload_0.length();

  // byte byte_arr[rsize+1];
  // payload_0.getBytes(byte_arr, rsize+1);

  // if (!sendWithACK(byte_arr, rsize)) {
  //   // Serial.println("sendStatus failed");
  //   return;
  // }
}

void sendStatus() {
  // Serial.print("status\n");
  byte radio_buff[32];
  byte radio_buff_index = 2;
  byte radio_package = 48;

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
      }

      radio_package++;
      radio_buff_index = 2;
    }
  }
}

void unsupportedCommand() {
  String responce = "0unsupported command\n";

  int rsize = responce.length();

  byte byte_arr[rsize+1];
  responce.getBytes(byte_arr, rsize+1);

  if (!sendWithACK(byte_arr, rsize)) {
    // Serial.println("unsupportedCommand failed");
    return;
  }
}

bool sendRequest() {
  String responce = "20tp rq\n";

  int rsize = responce.length();

  byte byte_arr[rsize+1];
  responce.getBytes(byte_arr, rsize+1);

  if (!sendWithACK(byte_arr, rsize)) {
    Serial.println("ok");
    return true;
  }

  return false;
}

boolean sendWithACK(byte * data, byte size) {
  byte response[32];
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

void sendACK(byte radio_node) {
  byte ack[2];
  ack[0] = radio_node;
  ack[1] = 6;
  radio.stopListening();
  radio.writeFast(ack, sizeof(ack));
  radio.txStandBy();
  radio.startListening();
}

ISR (WDT_vect) {
  wdt_disable();
  // sleep_at = millis();
}
