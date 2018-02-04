#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(9, 10);
unsigned short index = 0;
unsigned char packageEnd = '\n';
unsigned short code;
char strBuffer[20];
byte strIndex = 0;
int radio_retries = 20;

uint64_t pipes[5] = {
  0xAABBCCDD11LL,
  0xAABBCCDD22LL,
  0xAABBCCDD33LL,
  0xAABBCCDD44LL,
  0xAABBCCDD55LL,
};

unsigned long started_waiting_at;               // Set up a timeout period, get the current microseconds
boolean timeout = false;
boolean isEnded = false;

void setup() {
  Serial.begin(500000);
  Serial.setTimeout(50);
  
  radio.begin();
  delay(1000);
  radio.powerUp();
  radio.setChannel(75);
  radio.setRetries(15,15);
  radio.setDataRate(RF24_250KBPS);     // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);       // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.setAutoAck(1);
  // radio.openWritingPipe(0xAABBCCDD11LL);
  // radio.openWritingPipe(0xF0F0F0F0AALL);
  radio.startListening();
  Serial.print("Loaded\n");
}

void loop() {
  if (Serial.available() > 0) {
    radio.stopListening();

    if (!readSerial()) {
      Serial.print("FAIL\n");
    } else {
      Serial.print("OK\n");
    }

    timeout = false;
    index = 0;

    radio.startListening();
  }
}

boolean readSerial() {
  byte portSignal[1000];
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
    return false;
  } else {
    // If recive IR signal (it starts with i)
    if (portSignal[0] == 105) {
      return irSignal(portSignal);
    }

    return false;
  }
}

boolean irSignal(byte *signal) {
  byte b;
  int count = 0;

  // FIX ME Move to db
  // Set pipe to send signal
  if (signal[1] == 49) {
    radio.openWritingPipe(pipes[0]);
  } else if (signal[1] == 50) {
    radio.openWritingPipe(pipes[1]);
  } else if (signal[1] == 51) {
    radio.openWritingPipe(pipes[2]);
  } else if (signal[1] == 52) {
    radio.openWritingPipe(pipes[3]);
  } else if (signal[1] == 53) {
    radio.openWritingPipe(pipes[4]);
  }
  
  for (int i = 3; i < index; i++) {
    b = signal[i];
    
    if (b > 47 && b < 58) {
      strBuffer[strIndex] = b;
      strIndex++;
    } else if (b == 32) {
      count++;
      if (!sendSignal(atoi(strBuffer), false)) {
        clearBuffer();
        return false;
      }
      clearBuffer();
    } else if (b == 10) {
      if (!sendSignal(10, true)) {
        return false;
      }
    }
  }

  return true;
}

boolean sendSignal(int code, boolean end) {
  for (int i = 0; i < radio_retries; i++) {
    if (end) {
      if (radio.write(&packageEnd, sizeof(packageEnd))) {
        return true;
      }
    } else {
      if (radio.write(&code, sizeof(code))) {
        return true;
      }
    }
  }
  
  return false;
}

void clearBuffer() {
  memset(strBuffer, 0, sizeof(strBuffer));
  strIndex = 0;
}
