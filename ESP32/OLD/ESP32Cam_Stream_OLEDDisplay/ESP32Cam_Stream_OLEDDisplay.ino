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

//https://unsinnsbasis.de/oled-display-ssd1306/
#include <Adafruit_SSD1306.h>
 
// großes Display am Standard-I2C-Interface
// (SDA Pin 21, SCL Pin 22)
#define DISPLAY_1_I2C_ADDRESS 0x7B // or 0x3D
#define DISPLAY_1_WIDTH 128  // Breite in Pixeln
#define DISPLAY_1_HEIGHT 64  // Höhe in Pixeln
#define I2C_2_SDA 12
#define I2C_2_SCL 13
// je I2C-Kanal ein Interface definieren
TwoWire I2C_1 = TwoWire(0);
 
// Datenstrukturen für die Displays
// (-1 -> Display hat keinen Reset-Pin)
Adafruit_SSD1306 display1(DISPLAY_1_WIDTH, DISPLAY_1_HEIGHT, &I2C_1, -1);
 
// Bitrate für die Datenübertragung zum seriellen Monitor
// (ESP: z.B. 115200, Arduino: zwingend 9600)
#define BITRATE 115200  // Arduino: 9600



// DEFINE WIFI
const char *SSID = "Blynk"; // "BenMur"; //
const char *PWD =  "12345678"; //"MurBen3128";//
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

// put stream into tasks so that it is non-blocking  // TODO?
/*(void*)&is_streaming;
xTaskCreate(
                    globalIntTask,             
                    "StreamingTask",           
                    10000,                     
                    (void*)&is_streaming,      
                    1,                         
                    NULL);                     
*/

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


  /*
   * Initiliaze Display
   */
  boolean status1;
     
  // beide I2C-Interfaces nutzen
  I2C_1.begin(I2C_2_SDA, I2C_2_SCL);  // Standard-Interface

  // Displays initialisieren
  // im Fehlerfall Meldung ausgeben und Programm nicht
  // fortsetzen (leere Dauerschleife))
  status1 = display1.begin(SSD1306_SWITCHCAPVCC, DISPLAY_1_I2C_ADDRESS);

  if (!(status1)) {
    Serial.println("Fehler beim Initialisieren der Displays");
    Serial.print("Status Display 1: ");
    Serial.print(status1);
  }

  display1.clearDisplay();
  display1.setTextSize(2);  // große Schrift
  display1.setTextColor(SSD1306_WHITE); // helle Schrift auf dunklem Grund
  display1.setCursor(0, 0);
  display1.print("  Grosse\nBuchstaben\n  in vier\n  Zeilen");
  display1.display();

  /*
   * Camera Programm
   */

/*
  // visualize Power available
  delay(random(1000)); // Make sure that not all LEDs flash at the same time..
  pinMode(FLASH_PIN, OUTPUT);
  digitalWrite(FLASH_PIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(50);
  digitalWrite(FLASH_PIN, LOW);   // turn the LED on (HIGH is the voltage level)

  // Initiliaze Camera
  Serial.println("setting up camera");
  setupCam();

  // Initialize Wifi
  Serial.println("setting up WIFI");
  connectToWiFi();

  Serial.println("setting up SERVER");
  Serial.print("http://");
  Serial.println(WiFi.localIP());

 
  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/cam-raw.jpg", handleJpgRaw);
  server.on("/cam.jpg", handleJpg);
  server.on("/cam-stream.jpg", serve_jpg_stream);
  server.on("/cam-triggered.jpg", serve_triggered);
  server.on("/restart", handleRestart);
  server.on("/led", HTTP_POST, set_led);
  server.on("/flash", HTTP_POST, set_flash);
  server.on("/getID", HTTP_GET, get_ID);
  server.on("/setID", HTTP_POST, set_ID);
  server.on("/softtrigger", HTTP_POST, handleSoftTrigger);
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

  pinMode(TRIGGER_PIN, INPUT);
  */
}

boolean is_capture = true;
boolean trigger_state = false;
boolean trigger_state_last = false;


void loop()
{
  // should do an interrupt, but does not really work //TODO
  trigger_state = digitalRead(TRIGGER_PIN);

  if(is_capture or (trigger_state_last != trigger_state)){
    trigger_state_last = trigger_state; // rising edge
    capturePhotoSaveSpiffs(); 
    is_capture=false;
  }
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
    Serial.print(".");
    notConnectedCounter++;
    if (notConnectedCounter > 50) { // Reset board if not connected after 5s
      Serial.println("Resetting due to Wifi not connecting...");
      ESP.restart();
    }
  }

  Serial.print("Connected. IP: ");
  Serial.println(WiFi.localIP());
}


