/*
      Author: Robert Brenner Marthins

      Version: 0.1.00
      Notes:

*/

#include <AccelStepper.h>

const int vertikalDirPin = 8;
const int vertikalStepPin = 9;
String vIn = "0";
String OvIn = "0";
int vSpeed = 0;
#define motorInterfaceType 1
AccelStepper vertikal(motorInterfaceType, vertikalStepPin, vertikalDirPin);

const int horisontalDirPin = 10;
const int horisontalStepPin = 11;
String hIn = "0";
String OhIn = "0";
int hSpeed = 0;
#define motorInterfaceType 1
AccelStepper horisontal(motorInterfaceType, horisontalStepPin, horisontalDirPin);

const int maxUp = 1000;
const int maxDown = 1000;       //hvor lang motoren kan gå før det er fare for at den treffer rammen
String innkommende;


void setup() {
  vertikal.setMaxSpeed(1000);
  vertikal.setCurrentPosition(0);
  vertikal.setAcceleration(3000);
  horisontal.setMaxSpeed(1000);
  horisontal.setAcceleration(300); 
  horisontal.setCurrentPosition(0);
  Serial.begin(115200);
  Serial.setTimeout(15);

  digitalWrite(2, HIGH);
  digitalWrite(3, HIGH);
  digitalWrite(4, HIGH);
  digitalWrite(5, HIGH);
  digitalWrite(6, HIGH);
  digitalWrite(7, HIGH);

}

void loop() {
  if (Serial.available()) {
    innkommende = Serial.readStringUntil('\n');
    Serial.println(innkommende);
    if (innkommende != "h" || innkommende != "n") {
      int komma = innkommende.indexOf(',');
      String vIn = innkommende.substring(0, komma);
      String hIn = innkommende.substring(komma + 1);
      if (vIn != OvIn) {
        vSpeed = vIn.toInt();
      }

      if (hIn != OhIn) {
        hSpeed = hIn.toInt();
      }
      OhIn = hIn;
      OvIn = vIn;
    }
  }


  if (innkommende == "h") {
    vertikal.setSpeed(100);
    vertikal.moveTo(0);
    vertikal.runToPosition();
    innkommende = "0,0";
  }

  else if (innkommende == "n") {
    vertikal.setCurrentPosition(0);
  }

  else {
    vertikal.setSpeed(vSpeed);
    vertikal.run();
    horisontal.setSpeed(hSpeed);
    horisontal.run();
  }
}
