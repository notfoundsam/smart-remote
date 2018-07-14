#include <DHT.h>
#include <IRremote.h>
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <avr/wdt.h>
#include <avr/sleep.h>

// Radio setting
RF24 radio(9, 10); // For nano pin 9 and 10
uint64_t address = 0xAABBCCDD44LL;
int radioSpeedPin = 2;
int radioChannelPin1 = 3;
int radioChannelPin2 = 4;
int radio_retries = 5;
int radio_delay = 10;
byte radioSpeedState = 0; // 0 is RF24_250KBPS and 1 is RF24_1MBPS

// IRremote setting
IRsend irsend;
unsigned char khz = 38;

// DHT setting
#define DHTTYPE DHT22 // DHT 11
const byte dht_pin = 8;
DHT dht(dht_pin, DHTTYPE);
float hum;
float temp;

// Battery setting
int bat_pin = A1;
// float max_v = 4.1;
// float min_v = 2.5;
float bat = 0;
unsigned long sleep_at;

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
  radio.openWritingPipe(0xAABBCCDD55LL);
  radio.openReadingPipe(1, address);
  radio.startListening();
  getDhtParams();
  getBatteryVoltage();
  sleep_at = millis();
}

void loop() {
  // checkRadioSetting();

  if (radio.available()) {
    byte code[32];
    radio.read(&code, sizeof(code));

    sendACK();

    // If recive IR signal (it starts with i)
    if (code[1] == 105) {
      // Serial.println("ir");
      if (readIrSignal(code)) {
        responseSuccess();
      } else {
        // Serial.println("recieve timeout");
      }
    }
    // If recive comand (it starts with c)
    else if (code[1] == 99) {
      // Serial.println("c");
      readCommand(code);
    } else {
      // Serial.println("wtf");
    }
  }

  // Sleep each 15ms to save power
  while (millis() - sleep_at >= 20) {
    wdt_enable(WDTO_60MS); //Задаем интервал сторожевого таймера (30ms) WDTO_15MS, WDTO_30MS, WDTO_60MS, WDTO_120MS, WDTO_250MS, WDTO_500MS etc.
    WDTCSR |= (1 << WDIE); //Устанавливаем бит WDIE регистра WDTCSR для разрешения прерываний от сторожевого таймера
    set_sleep_mode(SLEEP_MODE_PWR_DOWN); //Устанавливаем интересующий нас режим

    radio.stopListening();
    radio.powerDown();

    // ADCSRA &= ~(1 << ADEN); // Отключаем АЦП
    // set_sleep_mode(SLEEP_MODE_PWR_DOWN); //Устанавливаем интересующий нас режим
    // sleep_enable();
    // // Отключаем детектор пониженного напряжения питания 
    // MCUCR = bit (BODS) | bit (BODSE);  
    // MCUCR = bit (BODS);
    // sleep_cpu(); // Переводим МК в спящий режим

    sleep_mode(); // Переводим МК в спящий режим
    sleep_at = millis();

    radio.powerUp();
    radio.startListening();
  }
}

boolean readIrSignal(byte * code) {
  int zero = 0;
  int one = 0;
  char buffer[5];
  byte buffer_index = 0;
  boolean bit_code = false;
  unsigned int raw_signal[300];
  int raw_index = 0;

  // Setup zero length
  buffer[0] = code[3];
  buffer[1] = code[4];
  buffer[2] = code[5];
  buffer[3] = '\0';
  zero = atoi(buffer);
  memset(buffer, 0, sizeof(buffer));

  // Setup one length
  buffer[0] = code[7];
  buffer[1] = code[8];
  buffer[2] = code[9];
  buffer[3] = code[10];
  buffer[4] = '\0';
  one = atoi(buffer);
  memset(buffer, 0, sizeof(buffer));

  for (int i = 12; i < 32; ++i)
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
      } else if (code[i] == 32) {
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

      if (ir_code[0] == 6) {
        continue;
      }

      sendACK();

      if (ir_code[0] == package) {
        started_at = millis();
        package++;
      } else {
        // Serial.println("same package");
        continue;
      }

      for (int i = 1; i < 32; ++i)
      {
        if (ir_code[i] == 10) {
          timeout = false;
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
          } else if (ir_code[i] == 32) {
            raw_signal[raw_index] = atoi(buffer);
            raw_index++;
            memset(buffer, 0, sizeof(buffer));
            buffer_index = 0;
          } else if (ir_code[i] == 10) {
            timeout = false;
            break;
          }
        }
      }
    }
  }

  if (!timeout) {
    irsend.sendRaw(raw_signal, raw_index, khz);
    return true;
  }

  return false;
}

void readCommand(byte * code) {
  byte data[32];
  unsigned long started_at = millis();

  char buffer[32] = "";
  int buffer_index = 0;

  for (int i = 2; i < 32; ++i)
  {
    if (code[i] == 10) {
      break;
    }

    buffer[buffer_index] = code[i];
    buffer_index++;
  }

  while (millis() - started_at <= radio_retries * radio_delay) {
    if (radio.available()) {
      radio.read(&data, sizeof(data));

      if (data[0] == 6) {
        continue;
      }

      sendACK();

      if (data[0] == 48) {
        started_at = millis();
      } else {
        // Serial.println("same package");
      }
    }
  }

  if (strcmp(buffer, "status") == 0) {
    sendStatus();
  } else {
    unsupportedCommand();
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
    hum = h;
    temp = t;
  }
}

void getBatteryVoltage() {
  bat = ((analogRead(bat_pin) * 1.1) / 1023) / 0.0855;
}

void responseSuccess() {
  String responce = "0ok";
  responce += "\n";

  int rsize = responce.length();
  
  byte byte_arr[rsize+1];
  responce.getBytes(byte_arr, rsize+1);

  if (!sendWithACK(byte_arr, rsize)) {
    // Serial.println("sendStatus failed");
    return;
  }
}

void sendStatus() {
  getBatteryVoltage();
  getDhtParams();
  // Add DHT params
  String responce = "0h ";
  responce += hum;
  responce += ",t ";
  responce += temp;

  // Add Battery voltage
  responce += ",b ";
  responce += bat;
  responce += "\n";

  int rsize = responce.length();

  byte byte_arr[rsize+1];
  responce.getBytes(byte_arr, rsize+1);

  if (!sendWithACK(byte_arr, rsize)) {
    // Serial.println("sendStatus failed");
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
  // sleep_at = millis();
}
