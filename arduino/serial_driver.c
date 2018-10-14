#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(9, 10);
int radio_retries = 15;
int radio_delay = 5;

boolean isSucces = false;
byte mode = 2; // 1 - tx mode, 2 - rx mode

void setup() {
  Serial.begin(500000);
  Serial.setTimeout(50);
  radio.begin();
  delay(100);
  radio.powerUp();
  radio.setAutoAck(false);
  radio.setChannel(90);
  // radio.setRetries(15,15);
  radio.setPayloadSize(32);
  radio.setCRCLength(RF24_CRC_8);
  radio.setDataRate(RF24_1MBPS);     // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);       // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.openReadingPipe(1, 0xAABBCCDD55LL);
  radio.openReadingPipe(2, 0xAABBCCDD88LL);
  radio.startListening();
}

void loop() {
  if (Serial.available() > 0) {
    isSucces = false;

    mode = 1;
    readSerial();
    mode = 2;

    if (isSucces) {
      Serial.print(":OK\n");
    } else {
      Serial.print(":FAIL\n");
    }
  }
  if (radio.available()) {
    isSucces = false;
    
    recive();

    if (isSucces) {
      Serial.print(":OK\n");
    } else {
      Serial.print(":FAIL\n");
    }
  }
}

void readSerial() {
  byte b;
  byte serial_buffer = 0;
  boolean timeout = true;
  unsigned long started_waiting_at = millis();

  char pipe_buf[10];
  int pipe_buf_i = 0;
  boolean pipe_set = false;
  uint64_t pipe;

  byte buffer[32];
  int buffer_index = 1;
  
  // Set timeout to 100ms
  while (millis() - started_waiting_at < 100) {
    if (Serial.available() > 0) {
      serial_buffer++;
      b = Serial.read();

      if (pipe_buf_i < 10) {
        pipe_buf[pipe_buf_i] = b;
        pipe_buf_i++;
        started_waiting_at = millis();
        continue;
      }

      if (!pipe_set) {
        pipe_set = true;
        buffer[0] = 48;
        buffer[buffer_index] = b;
        buffer_index++;
        
        pipe_buf[10] = '\0';
        pipe = getUInt64fromHex(pipe_buf);
        radio.openWritingPipe(pipe);
        started_waiting_at = millis();
        continue;
      }

      if (b == 10) {
        buffer[buffer_index] = 10;
        buffer_index++;

        if (!sendWithACK(buffer, buffer_index)) {
          Serial.print("RADIO TRANSMIT SIGNAL 1");
          return;
        }

        timeout = false;

        break;
      } else {
        buffer[buffer_index] = b;
        buffer_index++;
      }

      if (buffer_index == 32) {
        if (!sendWithACK(buffer, buffer_index)) {
          Serial.print("RADIO TRANSMIT SIGNAL 2");
          return;
        }
        buffer_index = 1;
        buffer[0] = buffer[0] + 1;
      }

      started_waiting_at = millis();

      if (serial_buffer == 32) {
        Serial.print("next\n");
        serial_buffer = 0;
      }
    }
  }
  
  if (timeout) {
    serialFlush();
    Serial.print("SERIAL READ TIMEOUT");
    return;
  } else {
    recive();
  }
}

void recive() {
  byte income_pipe;
  byte response[32];
  boolean pipe_set = false;
  char pipe_buf[10];
  int pipe_buf_i = 0;
  boolean ended = false;
  unsigned long started_at = millis();
  byte package = 48;
  int recive_limit = 500;
  uint64_t pipe;

  while (millis() - started_at <= recive_limit) {
    if (radio.available(&income_pipe)) {
      if (income_pipe == mode) {
        radio.read(&response, sizeof(response));

        if (response[0] == 6) {
          continue;
        }

        // Get the pipe address from the package
        if (mode == 2) {

          if (response[0] == package) {
            started_at = millis();
            package++;
            int i = 1;

            if (!pipe_set) {
              for (i; i < 11; i++) {
                pipe_buf[pipe_buf_i] = response[i];
                pipe_buf_i++;
              }
              pipe = getUInt64fromHex(pipe_buf);
              radio.openWritingPipe(pipe);
              pipe_set = true;

              Serial.write(114);
              Serial.write(32);

              for (int j = 0; j < sizeof(pipe_buf); j++) {
                Serial.write(pipe_buf[j]);
              }
              Serial.write(44);
            }
            
            sendACK();

            if (response[i] == 0) {
              continue;
            }

            for (i; i < sizeof(response); i++) {
              if (response[i] == 10) {
                ended = true;
                recive_limit = 20;
                break;
              }

              Serial.write(response[i]);
            }
          } else {
            sendACK();
            // Serial.println("same package");
          }
        } else {
          sendACK();

          if (response[0] == package) {
            started_at = millis();
            package++;

            for (int i = 1; i < sizeof(response); i++) {
              if (response[i] == 10) {
                ended = true;
                recive_limit = 20;
                break;
              }

              Serial.write(response[i]);
            }
          } else {
            // Serial.println("same package");
          }
        }
      }
    }
  }

  if (ended){
    isSucces = true;
  } else {
    Serial.print("RADIO RESPONCE TIMEOUT");
  }
}

boolean sendWithACK(byte * data, int size) {
  byte income_pipe;
  byte response[32];
  unsigned long ack_started_at;

  int radio_sleep_retries = 30;

  for (int i = 0; i <= radio_sleep_retries; i++) {
    radio.stopListening();
    radio.write(data, size);
    radio.startListening();

    ack_started_at = millis();
    // Wait 15ms for responce
    while (millis() - ack_started_at <= 15) {
      if (radio.available(&income_pipe)) {
        radio_sleep_retries = radio_retries;

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
