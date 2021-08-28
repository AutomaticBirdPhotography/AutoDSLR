/*
      Author: Robert

      Version: 1.12.01
      Notes:
      Versjon 11 - Totalt endret hvordan stativet kjører; positiv y verdi kjører opp, positiv x verdi kjører høyre:
              0,10
               |
               |
      -10,0---0,0---10,0
               |
               |
              0,-10
      Data ved vanlig kjøring typ. joy: x, y, servo_x, servo_y
      Ved til point: p x_grader, y_grader

      Versjon 12 - Totalt endret hvordan servoen styrer etter data. Legger til grader hvert x millisekund, ettersom dette er det det ville blitt sendt på med python tidligere.
                .10 - satt tilbake hvordan servoen kan komme tilbake etter overstyring
                .13 - bevegelse i stativet etter "til klikk" løst ved å sette: innkommende = "0,0,0,0"
                .14 - endret hastigheten på servoen, sendes nå i verdier opp til 10
                .15 - lagt til pan og tilt offset for å kalibrere servokamera mot speilrefleks
                .17 - tune verdier ved align
      Versjon 1.xx - Med enablepins til motorene, potentiometer for initiell posisjon
                12
                  .01 - "b" skendes for å endre enable-pin, "f" for enable fokus
                  

      Python: pantilt.py -på stativet
*/
#include <Servo.h>
Servo panServo;
Servo tiltServo;
float posTilt = 0;
float posPan = 0;
float pan_offset = 13; //13
float tilt_offset = 0;  //-3
float OldPosTilt = 90 + tilt_offset;
float OldPosPan = 90 + pan_offset;
int i = 1;
int n = 1;
int gjenMove = 0;
unsigned long timeNow = 0;
int period = 100; //oppdateringsfrekvensen på servoen

#include <AccelStepper.h>

const int vertikalDirPin = 7;
const int vertikalStepPin = 6;
String vIn = "0";
String OvIn = "0";
int vSpeed = 0;
#define motorInterfaceType 1
AccelStepper vertikal(motorInterfaceType, vertikalStepPin, vertikalDirPin);

const int horisontalDirPin = 8;
const int horisontalStepPin = 9;
const int enablePin = 2;
String hIn = "0";
String OhIn = "0";
int hSpeed = 0;
#define motorInterfaceType 1
AccelStepper horisontal(motorInterfaceType, horisontalStepPin, horisontalDirPin);
/*
  const int fokusDirPin = 3;
  const int fokusStepPin = 4;
  const int fokusEnablePin = 12;
  String fIn = "0";
  String OfIn = "0";
  int fSpeed = 0;
  #define motorInterfaceType 1
  AccelStepper fokus(motorInterfaceType, fokusStepPin, fokusDirPin);
*/
const int maxUp = 650;
const int maxDown = -350;       //hvor langt motoren kan gå før det er fare for at kameraet treffer rammen
String innkommende;
bool enable = false;
bool fokusEnable = false;

#define pot A7
unsigned long potVerdi = 0;

void setup() {
  pinMode(pot, INPUT);
  pinMode(enablePin, OUTPUT);
  digitalWrite(enablePin, HIGH); // motorene skal ikke være på i starten
  digitalWrite(fokusEnablePin, HIGH);
  
  panServo.attach(9);
  tiltServo.attach(10);
  panServo.write(90 + pan_offset);
  tiltServo.write(90 + tilt_offset);

  vertikal.setMaxSpeed(300);
  vertikal.setCurrentPosition(0);
  vertikal.setAcceleration(5000);
  horisontal.setMaxSpeed(300);
  horisontal.setAcceleration(5000);
  horisontal.setCurrentPosition(0);
  //fokus.setMaxSpeed(100);
  //fokus.setAcceleration(300);
  //fokus.setCurrentPosition(0);
  Serial.begin(115200);
  Serial.setTimeout(15);

  for (int i = 0; i < 500; i++) {
    potVerdi += analogRead(pot);
  }
  int homing = map((potVerdi / 500), 838, 596, 500, -500); //verdier kalibrert tidligere
  potVerdi = 0;
  vertikal.move(homing);
  vertikal.setCurrentPosition(0);

}

