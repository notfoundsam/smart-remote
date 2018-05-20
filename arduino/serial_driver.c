#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(9, 10);
int radio_retries = 10;
int radio_delay = 10;

boolean isSucces = false;
unsigned int radio_fail = 0;

void setup() {
  Serial.begin(500000);
  Serial.setTimeout(50);
  radioSetup();
  // Serial.print("Loaded\n");
}

void loop() {
  if (radio_fail > 20) {
    radioSetup();
    delay(50);
    radio_fail = 0;
  }

  if (Serial.available() > 0) {
    isSucces = false;
    // radio.stopListening();

    readSerial();
    if (isSucces) {
      Serial.print(":OK\n");
    } else {
      radio.startListening();
      // delay(50);
      // radio.flush_rx();
      // radio.flush_tx();
      Serial.print(":FAIL\n");
    }
  }
}

void radioSetup() {
  radio.begin();
  delay(10);
  radio.powerUp();
  radio.setChannel(75);
  radio.setRetries(15,15);
  radio.setPayloadSize(32);
  radio.setCRCLength(RF24_CRC_8);
  radio.setDataRate(RF24_2MBPS);     // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);       // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  // radio.openReadingPipe(2,0xAABBCCDD55LL);
  radio.startListening();
}

void readSerial() {
  byte b;
  byte buffer_counter = 0;
  boolean timeout = true;
  unsigned long started_waiting_at = micros();

  char pipe_buf[10];
  int pipe_buf_i = 0;
  boolean pipe_set = false;
  uint64_t pipe;

  byte buffer[32];
  byte buffer_index = 0;
  
  // Set timeout to 50ms
  while (micros() - started_waiting_at < 50000) {
    if (Serial.available() > 0) {
      // started_waiting_at = micros();
      buffer_counter++;
      b = Serial.read();

      if (pipe_buf_i < 10) {
        pipe_buf[pipe_buf_i] = b;
        pipe_buf_i++;
        started_waiting_at = micros();
        continue;
      }

      if (!pipe_set) {
        buffer[buffer_index] = b;
        buffer_index++;
        
        pipe_buf[10] = '\0';
        pipe = getUInt64fromHex(pipe_buf);
        radio.stopListening();
        radio.openWritingPipe(pipe);
        pipe_set = true;
        started_waiting_at = micros();
        continue;
      }

      if (b == 10) {
        buffer[buffer_index] = 10;
        buffer_index++;

        if (!sendSignal(buffer, sizeof(buffer))) {
          serialFlush();
          Serial.print("RADIO TRANSMIT SIGNAL 1");
          radio_fail++;
          return;
        }
        timeout = false;
        break;
      } else {
        buffer[buffer_index] = b;
        buffer_index++;
      }

      if (buffer_index == 32) {
        if (!sendSignal(buffer, buffer_index)) {
          serialFlush();
          Serial.print("RADIO TRANSMIT SIGNAL 2");
          radio_fail++;
          return;
        }
        buffer_index = 0;
      }

      started_waiting_at = micros();

      if (buffer_counter == 32) {
        Serial.print("next\n");
        buffer_counter = 0;
      }
    }
  }
  
  if (timeout) {
    serialFlush();
    Serial.print("SERIAL READ TIMEOUT");
    return;
  } else {
    radio.openReadingPipe(1, pipe);
    // setReadingPipe(buffer[1]);
    // radio.startListening();
    waitForResponce();
    // isSucces = true;
  }
}

boolean sendSignal(byte * signal, int size) {
  // unsigned long started_waiting_at = micros();

  for (int i = 0; i < radio_retries; i++) {
    if (radio.write(signal, size)) {
      // Serial.print("w");
      // Serial.print(micros() - started_waiting_at);
      // Serial.print("-");
      return true;
    }
    delay(radio_delay);
    // Serial.print("r");
  }

  // Serial.print(micros() - started_waiting_at);
  // Serial.print("-");

  return false;
}

void waitForResponce() {
  byte income_pipe;
  byte signal[32];
  unsigned long responce_started_at = micros();
  boolean timeout = true;

  byte b;
  byte buffer[200];
  int bufer_index = 0;

  delay(10);
  radio.startListening();

  // Wait 2s seconds for responce
  while (micros() - responce_started_at < 2000000) {
    if (radio.available(&income_pipe)) {
      if (income_pipe == 1) {
        // responce_started_at = micros();
        radio.read(&signal, sizeof(signal));

        // if (signal == 10) {
          timeout = false;
          break;
        // } else {
        //   buffer[bufer_index] = signal;
        //   bufer_index++;
        // }
      }
    }
  }

  if (!timeout) {
    for (int i = 0; i < 32; i++) {
      if (signal[i] == 10) {
        // Serial.print(signal[i]);
        break;
      }

      Serial.write(signal[i]);
    }
    isSucces = true;
  } else {
    // Some errors are here
    Serial.print("RADIO RESPONCE TIMEOUT");
  }
}

void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
}

uint64_t getUInt64fromHex(char const *str)
{
  uint64_t accumulator = 0;
  for (size_t i = 0 ; isxdigit((unsigned char)str[i]) ; ++i)
  {
    char c = str[i];
    accumulator *= 16;
    if (isdigit(c)) /* '0' .. '9'*/
      accumulator += c - '0';
    else if (isupper(c)) /* 'A' .. 'F'*/
      accumulator += c - 'A' + 10;
    else /* 'a' .. 'f'*/
      accumulator += c - 'a' + 10;
  }

  return accumulator;
}
