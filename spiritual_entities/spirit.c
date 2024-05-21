#include <Adafruit_NeoPixel.h>
#include <bluefruit.h>

#define NEOPIXEL_PIN 8
#define NUMPIXELS    1

Adafruit_NeoPixel pixels(NUMPIXELS, NEOPIXEL_PIN, NEOGRB + NEO_KHZ800);
BLEUart bleuart;  // BLE UART service

String state = "inert";
uint32_t color = pixels.Color(255, 0, 0); // Default color: Red
unsigned long previousMillis = 0;
unsigned long lastCrossFade = 0;
int crossFadeStep = 0;

void setup() {
  pixels.begin(); // Initialize the NeoPixel library.
  setupBLE();
}

void loop() {
  blinkNeopixel(state, color);

  // Handle incoming BLE data
  while (bleuart.available()) {
    String bleData = bleuart.readStringUntil('\n');
    handleIncomingData(bleData);
  }

  // Add your sensor data reading and sending here
  // sendSensorData();
}

void setupBLE() {
  Bluefruit.begin();
  Bluefruit.setName("MyFeatherSense");  // Set your custom name here
  Bluefruit.Periph.setConnectCallback(connect_callback);
  Bluefruit.Periph.setDisconnectCallback(disconnect_callback);

  bleuart.begin();

  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  Bluefruit.Advertising.addService(bleuart);
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.start(0);  // Start advertising forever
}

void blinkNeopixel(String state, uint32_t color) {
  unsigned long currentMillis = millis();
  static long interval = 0;

  if (state == "dormant") {
    interval = 1000;
  } else if (state == "interested") {
    interval = 500;
  } else {
    interval = 0; // No blinking for other states
  }

  if (interval > 0 && currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (pixels.getPixelColor(0) == color) {
      pixels.clear();
    } else {
      pixels.setPixelColor(0, color);
    }
    pixels.show();
  } else if (interval == 0) {
    if (state == "activated") {
      pixels.setPixelColor(0, color);
    } else if (state == "inert") {
      pixels.clear();
    } else if (state == "integrated") {
      crossFade(color);
    }
    pixels.show();
  }
}

void crossFade(uint32_t color) {
  unsigned long currentMillis = millis();
  if (currentMillis - lastCrossFade >= 10) {
    lastCrossFade = currentMillis;
    uint32_t oppositeColor = ~color;
    uint32_t mixedColor = mixColors(color, oppositeColor, crossFadeStep);
    pixels.setPixelColor(0, mixedColor);
    pixels.show();

    crossFadeStep++;
    if (crossFadeStep > 255) {
      crossFadeStep = 0;
    }
  }
}

uint32_t mixColors(uint32_t color1, uint32_t color2, int weight) {
  int red1 = (color1 >> 16) & 0xFF;
  int green1 = (color1 >> 8) & 0xFF;
  int blue1 = color1 & 0xFF;
  int red2 = (color2 >> 16) & 0xFF;
  int green2 = (color2 >> 8) & 0xFF;
  int blue2 = color2 & 0xFF;

  uint8_t redMix = (red1 * (255 - weight) + red2 * weight) / 255;
  uint8_t greenMix = (green1 * (255 - weight) + green2 * weight) / 255;
  uint8_t blueMix = (blue1 * (255 - weight) + blue2 * weight) / 255;

  return pixels.Color(redMix, greenMix, blueMix);
}

void handleIncomingData(String data) {
  if (data.startsWith("state:")) {
    String newState = data.substring(6);
    if (state != newState) {
      state = newState; // Update the state
      previousMillis = millis(); // Reset the timer for immediate effect
    }
  }
  // Handle color change...
  // Similar logic to handle color change as needed
}

// Callbacks for BLE events
void connect_callback(uint16_t conn_handle) {
  Bluefruit.Advertising.stop();

  // Manually blink LED twice
    for (int i = 0; i < 4; i++) {
        if (i % 2 == 0) {
            pixels.setPixelColor(0, color); // Turn LED on
        } else {
            pixels.clear(); // Turn LED off
        }
        pixels.show();
        delay(19); // Delay for both 'on' and 'off' states
    }
}

void disconnect_callback(uint16_t conn_handle, uint8_t reason) {
  Bluefruit.Advertising.start(0);  // Restart advertising indefinitely

  // Reset the state to inert
  state = "inert";
}