void loop() {
  if (Serial.available() > 0) {
    innkommende = Serial.readStringUntil('\n');
  }
  if (innkommende[0] != 'h' && innkommende[0] != 'a' && innkommende[0] != 'p' && innkommende[0] != 'b' && innkommende[0] != 'f') {  //må ikke være noen av disse verdiene
    int komma = innkommende.indexOf(',');
    int andrekomma = innkommende.indexOf(',', komma + 1);
    int tredjekomma = innkommende.indexOf(',', andrekomma + 1);
    int fjerdekomma = innkommende.indexOf(',', tredjekomma + 1);
    String hIn = innkommende.substring(0, komma);
    String vIn = innkommende.substring(komma + 1, andrekomma);
    String AxisPan = innkommende.substring(andrekomma + 1, tredjekomma);
    String AxisTilt = innkommende.substring(tredjekomma + 1, fjerdekomma);
    float posTilt = AxisTilt.toFloat() / 10;
    float posPan = AxisPan.toFloat() / -10;

    if (millis() >= timeNow + period) {
      timeNow += period;
      tiltServo.write(OldPosTilt + posTilt);
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
    }
    //-----------------------------------
    if (vIn != OvIn) {
      vSpeed = vIn.toInt();
    }

    if (hIn != OhIn) {
      hSpeed = hIn.toInt() * -1;
    }


    OhIn = hIn;
    OvIn = vIn;
  }



  if (innkommende[0] == 'h') {
    timeNow = millis();
    if (i == 1) {
      OldPosTilt = 90 + tilt_offset;
      tiltServo.write(90 + tilt_offset);

      for (int i = 0; i < 500; i++) {
        potVerdi += analogRead(pot);
      }
      int homing = map((potVerdi / 500), 838, 596, 500, -500); //verdier kalibrert tidligere
      potVerdi = 0;
      vertikal.move(homing);
      vertikal.setSpeed(80);
      while (vertikal.distanceToGo() != 0) {
        vertikal.runSpeedToPosition();
      }
      vertikal.setCurrentPosition(0);
      i = 2;
    }
  }
  else if (innkommende[0] == 'a') {
    timeNow = millis();
    if (n == 1) {
      //nema 17 : 200 steps pr rev. *16(microstepping) *1,8(36/20(tannhjul))=5760 -> 1deg = 16steps (5760/360)
      float horisontalAlignPos = (OldPosPan - (90 + pan_offset)) * 15; //kjører litt for langt
      float vertikalAlignPos = (OldPosTilt - (90 + tilt_offset)) * 16;
      if (vertikalAlignPos > maxUp) {
        vertikalAlignPos = maxUp;
      }
      else if (vertikalAlignPos < maxDown) {
        vertikalAlignPos = maxDown;
      }

      horisontal.move(horisontalAlignPos);
      int totalMove = horisontal.distanceToGo();
      gjenMove = totalMove;

      vertikal.moveTo(vertikalAlignPos);

      while ((horisontal.distanceToGo() != 0 && vertikal.distanceToGo() != 0) || (horisontal.distanceToGo() != 0 || vertikal.distanceToGo() != 0)) {
        gjenMove = horisontal.distanceToGo();
        float alignPanServo = map(gjenMove, 0, totalMove, 90 + pan_offset, OldPosPan);
        panServo.write(alignPanServo);
        horisontal.setSpeed(80);
        horisontal.runSpeedToPosition();
        vertikal.setSpeed(80);
        vertikal.runSpeedToPosition();
      }
      n = 2;
      OldPosPan = 90 + pan_offset;
      innkommende = "0,0,0,0";
    }
  }
  else if (innkommende[0] == 'b'){
    enable != enable;
    if (enable){
      digitalWrite(enablePin, LOW);
    }
    if (enable = false){
      digitalWrite(enablePin, HIGH);
    }
    
  }
  else if (innkommende[0] == 'f'){
    fokusEnable != fokusEnable;
    if (enable){
      digitalWrite(fokusEnablePin, LOW);
    }
    if (enable = false){
      digitalWrite(fokusEnablePin, HIGH);
    }
    
  }
  else if (innkommende[0] == 'p') {
    timeNow = millis();
    innkommende.remove(0, 1); //fjerner første bokstav, som er p
    int komma = innkommende.indexOf(',');
    String hGrader = innkommende.substring(0, komma);
    //Serial.println(vGrader);
    String vGrader = innkommende.substring(komma + 1);
    float fvGrader = vGrader.toFloat();
    float fhGrader = hGrader.toFloat() * -1;
    float fvSteps = fvGrader * 16;
    float fhSteps = fhGrader * 16;
    int vSteps = round(fvSteps);
    if (vSteps + vertikal.currentPosition() > maxUp) {
      vSteps = maxUp - vertikal.currentPosition();    //hvis maxUp er 300 og currentPosition er 301 blir vSteps -1, slik at den kjører tilbake dit den skal :)
    }
    else if (vSteps + vertikal.currentPosition() < maxDown) {
      vSteps = maxDown - vertikal.currentPosition();
    }
    int hSteps = round(fhSteps);
    Serial.print(vSteps);
    Serial.print(", ");
    Serial.println(hSteps);
    vertikal.move(vSteps);
    horisontal.move(hSteps);
    while ((horisontal.distanceToGo() != 0 && vertikal.distanceToGo() != 0) || (horisontal.distanceToGo() != 0 || vertikal.distanceToGo() != 0)) {
      horisontal.setSpeed(100);
      horisontal.runSpeedToPosition();
      vertikal.setSpeed(100);
      vertikal.runSpeedToPosition();
    }
    hSpeed = 0;
    vSpeed = 0;
    innkommende = "0,0,0,0";
  }
  else {
    //Serial.println(vertikal.currentPosition());
    if (vertikal.currentPosition() > maxUp) {
      if (vSpeed < 0) {
        vertikal.setSpeed(vSpeed);
        vertikal.runSpeed();
      }
    }
    else if (vertikal.currentPosition() < maxDown) {
      if (vSpeed > 0) {
        vertikal.setSpeed(vSpeed);
        vertikal.runSpeed();
      }
    }
    else {
      vertikal.setSpeed(vSpeed);
      vertikal.runSpeed();
    }
    horisontal.setSpeed(hSpeed);
    horisontal.runSpeed();
    //fokus.setSpeed(fSpeed);
    //fokus.run();
    i = 1;
    n = 1;
  }
  //Serial.println(horisontal.currentPosition() + "," + vertikal.currentPosition());
}
