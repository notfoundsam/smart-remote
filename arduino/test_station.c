#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// Radio setting
RF24 radio(9, 10); // For nano pin 9 and 10

int radio_retries = 10;
int radio_delay = 10;

uint8_t radio_id = 51;
unsigned long status_timer;

void setup() {
  delay(3000); // Sleep 3s before loop.

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
      // delay(250);
      sendACK();
      Serial.println("fp ack");

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


  // Send status periodically
  if (millis() - status_timer > 5000) {
    sendStatus();
    status_timer = millis();
  }
}

void readCommand(uint8_t *code) {
  uint8_t payload[32];
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
      radio.read(&payload, sizeof(payload));

      if (payload[0] != radio_id) {
        Serial.println("wtf2");
        continue;
      }
      
      sendACK();
      started_at = millis();

      if (payload[1] == 48) {
        Serial.println("same package");
        started_at = millis();
      }
    }
  }

  if (strcmp(buffer, "led_on") == 0) {
    Serial.println("led_on");
  } else if (strcmp(buffer, "led_off") == 0) {
    Serial.println("led_off");
  } else {
    Serial.println("unknown command");
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

void sendStatus() {
  uint8_t radio_buff[32];
  uint8_t radio_buff_index = 2;
  uint8_t radio_package = 48;

  // Max payload size in one package is 32 bytes
  String payload = "tp ev,";
  payload += "h ";
  payload += "50.00";
  payload += ",t ";
  payload += "26.50";
  payload += ",p ";
  payload += "1010.00";
  payload += ",b ";
  payload += "4.12";
  payload += "\n";

  int rsize = payload.length();

  radio_buff[0] = radio_id;
  radio_buff[1] = radio_package;

  for (int i = 0; i < rsize; i++) {
    radio_buff[radio_buff_index] = payload[i];
    radio_buff_index++;

    if (radio_buff_index == 32 || payload[i] == 10) {
      radio_buff[1] = radio_package;

      for (int j = 0; j < radio_buff_index; j++) {
        Serial.write(radio_buff[j]);
      }
      Serial.print("\n");

      if (!sendWithACK(radio_buff, radio_buff_index)) {
        Serial.print("fail\n");
        return;
      } else {
        // delay(15);
        Serial.print("success\n");
      }

      radio_package++;
      radio_buff_index = 2;
    }
  }
}

boolean sendWithACK(uint8_t *data, uint8_t size) {
  byte response[32];
  unsigned long ack_started_at;

  for (uint8_t i = 0; i <= radio_retries; i++) {
    radio.stopListening();
    radio.writeFast(data, size);
    radio.txStandBy();
    radio.startListening();

    ack_started_at = millis();
    // Wait 15ms for responce
    while (millis() - ack_started_at <= radio_delay) {
      if (radio.available()) {
        Serial.print("came\n");
        radio.read(&response, sizeof(response));

        if (data[0] == response[0] && response[1] == 6) {
          return true;
        }
      }
    }
    Serial.print(".");
  }

  return false;
}

void sendACK() {
  uint8_t ack[2];
  ack[0] = radio_id;
  ack[1] = 6;
  radio.stopListening();
  radio.writeFast(ack, sizeof(ack));
  radio.txStandBy();
  radio.startListening();
}
