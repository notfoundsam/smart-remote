#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(9, 10);
unsigned short index = 0;
unsigned char packageEnd = '\n';
int radio_retries = 20;

uint64_t pipes[5] = {
  0xAABBCCDD11LL,
  0xAABBCCDD22LL,
  0xAABBCCDD33LL,
  0xAABBCCDD44LL,
  0xAABBCCDD55LL,
};

// uint64_t responce_address = 0xAABBCCDD55LL;

unsigned long started_waiting_at;               // Set up a timeout period, get the current microseconds
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
  radio.setAutoAck(1);
  // radio.openReadingPipe(1, responce_address);
  radio.startListening();
  Serial.print("Loaded\n");
}

void loop() {
  if (Serial.available() > 0) {
    isSucces = false;
    radio.stopListening();

    readSerial();
    if (isSucces) {
      Serial.print("OK\n");
    } else {
      Serial.print("FAIL\n");
    }

    timeout = false;
    index = 0;

    radio.startListening();
  }
}

void readSerial() {
  unsigned short code;
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
    return;
  } else {
    if (portSignal[0] == 105) {
      // If recive IR signal (it starts with i)
      irSignal(portSignal);
    } else if (portSignal[0] == 99) {
      // If recive comand (it starts with c)
      command(portSignal);
    }
  }
}

void command(byte *signal) {
  int b;
  setWritingPipe(signal[1]);

  if (!sendSignal(99)) {
    Serial.print(":99fail");
    return;
  }

  for (int i = 3; i < index; i++) {
    b = signal[i];
    
    if (b == 10) {
      if (sendSignal(10)) {
        delay(30);
        setReadingPipe(signal[1]);
        radio.startListening();
        // delay(20);
        radio.flush_rx();
        waitResponce();
      } else {
        Serial.print(":10fail");
      }
    } else {
      if (!sendSignal(b)) {
        Serial.print(":bfail");
        return;
      }
    }
  }
}

void irSignal(byte *signal) {
  byte b;
  char strBuffer[20];
  byte strIndex = 0;

  setWritingPipe(signal[1]);

  if (!sendSignal(105)) {
    return;
  }
  
  for (int i = 3; i < index; i++) {
    b = signal[i];
    
    if (b > 47 && b < 58) {
      strBuffer[strIndex] = b;
      strIndex++;
    } else if (b == 32) {
      if (!sendSignal(atoi(strBuffer))) {
        return;
      }
      memset(strBuffer, 0, sizeof(strBuffer));
      strIndex = 0;
    } else if (b == 10) {
      if (sendSignal(10)) {
        isSucces = true;
        return;
      }
    }
  }
}

boolean sendSignal(int signal) {
  for (int i = 0; i < radio_retries; i++) {
    if (radio.write(&signal, sizeof(signal))) {
      return true;
    }
    delay(20);
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

// Set pipe to send signal
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

void waitResponce() {
  byte pipe;
  unsigned int index = 0;
  unsigned int signal;
  started_waiting_at = micros();
  timeout = true;

  // Wait 5 seconds for responce
  while (timeout == true && (micros() - started_waiting_at < 500000)) {
    if (radio.available(&pipe)) {
      if (pipe == 1) {
        started_waiting_at = micros();
        radio.read(&signal, sizeof(signal));
        if (signal == 10) {
          timeout = false;
          // ASCII symbol ":" before OK
          Serial.print(":");
          isSucces = true;
          return;
        } else {
          Serial.write(signal);
        }
      }
    }
  }
}
