/*
      Author: Robert

      Version: 0.1.00
      Notes:
      GROUND TIL ARDUINO MÅ BRUKES!!!
      løst med pulldown på STEP: Steppermotorer kjører vilkårlig i starten
      Python: objekt_tracker_multithreading.py -nja, ikke helt
*/
#include <Servo.h>
Servo panServo;
Servo tiltServo;
float OldPosTilt = 90;
float OldPosPan = 90;

#include <AccelStepper.h>

const int vertikalDirPin = 5;
const int vertikalStepPin = 6;
String vIn = "0";
String OvIn = "0";
int vSpeed = 0;
#define motorInterfaceType 1
AccelStepper vertikal(motorInterfaceType, vertikalStepPin, vertikalDirPin);

const int horisontalDirPin = 7;
const int horisontalStepPin = 8;
String hIn = "0";
String OhIn = "0";
int hSpeed = 0;
#define motorInterfaceType 1
AccelStepper horisontal(motorInterfaceType, horisontalStepPin, horisontalDirPin);
/*
  const int fokusDirPin = 3;
  const int fokusStepPin = 4;
  String fIn = "0";
  String OfIn = "0";
  int fSpeed = 0;
  #define motorInterfaceType 1
  AccelStepper fokus(motorInterfaceType, fokusStepPin, fokusDirPin);
*/
const int maxUp = 650;
const int maxDown = -350;       //hvor langt motoren kan gå før det er fare for at den treffer rammen
String innkommende;


void setup() {
  panServo.attach(9);
  tiltServo.attach(10);
  panServo.write(90);
  tiltServo.write(90);

  vertikal.setMaxSpeed(500);
  vertikal.setCurrentPosition(0);
  vertikal.setAcceleration(100);
  horisontal.setMaxSpeed(500);
  horisontal.setAcceleration(100);
  horisontal.setCurrentPosition(0);
  //fokus.setMaxSpeed(100);
  //fokus.setAcceleration(300);
  //fokus.setCurrentPosition(0);
  Serial.begin(115200);
  Serial.setTimeout(15);
}

void loop() {
  if (Serial.available() > 0) {
    innkommende = Serial.readStringUntil('\n');
    if (innkommende[0] != 'h' || innkommende[0] != 'a') {
      int komma = innkommende.indexOf(',');
      int andrekomma = innkommende.indexOf(',', komma + 1);
      int tredjekomma = innkommende.indexOf(',', andrekomma + 1);
      int fjerdekomma = innkommende.indexOf(',', tredjekomma + 1);
      String vIn = innkommende.substring(0, komma);
      String hIn = innkommende.substring(komma + 1, andrekomma);
      String AxisPan = innkommende.substring(andrekomma + 1, tredjekomma);
      String AxisTilt = innkommende.substring(tredjekomma + 1, fjerdekomma);
      float posTilt = AxisTilt.toFloat();
      tiltServo.write(OldPosTilt + posTilt);
      float posPan = AxisPan.toFloat();
      panServo.write(OldPosPan + posPan);

      if (OldPosTilt >= 120) {
        if (posTilt < 0) {
          OldPosTilt += posTilt;
        }
      }
      else if (OldPosTilt <= 60) {
        if (posTilt > 0) {
          OldPosTilt += posTilt;
        }
      }
      else {
        OldPosTilt += posTilt;
      }

      if (OldPosPan >= 180) {
        if (posPan < 0) {
          OldPosPan += posPan;
        }
      }
      else if (OldPosPan <= 0) {
        if (posPan > 0) {
          OldPosPan += posPan;
        }
      }
      else {
        OldPosPan += posPan;
      }
      //-----------------------------------
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


  if (innkommende[0] == 'h') {
    vertikal.setSpeed(100);
    vertikal.moveTo(0);
    vertikal.runToPosition();
    innkommende = "0,0,0,0";
  }
  else if (innkommende[0] == 'a') {
    //nema 17 - 200 steps pr rev. *16(microstepping) *1,8(36/20)=5760 -> 1deg = 16steps (5760/360)
    float alignPos = (OldPosPan - 90) * 16;
    vertikal.setSpeed(100);
    vertikal.moveTo(alignPos);
    vertikal.runToPosition();
    panServo.write(90);
  }

  else {
    //Serial.println(vertikal.currentPosition());
    if (vertikal.currentPosition() > maxUp) {
      if (vSpeed < 0) {
        vertikal.setSpeed(vSpeed);
        vertikal.run();
      }
    }
    else if (vertikal.currentPosition() < maxDown) {
      if (vSpeed > 0) {
        vertikal.setSpeed(vSpeed);
        vertikal.run();
      }
    }
    else {
      vertikal.setSpeed(vSpeed);
      vertikal.run();
    }
    horisontal.setSpeed(hSpeed);
    horisontal.run();
    //fokus.setSpeed(fSpeed);
    //fokus.run();
  }

}
