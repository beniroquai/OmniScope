//https://stackoverflow.com/questions/60029614/esp32-cam-stream-in-opencv-python
#include <esp32cam.h>
#include <WebServer.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <EEPROM.h>

// DEFINE WIFI
const char *SSID = "Blynk"; // "BenMur";
const char *PWD =  "12345678"; //"MurBen3128";
String hostname = "ESPLENS0";

#define LED_PIN 4 // 18

WebServer server(80);

char buffer[2500];
DynamicJsonDocument jsonDocument(2048);

static auto loRes = esp32cam::Resolution::find(320, 240);
static auto hiRes = esp32cam::Resolution::find(800, 600);
static auto rawRes = esp32cam::Resolution::find(1632, 1232);

// EEPROM
int addr_id = 0;
int setup_id = 0;

String identifier = "OMNISCOPE_1";

void setup()
{
  Serial.begin(115200);
  Serial.println("Spinning Up Microscope");

  // EEPROM
  EEPROM.begin(512);
  EEPROM.get(addr_id,setup_id);
  Serial.println("SETUP ID is: "+String(setup_id));

  // visualize Power available
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);
  digitalWrite(LED_PIN, LOW);   // turn the LED on (HIGH is the voltage level)

  
  // Initiliaze Camera
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
    cfg.setBufferCount(2);
    cfg.setJpeg(100);

    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }

  connectToWiFi(); 


  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam.bmp");
  Serial.println("  /cam-lo.jpg");
  Serial.println("  /cam-hi.jpg");
  Serial.println("  /cam.mjpeg");

  server.on("/cam.bmp", handleBmp);
  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/cam-raw.jpg", handleJpgRaw);
  server.on("/cam.jpg", handleJpg);
  server.on("/cam.mjpeg", handleMjpeg);
  server.on("/restart", handleRestart);
  server.on("/led", HTTP_POST, set_led);
  server.on("/getID", HTTP_GET, get_ID);
  server.on("/setID", HTTP_POST, set_ID);
  server.on("/omniscope", HTTP_GET, handleIdentification);

  server.begin();
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

  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.println("Wifi connecting...");
    notConnectedCounter++;
    if (notConnectedCounter > 50) { // Reset board if not connected after 5s
      Serial.println("Resetting due to Wifi not connecting...");
      ESP.restart();
    }
  }

  Serial.print("Connected. IP: ");
  Serial.println(WiFi.localIP());
}


void handleBmp()
{
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("SET-LO-RES FAIL");
  }

  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  if (!frame->toBmp()) {
    Serial.println("CONVERT FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CONVERT OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/bmp");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

void handleJpgLo()
{
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("SET-LO-RES FAIL");
  }
  serveJpg();
}

void handleJpgHi()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

void handleJpgRaw()
{
  if (!esp32cam::Camera.changeResolution(rawRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}


void handleJpg()
{
  server.sendHeader("Location", "/cam-hi.jpg");
  server.send(302, "", "");
}

void handleMjpeg()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }

  Serial.println("STREAM BEGIN");
  WiFiClient client = server.client();
  auto startTime = millis();
  int res = esp32cam::Camera.streamMjpeg(client);
  if (res <= 0) {
    Serial.printf("STREAM ERROR %d\n", res);
    return;
  }
  auto duration = millis() - startTime;
  Serial.printf("STREAM END %dfrm %0.2ffps\n", res, 1000.0 * res / duration);
}

void handleRestart(){
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
  EEPROM.get(addr_id,setup_id);
  Serial.println("Old EEPROM value is: "+String(setup_id));
  

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
  EEPROM.put(addr_id,setup_id);
  EEPROM.commit();  
  
  Serial.print("setup_id: ");
  Serial.print(setup_id);

  // Respond to the client
  server.send(200, "application/json", "{}");
}

void handleIdentification(){
  server.send(200, "application/json", identifier);
}
