// Arduino stepper motor control code
// Maximum speed 1000
#include <Stepper.h> // Include the header file
// change this to the number of steps on your motor
#define STEPS 32
// create an instance of the stepper class using the steps and pins
Stepper stepper(STEPS, 13,12,14,27);
int upKey = 7;
int downKey = 6;
int Step = 500;
int Speed = 500;
void setup()
{
  //Serial.begin(9600);
  //stepper.setMaxSpeed(Speed);
  //digitalWrite(upKey,LOW);
  stepper.setSpeed(Speed);
}
void loop()
{
  stepper.step(-Step);
  delay(10);
  stepper.step(Step);
  delay(10);
}