const char JHEADER[] = "HTTP/1.1 200 OK\r\n" \
                       "Content-disposition: inline; filename=capture.jpg\r\n" \
                       "Content-type: image/jpeg\r\n\r\n";
const int jhdLen = strlen(JHEADER);
const char HEADER[] = "HTTP/1.1 200 OK\r\n" \
                      "Access-Control-Allow-Origin: *\r\n" \
                      "Content-Type: multipart/x-mixed-replace; boundary=123456789000000000000987654321\r\n";
const char BOUNDARY[] = "\r\n--123456789000000000000987654321\r\n";
const char CTNTTYPE[] = "Content-Type: image/jpeg\r\nContent-Length: ";
const int hdrLen = strlen(HEADER);
const int bdrLen = strlen(BOUNDARY);
const int cntLen = strlen(CTNTTYPE);
                      
void serve_jpg_stream(void)
{ // https://github.com/krukmat/ESPtream/blob/5158e70a0551b07f695d1d9d138ee2d83d07958a/StreamAlive.ino
  char buf[32];
  int s;
  camera_fb_t * fb = NULL; // pointer
  WiFiClient client = server.client();

  client.write(HEADER, hdrLen);
  client.write(BOUNDARY, bdrLen);
  Serial.println("Starting stream...");
  while (true)
  {
    if (!client.connected()) break;
    fb = esp_camera_fb_get();
    client.write(CTNTTYPE, cntLen);
    sprintf( buf, "%d\r\n\r\n", s );
    client.write(buf, strlen(buf));
    client.write((char *)fb->buf, fb->len);
    client.write(BOUNDARY, bdrLen);
  }
  esp_camera_fb_return(fb);
  Serial.println("Ending stream...");
}


void serveJpg(void)
{
  camera_fb_t * fb = NULL; // pointer
  // Take a photo with the camera
  Serial.println("Taking a photo...");
  fb = esp_camera_fb_get();
  
  WiFiClient client = server.client();

  if (!client.connected()) return;

  client.write(JHEADER, jhdLen);
  client.write((char *)fb->buf, fb->len);
}

void handleJpgLo()
{
 // if (esp_camera_init(&config) == ESP_OK)
    serveJpg();
}

void handleJpgHi()
{
  //config.frame_size = FRAMESIZE_SVGA;
  //if (esp_camera_init(&config) == ESP_OK)
  serveJpg();
}

void handleJpgRaw()
{
  config.frame_size = FRAMESIZE_UXGA;
 // if (esp_camera_init(&config) == ESP_OK)
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
  Serial.println(led_value);
  digitalWrite(LED_PIN, led_value);   // turn the LED on (HIGH is the voltage level)

  // Respond to the client
  server.send(200, "application/json", "{}");
}


void set_flash() {
  String body = server.arg("plain");
  deserializeJson(jsonDocument, body);

  // Get RGB components
  int flash_value = jsonDocument["value"];
  Serial.print("Flash: ");
  Serial.println(flash_value );
  pinMode(FLASH_PIN, OUTPUT);
  digitalWrite(FLASH_PIN, flash_value );   // turn the LED on (HIGH is the voltage level)

  if(flash_value==false) {
    pinMode(FLASH_PIN, INPUT_PULLUP);
  }
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
  // Turn-off the 'brownout detector'
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  // OV2640 camera module
  camera_config_t config;
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
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }
  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    ESP.restart();
  }

  Serial.printf("Camera initialized");
    
}


void serve_triggered(){
  Serial.println("Serve triggered image");
  handleFileRead(TRIGGER_PHOTO_NAME); 
}

String getContentType(String filename){
  if(server.hasArg("download")) return "application/octet-stream";
  else if(filename.endsWith(".htm")) return "text/html";
  else if(filename.endsWith(".html")) return "text/html";
  else if(filename.endsWith(".css")) return "text/css";
  else if(filename.endsWith(".js")) return "application/javascript";
  else if(filename.endsWith(".png")) return "image/png";
  else if(filename.endsWith(".gif")) return "image/gif";
  else if(filename.endsWith(".jpg")) return "image/jpeg";
  else if(filename.endsWith(".ico")) return "image/x-icon";
  else if(filename.endsWith(".xml")) return "text/xml";
  else if(filename.endsWith(".pdf")) return "application/x-pdf";
  else if(filename.endsWith(".zip")) return "application/x-zip";
  else if(filename.endsWith(".gz")) return "application/x-gzip";
  return "text/plain";
}

bool handleFileRead(String path){
  String contentType = getContentType(path);
  if(SPIFFS.exists(path)){
    File file = SPIFFS.open(path, "r");
    size_t sent = server.streamFile(file, contentType);
    file.close();
    return true;
  }
  return false;
}

boolean handleSoftTrigger() {
  server.send(200, "application/json", "{}");
  capturePhotoSaveSpiffs(); 
}
