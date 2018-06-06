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
unsigned long started_waiting_at_dht = 0;
float hum;
float temp;

// Battery setting
unsigned long started_waiting_at_battery = 0;
int bat_pin = A1;
// float max_v = 4.1;
// float min_v = 2.5;
float Vin = 0;
unsigned long ct = 0;

void setup() {
  analogReference(INTERNAL);
  pinMode(radioSpeedPin, INPUT);
  Serial.begin(9600);
  radio.begin();
  delay(100);
  radio.powerUp();
  radio.setChannel(90);                 // (0 - 127)
  radio.setRetries(15,15);
  radio.setPayloadSize(32);
  radio.setCRCLength(RF24_CRC_16);
  radio.setDataRate(RF24_1MBPS);      // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);        // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.openWritingPipe(address);
  // radio.openWritingPipe(0xAABBCCDD55LL);
  radio.openReadingPipe(1, address);
  radio.startListening();
}

void loop() {
  // checkRadioSetting();
  getDhtParams();
  getBatteryVoltage();

  if (radio.available()) {
    byte code[32];
    radio.read(&code, sizeof(code));

    Serial.println(ct++);

    // If recive IR signal (it starts with i)
    if (code[0] == 105) {
      Serial.println("ir");
      if (readIrSignal(code)) {
        radio.stopListening();
        // delay(10);
        responseSuccess();
        radio.startListening();
      } else {
        Serial.println("recieve timeout");
      }
    }
    // If recive comand (it starts with c)
    else if (code[0] == 99) {
      Serial.println("c");
      readCommand(code);
    } else {
      Serial.println("wtf");
    }
    // radio.flush_rx();
    // radio.flush_tx();
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
  buffer[0] = code[2];
  buffer[1] = code[3];
  buffer[2] = code[4];
  buffer[3] = '\0';
  zero = atoi(buffer);
  memset(buffer, 0, sizeof(buffer));

  // Setup one length
  buffer[0] = code[6];
  buffer[1] = code[7];
  buffer[2] = code[8];
  buffer[3] = code[9];
  buffer[4] = '\0';
  one = atoi(buffer);
  memset(buffer, 0, sizeof(buffer));

  Serial.println(zero);
  Serial.println(one);

  for (int i = 11; i < 32; ++i)
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
    // Serial.write(code[i]);
  }

  // Serial.println("---");

  byte ir_code[32];
  boolean timeout = true;
  unsigned long started_waiting_at = micros();

  // set timeout to 100ms
  while (micros() - started_waiting_at < 100000) {
    if (radio.available()) {
      
      radio.read(&ir_code, sizeof(ir_code));

      for (int i = 0; i < 32; ++i)
      {
        Serial.write(ir_code[i]);
        if (ir_code[i] == 10) {
          timeout = false;
          break;
        }
        Serial.write(ir_code[i]);
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
            // Serial.println(raw_signal[raw_index]);
            raw_index++;
            memset(buffer, 0, sizeof(buffer));
            buffer_index = 0;
          } else if (ir_code[i] == 10) {
            timeout = false;
            break;
          }
        }
      }
      started_waiting_at = micros();
      // Serial.println("-");
      // return true;
      // Serial.println(b);
    }
  }

  if (!timeout) {
    // radio.flush_rx();
    // radio.flush_tx();
    Serial.println("send ir signal");
    // for (int i = 0; i < raw_index; ++i)
    // {
    //   Serial.println(raw_signal[i]);
    // }
    irsend.sendRaw(raw_signal, raw_index, khz);
    return true;
  }

  return false;
}

void responseSuccess() {
  // Serial.println("ir signal sent");
  String responce = "ok";
  responce += "\n";

  int rsize = responce.length();
  
  byte byte_arr[rsize+1];
  responce.getBytes(byte_arr, rsize+1);

  if (!sendSignal(byte_arr, rsize)) {
    Serial.println("sendStatus failed");
    return;
  }
  radio.flush_rx();
  radio.flush_tx();
  Serial.println("sendStatus ok");
}

void readCommand(byte * code) {
  char buffer[32] = "";
  int buffer_index = 0;

  for (int i = 1; i < 32; ++i)
  {
    if (code[i] == 10) {
      break;
    }

    buffer[buffer_index] = code[i];
    buffer_index++;
  }

  radio.stopListening();

  if (strcmp(buffer, "status") == 0) {
    // Serial.println("exec status command");
    delay(10);
    sendStatus();
  } else {
    // Serial.println("unsupportedCommand");
    unsupportedCommand();
  }

  radio.startListening();
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
  delay(2);
  // 10 seconds
  if (started_waiting_at_dht == 0 || micros() - started_waiting_at_dht > 10000000) {
    Serial.println("get dht");
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    started_waiting_at_dht = micros();

    if (!isnan(t) && !isnan(h)) {
      hum = h;
      temp = t;

    }
  }
}

void getBatteryVoltage() {
  delay(2);
  // 8 seconds
  if (started_waiting_at_battery == 0 || micros() - started_waiting_at_battery > 8000000) {
    Serial.println("get bat");
    // Vin = analogRead(bat_pin);
    Vin = ((analogRead(bat_pin) * 1.1) / 1023) / 0.0911;

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

  byte byte_arr[rsize+1];
  responce.getBytes(byte_arr, rsize+1);

  if (!sendSignal(byte_arr, rsize)) {
    Serial.println("sendStatus failed");
    return;
  }
}

void unsupportedCommand() {
  String responce = "unsupported command\n";

  int rsize = responce.length();

  byte byte_arr[rsize+1];
  responce.getBytes(byte_arr, rsize+1);

  if (!sendSignal(byte_arr, rsize)) {
    Serial.println("unsupportedCommand failed");
    return;
  }
}

boolean sendSignal(byte * code, int size) {
  for (int i = 0; i < radio_retries; i++) {
    if (radio.write(code, size)) {
      return true;
    }

    delay(radio_delay);
  }

  return false;
}
