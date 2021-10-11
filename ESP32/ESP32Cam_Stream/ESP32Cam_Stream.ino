//https://stackoverflow.com/questions/60029614/esp32-cam-stream-in-opencv-python
#include "esp_camera.h"
#include <WebServer.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <EEPROM.h>
#include "soc/soc.h"           // Disable brownour problems
#include "soc/rtc_cntl_reg.h"  // Disable brownour problems
#include "driver/rtc_io.h"
#include <SPIFFS.h>
#include "camera_pin.h"

// DEFINE WIFI
const char *SSID = "Blynk"; // "BenMur";
const char *PWD =  "12345678"; //"MurBen3128";
String hostname = "ESPLENS0";

// TRIGGER
#define LED_PIN 33
#define FLASH_PIN 4
#define TRIGGER_PIN 4
#define TRIGGER_PHOTO_NAME "/photo.jpg"

WebServer server(80);

char buffer[2500];
DynamicJsonDocument jsonDocument(2048);


// camera settings
  // OV2640 camera module
  camera_config_t config;

  
// loRes => FRAMESIZE_QVGA
// hiRes => FRAMESIZE_SVGA
// rawRes => FRAMESIZE_UXGA

// EEPROM
int addr_id = 0;
int setup_id = 0;

String identifier = "OMNISCOPE_1";


// Triggered image to SPIFFS
void IRAM_ATTR trigger_image() {
  capturePhotoSaveSpiffs();
}

void setup()
{
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); //disable brownout detector

  Serial.begin(115200);
  Serial.println("Spinning Up Microscope");

  // EEPROM
  EEPROM.begin(512);
  EEPROM.get(addr_id, setup_id);
  Serial.println("SETUP ID is: " + String(setup_id));

  // visualize Power available
  pinMode(FLASH_PIN, OUTPUT);
  digitalWrite(FLASH_PIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);
  digitalWrite(FLASH_PIN, LOW);   // turn the LED on (HIGH is the voltage level)

  // Initiliaze Camera
  setupCam();

  // Initialize Wifi
  Serial.println("setting up WIFI");
  connectToWiFi();

  Serial.println("setting up SERVER");
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam-lo.jpg");
  Serial.println("  /cam-hi.jpg");
  Serial.println("  /cam-raw.jpg");

  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/cam-raw.jpg", handleJpgRaw);
  server.on("/cam.jpg", handleJpg);
  server.on("/restart", handleRestart);
  server.on("/led", HTTP_POST, set_led);
  server.on("/getID", HTTP_GET, get_ID);
  server.on("/setID", HTTP_POST, set_ID);
  server.on("/omniscope", HTTP_GET, handleIdentification);
  server.begin();

  // handle HW trigger
  Serial.println("setting up Trigger");
  //pinMode(TRIGGER_PIN, INPUT_PULLUP);
  //attachInterrupt(TRIGGER_PIN, trigger_image, RISING);
  //digitalWrite(TRIGGER_PIN, LOW);
  //rtc_gpio_hold_dis(GPIO_NUM_4);

  // Start SPIFFS to save triggered image
  Serial.println("setting up SPIFFS");
  if (!SPIFFS.begin(true)) {
    Serial.println("An Error has occurred while mounting SPIFFS");
    ESP.restart();
  }
  else {
    delay(500);
    Serial.println("SPIFFS mounted successfully");
  }

}

void loop()
{
  server.handleClient();
}


void connectToWiFi() {
  Serial.print("Connecting to ");
  Serial.println(SSID);
  WiFi.mode(WIFI_STA);
  WiFi.config(INADDR_NONE, INADDR_NONE, INADDR_NONE, INADDR_NONE);
  WiFi.setHostname(hostname.c_str()); //define hostname
  WiFi.begin(SSID, PWD);

  int notConnectedCounter = 0;

  Serial.print("Wifi connecting...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.println(".");
    notConnectedCounter++;
    if (notConnectedCounter > 50) { // Reset board if not connected after 5s
      Serial.println("Resetting due to Wifi not connecting...");
      ESP.restart();
    }
  }

  Serial.print("Connected. IP: ");
  Serial.println(WiFi.localIP());
}



