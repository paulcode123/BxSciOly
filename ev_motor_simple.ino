/*
UNPHAYZED ELECTRIC CHAMPION KIT 2025-2026
SIMPLE MOTOR CONTROL
Run at a given power for a given time. That's it.
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <RobojaxBTS7960.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);
#define RPWM 10
#define R_EN 11
#define R_IS 13
#define LPWM 9
#define L_EN 8
#define L_IS 12
#define CW 1
#define CCW 0
#define debug 1
RobojaxBTS7960 motor(R_EN,RPWM,R_IS, L_EN,LPWM,L_IS,debug);
#define StartButtonPin 6
#define SetButtonPin 7
#define DialCLK 5
#define DialDT 4
#define DialButtonPin A0

int pos = 1;
float inc = 1;
int set = -1;

int runPower = 50;        // Motor power 0-100%
float runTimeSec = 12.0;  // Run duration in seconds
bool running = false;
unsigned long runStartTime = 0;

void setup() {
  Serial.begin(9600);
  motor.begin();
  set = 0;
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0); lcd.print("Power:    %");
  lcd.setCursor(7, 0); lcd.print(runPower);
  lcd.setCursor(0,1); lcd.print("Time:     s");
  lcd.setCursor(7, 1); lcd.print(runTimeSec, 1);
  pinMode(SetButtonPin, INPUT);
  digitalWrite(SetButtonPin, HIGH);
  pinMode(StartButtonPin, INPUT);
  digitalWrite(StartButtonPin, HIGH);
  pinMode(DialCLK, INPUT);
  pinMode(DialDT, INPUT);
  digitalWrite(DialCLK, HIGH);
  digitalWrite(DialDT, HIGH);
}

void loop() {
  // Power entry (set == 0)
  if (set == 0) {
    if (digitalRead(SetButtonPin) == LOW) {
      lcd.setCursor(0,0); lcd.print("Power:    %");
      lcd.setCursor(7, 0); lcd.print(runPower);
      lcd.setCursor(0,1); lcd.print("Time:     s");
      lcd.setCursor(7, 1); lcd.print(runTimeSec, 1);
      set = 1;
      delay(300);
    }
    if (analogRead(DialButtonPin) == 0) {
      inc = (inc == 5) ? 1 : 5;
      delay(300);
    }
    if (digitalRead(DialDT) == LOW) {
      runPower -= inc;
      runPower = constrain(runPower, 0, 100);
      lcd.setCursor(7, 0); lcd.print("   ");
      lcd.setCursor(7, 0); lcd.print(runPower);
      delay(150);
    }
    if (digitalRead(DialCLK) == LOW) {
      runPower += inc;
      runPower = constrain(runPower, 0, 100);
      lcd.setCursor(7, 0); lcd.print("   ");
      lcd.setCursor(7, 0); lcd.print(runPower);
      delay(150);
    }
  }

  // Time entry (set == 1)
  if (set == 1) {
    if (digitalRead(SetButtonPin) == LOW) {
      lcd.setCursor(0,0); lcd.print("Ready. START!   ");
      lcd.setCursor(0,1); lcd.print("P:");
      lcd.print(runPower);
      lcd.print("% T:");
      lcd.print(runTimeSec, 1);
      lcd.print("s ");
      set = 2;
      delay(300);
    }
    if (analogRead(DialButtonPin) == 0) {
      inc = (inc == 1.0) ? 0.5 : (inc == 0.5) ? 0.1 : 1.0;
      delay(300);
    }
    if (digitalRead(DialDT) == LOW) {
      runTimeSec -= inc;
      runTimeSec = max(0.1f, runTimeSec);
      lcd.setCursor(7, 1); lcd.print("      ");
      lcd.setCursor(7, 1); lcd.print(runTimeSec, 1);
      delay(150);
    }
    if (digitalRead(DialCLK) == LOW) {
      runTimeSec += inc;
      lcd.setCursor(7, 1); lcd.print("      ");
      lcd.setCursor(7, 1); lcd.print(runTimeSec, 1);
      delay(150);
    }
  }

  // Ready to run (set == 2)
  if (set == 2) {
    if (digitalRead(SetButtonPin) == LOW) {
      lcd.setCursor(0,0); lcd.print("Power:    %");
      lcd.setCursor(0,1); lcd.print("Time:     s");
      set = 0;
      delay(300);
    }

    if (digitalRead(StartButtonPin) == LOW && !running) {
      running = true;
      runStartTime = millis();
      motor.rotate(runPower, CW);
    }

    if (running) {
      float elapsed = (millis() - runStartTime) / 1000.0;
      if (elapsed >= runTimeSec) {
        motor.stop();
        running = false;
        lcd.setCursor(0,0); lcd.print("Done!           ");
        lcd.setCursor(0,1); lcd.print("Ran ");
        lcd.print(elapsed, 1);
        lcd.print("s    ");
        delay(2000);
        lcd.setCursor(0,0); lcd.print("Ready. START!   ");
        lcd.setCursor(0,1); lcd.print("P:");
        lcd.print(runPower);
        lcd.print("% T:");
        lcd.print(runTimeSec, 1);
        lcd.print("s ");
      }
    }
  }
}
