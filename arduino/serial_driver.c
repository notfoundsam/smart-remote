#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(9, 10);
int index = 0;
int radio_retries = 1;
int radio_delay = 20;

uint64_t pipes[5] = {
  0xAABBCCDD11LL,
  0xAABBCCDD22LL,
  0xAABBCCDD33LL,
  0xAABBCCDD44LL,
  0xAABBCCDD55LL,
};

unsigned long started_waiting_at;               // Set up a timeout period, get the current microseconds
unsigned long responce_started_at;               // Set up a timeout period, get the current microseconds
boolean timeout = false;
boolean isSucces = false;

void setup() {
  Serial.begin(500000);
  Serial.setTimeout(50);
  
  radio.begin();
  delay(1000);
  radio.powerUp();
  radio.setChannel(75);
  radio.setRetries(15,15);
  radio.setDataRate(RF24_1MBPS);     // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);       // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  // radio.setPayloadSize(1);
  // radio.setAutoAck(1);
  radio.openReadingPipe(2, 0xAABBCCDD55LL);
  radio.startListening();
  Serial.print("Loaded\n");
}

void loop() {
  if (Serial.available() > 0) {
    isSucces = false;
    radio.stopListening();

    readSerial();
    if (isSucces) {
      Serial.print(":OK\n");
    } else {
      radio.startListening();
      delay(50);
      Serial.print(":FAIL\n");
    }

    timeout = false;
    index = 0;
  }
}

void readSerial() {
  byte code;
  byte portSignal[3000];
  timeout = true;
  started_waiting_at = micros();
  
  while (timeout == true && (micros() - started_waiting_at < 200000)) {
    if (Serial.available() > 0) {
      started_waiting_at = micros();
      
      code = Serial.read();
      portSignal[index] = code;
      index++;
      if (code == 10) {
        timeout = false;
        break;
      }
    }
  }
  
  if (timeout) {
    Serial.print("SERIAL READ TIMEOUT");
    return;
  } else {
    transmitSignal(portSignal);
  }
}

void transmitSignal(byte *signal) {
  int b;
  setWritingPipe(signal[1]);
  Serial.print("-");

  for (int i = 0; i < index; i++) {
    b = signal[i];

    if (i == 1) {
      continue;
    }

    if (b != 10) {
      Serial.write(b);
    }
    // delay(100);
    if (!sendSignal(b)) {
      Serial.print("RADIO TRANSMIT SIGNAL");
      Serial.write(b);
      return;
    }
    
    if (b == 10) {
      // This delay is necessary
      delay(30);
      // setReadingPipe(signal[1]);
      // radio.startListening();
      waitForResponce();
      // isSucces = true;
    }
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
  responce_started_at = micros();
  timeout = true;

  byte b;
  byte buffer[200];
  int bufer_index = 0;

  radio.startListening();

  // Wait 2 seconds for responce
  while (timeout == true && (micros() - responce_started_at < 2000000)) {
    if (radio.available(&pipe)) {
      if (pipe == 2) {
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
    // Some error are here
    Serial.print("RADIO RESPONCE TIMEOUT");
  }
}
