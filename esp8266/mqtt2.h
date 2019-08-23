#include "EspMQTTClient.h"
#include <IRsend.h>

void onConnectionEstablished();

/*

EspMQTTClient client(
  "",                 // Wifi ssid
  "",                 // Wifi password
  onConnectionEstablished,// MQTT connection established callback
  "192.168.100.111"                    // MQTT broker ip
);
*/

#define MQTT_MAX_PACKET_SIZE 256

EspMQTTClient client(
  "",                      // Wifi ssid
  "",                      // Wifi password
  onConnectionEstablished, // Connection established callback
  "192.168.100.111",       // MQTT broker ip
  1883,                    // MQTT broker port
  "",                      // MQTT username
  "",                      // MQTT password
  "esp02",                 // Client name
  false,                   // Enable web updater
  false                    // Enable debug messages
);

const uint8_t IR_LED_PIN = 4;  // ESP8266 GPIO pin to use. Recommended: 4 (D2).
const uint8_t RED_LED_PIN = 0;  // ESP8266 GPIO pin to use.

const uint8_t RED_ON_CODE = 11;
const uint8_t RED_OFF_CODE = 10;

IRsend irsend(IR_LED_PIN);  // Set the GPIO to be used to sending the message.

// uint16_t raw_signal[400];

void setup()
{
  pinMode(RED_LED_PIN, OUTPUT);
  digitalWrite(RED_LED_PIN, LOW);
  irsend.begin();
  Serial.begin(115200);
}

void onConnectionEstablished()
{
  // Subscribe to "mytopic/test" and display received message to Serial
  client.subscribe("alexa/esp1/red_led", [](const String & command) {
    uint16_t rsize = command.length();
    char buffer[rsize+1];

    for (int i = 0; i < rsize; i++) {
      buffer[i] = command[i];
    }

    int code = atoi(buffer);

    if (code == RED_ON_CODE) {
      digitalWrite(RED_LED_PIN, HIGH);
      Serial.println("LED ON");
    } else if (code == RED_OFF_CODE) {
      digitalWrite(RED_LED_PIN, LOW);
      Serial.println("LED OFF");
    }
  });

  // Subscribe to "mytopic/test" and display received message to Serial
  client.subscribe("alexa/esp1/ir", [](const String & code) {
    // Serial.println("ir");
    if (code[0] != 50) {
      return;
    }
    // Serial.println("start");

    int zero = 0;
    int one = 0;
    char buffer[5];
    byte buffer_index = 0;
    boolean bit_code = false;
    uint16_t raw_signal[300];
    int raw_index = 0;

    // Setup zero length
    buffer[0] = code[1];
    buffer[1] = code[2];
    buffer[2] = code[3];
    buffer[3] = '\0';
    zero = atoi(buffer);
    memset(buffer, 0, sizeof(buffer));

    // Setup one length
    buffer[0] = code[5];
    buffer[1] = code[6];
    buffer[2] = code[7];
    buffer[3] = code[8];
    buffer[4] = '\0';
    one = atoi(buffer);
    memset(buffer, 0, sizeof(buffer));
    uint16_t rsize = code.length();

    for (int i = 10; i < rsize; ++i)
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
        } else if (code[i] == 32 && buffer_index > 0) {
          raw_signal[raw_index] = atoi(buffer);
          raw_index++;
          memset(buffer, 0, sizeof(buffer));
          buffer_index = 0;
        } else if (code[i] == 10) {
          raw_signal[raw_index] = atoi(buffer);
          break;
        }
      }
    }

    // Serial.println(code);
    // Serial.println(rsize);
    irsend.sendRaw(raw_signal, raw_index, 38);
  });

  // Publish a message to "mytopic/test"
  // client.publish("test/one", "This is a message");

  // Execute delayed instructions
  // client.executeDelayed(5 * 1000, []() {
  //   client.publish("test/one", "This is a message sent 5 seconds later");
  // });
}

void loop()
{
  client.loop();
}