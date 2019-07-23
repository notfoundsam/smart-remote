#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
RF24 radio(9, 10);
uint8_t radio_retries = 15;
uint8_t radio_delay = 10;

bool isRadioSeted = true;

void setup() {
  Serial.begin(500000);
  Serial.setTimeout(50);
  radio.begin();
  delay(100);

  radio.powerUp();
  radio.setChannel(90);

  radio.setAutoAck(false); // Disable hardware ACK, use program ACK

  radio.setPayloadSize(32);
  radio.setCRCLength(RF24_CRC_8);
  radio.setDataRate(RF24_1MBPS);     // (RF24_250KBPS, RF24_1MBPS, RF24_2MBPS)
  radio.setPALevel(RF24_PA_MAX);       // (RF24_PA_MIN=-18dBm, RF24_PA_LOW=-12dBm, RF24_PA_HIGH=-6dBm, RF24_PA_MAX=0dBm)
  radio.openWritingPipe(0xAAAAAAAA11LL);
  radio.openReadingPipe(1, 0xAAAAAAAA22LL);
  radio.startListening();
}

void setupRadio() {
  if (isRadioSeted) {
    radio.stopListening();
  }

  uint8_t sum = 0;
  uint8_t channel;
  uint8_t crc_length;
  uint8_t data_rate;
  uint8_t pa_level;
  uint64_t w_pipe;
  uint64_t r_pipe;
}

void loop() {
  uint8_t b = 18;
  if (Serial.available() > 0) {
    // b = Serial.read();
    readSerial(b);
  }

  if (isRadioSeted) {
    recive();
  }
}

void readSerial(uint8_t type) {
  bool setup_mode = false;
  // max size 300 bytes
  bool serial_timeout = true;
  uint8_t serial_buff[300];
  uint16_t serial_buff_index = 0;
  // Serial buffer size is 64 bytes
  uint8_t serial_chank_index = 0;

  uint8_t radio_buff[32];
  uint8_t radio_buff_index = 0;
  uint8_t radio_package = 48;

  uint8_t b;

  unsigned long started_waiting_at = millis();
  
  while (millis() - started_waiting_at < 100) {
    if (Serial.available() == 0) {
      continue;
    }

    b = Serial.read();

    serial_chank_index++;

    // Radio transmit mode
    if (type == 18 && radio_buff_index == 0) {
      radio_buff[0] = b;
      radio_buff_index = 2;
      continue;
    }

    serial_buff[serial_buff_index] = b;
    serial_buff_index++;

    if (b == 10) {
      Serial.print(":ack:\n");
      serial_timeout = false;
      break;
    }

    if (serial_chank_index == 64) {
      Serial.print(":next:\n");
      serial_chank_index = 0;
      continue;
      // recive();
    }

    if (serial_buff_index == 299) {
      Serial.print(":overflow:\n");
      return;
    }

    // recive();
  }
  
  if (serial_timeout) {
    Serial.print("\n:timeout:\n");
    return;
  }

  // Radio transmit mode
  if (type == 18) {
    radio_buff[1] = radio_package;

    for (uint16_t i = 0; i < serial_buff_index; i++) {
      radio_buff[radio_buff_index] = serial_buff[i];
      radio_buff_index++;

      if (radio_buff_index == 32 || serial_buff[i] == 10) {
        if (!sendWithACK(radio_buff, radio_buff_index)) {
          Serial.print(":fail:\n");
          return;
        }

        radio_buff_index = 2;
        radio_package++;
        radio_buff[1] = radio_package;
      }
    }
  } else if (type == 17) {
    // Setup mode
    setupRadio();
  }

  Serial.print(":success:\n");
}

void recive() {
  uint8_t payload[32];

  if (radio.available()) {
    radio.read(&payload, sizeof(payload));

    // Send ACK to current radio node
    sendACK(payload[0]);

    for (uint8_t j = 0; j < sizeof(payload); j++) {
      if (payload[j] == 10) {
        Serial.write(23);
        break;
      }

      Serial.write(payload[j]);
    }

    Serial.write(10);
  }
}

boolean sendWithACK(uint8_t *data, uint8_t size) {
  uint8_t response[32];
  unsigned long ack_started_at;

  for (uint8_t i = 0; i <= radio_retries; i++) {
    radio.stopListening();
    radio.writeFast(data, size);
    radio.txStandBy();
    radio.startListening();

    ack_started_at = millis();
    
    // Wait for responce
    while (millis() - ack_started_at <= radio_delay) {
      if (radio.available()) {
        radio.read(&response, sizeof(response));
        
        if (data[0] == response[0] && response[1] == 6) {
          return true;
        }

        // Send ACK to current radio node
        sendACK(response[0]);

        for (uint8_t j = 0; j < sizeof(response); j++) {
          if (response[j] == 10) {
            Serial.write(23);
            break;
          }

          Serial.write(response[j]);
        }

        Serial.write(10);
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

void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
}

uint64_t getUInt64fromHex(char const *str)
{
  uint64_t accumulator = 0;
  
  for (size_t i = 0 ; isxdigit((unsigned char)str[i]) ; ++i) {
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
