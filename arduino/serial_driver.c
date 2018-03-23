#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(9, 10);
// int index = 0;
int radio_retries = 10;
int radio_delay = 15;

uint64_t pipes[5] = {
  0xAABBCCDD11LL,
  0xAABBCCDD22LL,
  0xAABBCCDD33LL,
  0xAABBCCDD44LL,
  0xAABBCCDD55LL,
};

boolean isSucces = false;

void setup() {
  Serial.begin(500000);
  Serial.setTimeout(50);
  
  radio.begin();
  delay(1000);
  radio.powerUp();
  radio.setChannel(75);
  radio.setRetries(15,15);
  radio.setDataRate(RF24_2MBPS);     // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);       // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.startListening();
  Serial.print("Loaded\n");
}

void loop() {
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

void readSerial() {
  byte b;
  byte buffer[5];
  byte buffer_index = 0;
  byte buffer_counter = 0;
  boolean buffer_on = true;
  boolean timeout = true;
  unsigned long started_waiting_at = micros();
  
  // Set timeout to 50ms
  while (micros() - started_waiting_at < 50000) {
    if (Serial.available() > 0) {
      // started_waiting_at = micros();
      buffer_counter++;
      b = Serial.read();

      if (buffer_on) {
        if (buffer_index == 2) {
          buffer_on = false;
          radio.stopListening();
          delay(10);
          setWritingPipe(buffer[1]);
          delay(10);

          if (!sendSignal(buffer[0])) {
            Serial.print("RADIO TRANSMIT SIGNAL 1");
            return;
          }
          started_waiting_at = micros();
        } else {
          buffer[buffer_index] = b;
          buffer_index++;
        }
        
        continue;
      }

      if (!sendSignal(b)) {
        Serial.print("RADIO TRANSMIT SIGNAL 2");
        return;
      }

      started_waiting_at = micros();

      if (b == 10) {
        timeout = false;
        break;
      }

      if (buffer_counter == 30) {
        Serial.print("next\n");
        buffer_counter = 0;
      }
    }
  }
  
  if (timeout) {
    Serial.print("SERIAL READ TIMEOUT");
    return;
  } else {
    setReadingPipe(buffer[1]);
    // radio.startListening();
    waitForResponce();
    // isSucces = true;
  }
}

boolean sendSignal(byte signal) {
  for (int i = 0; i < radio_retries; i++) {
    if (radio.write(&signal, sizeof(signal))) {
      return true;
    }
    delay(radio_delay);
  }

  return false;
}

// Set pipe to send signal
void setWritingPipe(int pipe) {

  if (pipe == 49) {
    radio.openWritingPipe(pipes[0]);
  } else if (pipe == 50) {
    radio.openWritingPipe(pipes[1]);
  } else if (pipe == 51) {
    radio.openWritingPipe(pipes[2]);
  } else if (pipe == 52) {
    radio.openWritingPipe(pipes[3]);
  } else if (pipe == 53) {
    radio.openWritingPipe(pipes[4]);
  }
}

// Set pipe to recieve responce
void setReadingPipe(int pipe) {
  if (pipe == 49) {
    radio.openReadingPipe(1, pipes[0]);
  } else if (pipe == 50) {
    radio.openReadingPipe(1, pipes[1]);
  } else if (pipe == 51) {
    radio.openReadingPipe(1, pipes[2]);
  } else if (pipe == 52) {
    radio.openReadingPipe(1, pipes[3]);
  } else if (pipe == 53) {
    radio.openReadingPipe(1, pipes[4]);
  }
}

void waitForResponce() {
  byte pipe;
  byte signal;
  unsigned long responce_started_at = micros();
  boolean timeout = true;

  byte b;
  byte buffer[200];
  int bufer_index = 0;

  radio.startListening();

  // Wait 2s seconds for responce
  while (micros() - responce_started_at < 2000000) {
    if (radio.available(&pipe)) {
      if (pipe == 1) {
        responce_started_at = micros();
        radio.read(&signal, sizeof(signal));

        if (signal == 10) {
          timeout = false;
          break;
        } else {
          buffer[bufer_index] = signal;
          bufer_index++;
        }
      }
    }
  }

  if (!timeout) {
    for (int i = 0; i < bufer_index; i++) {
      Serial.write(buffer[i]);
    }
    isSucces = true;
  } else {
    // Some errors are here
    Serial.print("RADIO RESPONCE TIMEOUT");
  }
}