void serveJpg()
{
  camera_fb_t * frame = NULL;
  frame = esp_camera_fb_get();
  esp_camera_fb_return(frame);
  server.send(200, "image/jpeg");
  server.client().write((char *)frame->buf, frame->len);
  /*
    server.setContentLength(frame->size());
    server.send(200, "image/jpeg");
    WiFiClient client = server.client();
    frame->writeTo(client);
  */
}

void handleJpgLo()
{
  if (esp_camera_init(&config) == ESP_OK)
    serveJpg();
}

void handleJpgHi()
{
  config.frame_size = FRAMESIZE_SVGA;
  if (esp_camera_init(&config) == ESP_OK)
    serveJpg();
}

void handleJpgRaw()
{
  config.frame_size = FRAMESIZE_UXGA;
  if (esp_camera_init(&config) == ESP_OK)
    serveJpg();
}

void handleJpg()
{
  server.sendHeader("Location", "/cam-hi.jpg");
  server.send(302, "", "");
}

void handleRestart() {
  ESP.restart();
}

void set_led() {
  if (server.hasArg("plain") == false) {
    //handle error here
  }
  String body = server.arg("plain");
  deserializeJson(jsonDocument, body);

  // Get RGB components
  int led_value = jsonDocument["value"];
  Serial.print("LED: ");
  Serial.print(led_value);
  digitalWrite(LED_PIN, led_value);   // turn the LED on (HIGH is the voltage level)

  // Respond to the client
  server.send(200, "application/json", "{}");
}

void get_ID() {
  EEPROM.get(addr_id, setup_id);
  Serial.println("Old EEPROM value is: " + String(setup_id));


  Serial.print("setup_id: ");
  Serial.print(setup_id);

  // Respond to the client
  server.send(200, "application/json", String(setup_id));
}


void set_ID() {
  String body = server.arg("plain");
  deserializeJson(jsonDocument, body);

  // Get RGB components
  setup_id = (int)jsonDocument["value"];
  EEPROM.put(addr_id, setup_id);
  EEPROM.commit();

  Serial.print("setup_id: ");
  Serial.print(setup_id);

  // Respond to the client
  server.send(200, "application/json", "{}");
}

void handleIdentification() {
  server.send(200, "application/json", identifier);
}


// Check if photo capture was successful
bool checkPhoto( fs::FS &fs ) {
  File f_pic = fs.open( TRIGGER_PHOTO_NAME );
  unsigned int pic_sz = f_pic.size();
  return ( pic_sz > 100 );
}

// Capture Photo and Save it to SPIFFS
void capturePhotoSaveSpiffs( void ) {
  camera_fb_t * fb = NULL; // pointer
  bool ok = 0; // Boolean indicating if the picture has been taken correctly

  do {
    // Take a photo with the camera
    Serial.println("Taking a photo...");

    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      return;
    }

    // Photo file name
    Serial.printf("Picture file name: %s\n", TRIGGER_PHOTO_NAME);
    File file = SPIFFS.open(TRIGGER_PHOTO_NAME, FILE_WRITE);

    // Insert the data in the photo file
    if (!file) {
      Serial.println("Failed to open file in writing mode");
    }
    else {
      file.write(fb->buf, fb->len); // payload (image), payload length
      Serial.print("The picture has been saved in ");
      Serial.print(TRIGGER_PHOTO_NAME);
      Serial.print(" - Size: ");
      Serial.print(file.size());
      Serial.println(" bytes");
    }
    // Close the file
    file.close();
    esp_camera_fb_return(fb);

    // check if file has been correctly saved in SPIFFS
    ok = checkPhoto(SPIFFS);
  } while ( !ok );
}

void setupCam() {
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 100;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 100;
    config.fb_count = 1;
  }

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    ESP.restart();
  }
}
