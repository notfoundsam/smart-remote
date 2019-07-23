#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// Radio setting
RF24 radio(9, 10); // For nano pin 9 and 10
// int radioSpeedPin = 2;
// int radioChannelPin1 = 3;
// int radioChannelPin2 = 4;
int radio_retries = 15;
int radio_delay = 10;

uint8_t radio_id = 51;

// LED settings
// int led_pin_blue = A1;
// int led_pin_red = A2;

void setup() {
  delay(3000); // Sleep 3s before loop.

  // pinMode(LED_BUILTIN, OUTPUT);
  // pinMode(led_pin_red, OUTPUT);
  // pinMode(led_pin_blue, OUTPUT);
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
}

void loop() {
  if (radio.available()) {
    byte payload[32];
    radio.read(&payload, sizeof(payload));

    if (payload[0] == radio_id && payload[1] == 48) {
      sendACK(radio_id);

      // If recive IR signal (it starts with i)
      if (payload[2] == 105) {
        // Serial.println("ir");
        // readIrSignal(payload);
      }
      // If recive comand (it starts with c)
      else if (payload[2] == 99) {
        // Serial.println("c");
        readCommand(payload);
      } else {
        Serial.println("wtf1");
      }
    }
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

  while (millis() - started_at <= radio_retries * radio_delay) {
    if (radio.available()) {
      radio.read(&data, sizeof(data));

      if (data[0] != radio_id) {
        Serial.println("wtf2");
        continue;
      }
      
      sendACK(radio_id);
      started_at = millis();


      if (data[0] == 48) {
        started_at = millis();
      } else {
        Serial.println("same package");
      }
    }
  }

  if (strcmp(buffer, "led_on") == 0) {
    // digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("led_on");
  } else if (strcmp(buffer, "led_off") == 0) {
    // digitalWrite(LED_BUILTIN, LOW);
    Serial.println("led_off");
  } else if (strcmp(buffer, "empty") == 0) {
    // Serial.println("go to sleep");
    // sendStatus();
    // return;
  } else {
    // unsupportedCommand();
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

void sendACK(uint8_t radio_node) {
  uint8_t ack[2];
  ack[0] = radio_node;
  ack[1] = 6;
  radio.stopListening();
  radio.writeFast(ack, sizeof(ack));
  radio.txStandBy();
  radio.startListening();
}
