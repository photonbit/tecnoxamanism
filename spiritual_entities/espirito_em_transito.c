#include <Adafruit_NeoPixel.h>
#include <bluefruit.h>

#include <Adafruit_Sensor_Calibration.h>
#include <Adafruit_AHRS.h>

Adafruit_Sensor *accelerometer, *gyroscope, *magnetometer;

// uncomment one combo 9-DoF!
#include "LSM6DS_LIS3MDL.h"  // can adjust to LSM6DS33, LSM6DS3U, LSM6DSOX...
//#include "LSM9DS.h"           // LSM9DS1 or LSM9DS0
//#include "NXP_FXOS_FXAS.h"  // NXP 9-DoF breakout

// pick your filter! slower == better quality output
// Adafruit_NXPSensorFusion filter; // slowest
//Adafruit_Madgwick filter;  // faster than NXP
Adafruit_Mahony filter;  // fastest/smallest

#if defined(ADAFRUIT_SENSOR_CALIBRATION_USE_EEPROM)
  Adafruit_Sensor_Calibration_EEPROM cal;
#else
  Adafruit_Sensor_Calibration_SDFat cal;
#endif

#define FILTER_UPDATE_RATE_HZ 200
#define PRINT_EVERY_N_UPDATES 1
//#define AHRS_DEBUG_OUTPUT

uint32_t timestamp;

#define NEOPIXEL_PIN 8
#define NUMPIXELS    1

Adafruit_NeoPixel pixels(NUMPIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
BLEUart bleuart;  // BLE UART service

enum State {
  INERT,
  DORMANT,
  INTERESTED,
  ACTIVATED,
  INTEGRATED
};

State state = INERT; // Initialize state
uint32_t color = pixels.Color(255, 0, 0); // Default color: Red
unsigned long previousMillis = 0;
unsigned long lastCrossFade = 0;
int crossFadeStep = 0;

void setup() {
  pixels.begin(); // Initialize the NeoPixel library.
  if (!init_sensors()) {
    Serial.println("Failed to find sensors");
    while (1) delay(10);
  }

  setup_sensors();
  filter.begin(FILTER_UPDATE_RATE_HZ);
  timestamp = millis();
  setupBLE();
}

void loop() {
  blinkNeopixel(state, color);

  // Handle incoming BLE data
  while (bleuart.available()) {
    String bleData = bleuart.readString();
    Serial.print(bleData);
    handleIncomingData(bleData);
  }

  sendSensorData(); // Uncomment to send sensor data
}

void setupBLE() {
  Bluefruit.begin();
  Bluefruit.setName("Espirito");
  Bluefruit.setAppearance(0x0203);
  Bluefruit.Periph.setConnectCallback(connect_callback);
  Bluefruit.Periph.setDisconnectCallback(disconnect_callback);

  bleuart.begin();

  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  Bluefruit.Advertising.addService(bleuart);
  Bluefruit.Advertising.addName();
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.start(0);
}


void sendSensorData() {
  float gx, gy, gz;
  static uint8_t counter = 0;

  if ((millis() - timestamp) < (1000 / FILTER_UPDATE_RATE_HZ)) {
    return;
  }
  timestamp = millis();
  // Read the motion sensors
  sensors_event_t accel, gyro, mag;
  accelerometer->getEvent(&accel);
  gyroscope->getEvent(&gyro);
  magnetometer->getEvent(&mag);

  cal.calibrate(mag);
  cal.calibrate(accel);
  cal.calibrate(gyro);
  // Gyroscope needs to be converted from Rad/s to Degree/s
  // the rest are not unit-important
  gx = gyro.gyro.x * SENSORS_RADS_TO_DPS;
  gy = gyro.gyro.y * SENSORS_RADS_TO_DPS;
  gz = gyro.gyro.z * SENSORS_RADS_TO_DPS;

  // Update the SensorFusion filter
  filter.update(gx, gy, gz,
                accel.acceleration.x, accel.acceleration.y, accel.acceleration.z,
                mag.magnetic.x, mag.magnetic.y, mag.magnetic.z);
  // reset the counter
  counter = 0;

  char quaternionData[40];
  float qw, qx, qy, qz;
  filter.getQuaternion(&qw, &qx, &qy, &qz);

  sprintf(quaternionData, "%u,%.4f,%.4f", Blue, qw, qx);
  bleuart.print(quaternionData);
}

void blinkNeopixel(State state, uint32_t color) {
  unsigned long currentMillis = millis();
  static long interval = 0;

  switch (state) {
    case DORMANT:
      interval = 1000;
      break;
    case INTERESTED:
      interval = 500;
      break;
    default:
      interval = 0;
      break;
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
    handleNonBlinkingStates(state, color);
  }
}

void handleNonBlinkingStates(State state, uint32_t color) {
  switch (state) {
    case ACTIVATED:
      pixels.setPixelColor(0, color);
      break;
    case INERT:
      pixels.clear();
      break;
    case INTEGRATED:
      crossFade(color);
      break;
    default:
      break;
  }
  pixels.show();
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

        if (newState == "inert") {
          state = INERT;
        } else if (newState == "dormant") {
          state = DORMANT;
        } else if (newState == "interested") {
          state = INTERESTED;
        } else if (newState == "activated") {
          state = ACTIVATED;
        } else if (newState == "integrated") {
          state = INTEGRATED;
        }
        previousMillis = millis(); // Reset the timer for immediate effect
    }
}

void connect_callback(uint16_t conn_handle) {
    // Connection established
    Bluefruit.Advertising.stop(); // Stop advertising

    // Manually blink LED twice
    for (int i = 0; i < 4; i++) {
        if (i % 2 == 0) {
            pixels.setPixelColor(0, color); // Turn LED on
        } else {
            pixels.clear(); // Turn LED off
        }
        pixels.show();
        if (i < 3) {
            delay(150); // Delay for both 'on' and 'off' states
        }
    }
}

void disconnect_callback(uint16_t conn_handle, uint8_t reason) {
    // Connection disconnected
    Bluefruit.Advertising.start(0); // Restart advertising indefinitely
    state = INERT; // Reset the state to inert
}

