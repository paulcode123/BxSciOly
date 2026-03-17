/*
UNPHAYZED ELECTRIC CHAMPION KIT 2025-2026
CONSTANT-SPEED MOTOR CONTROL
Single phase: Targeting loop — measure speed, adjust power to reach
40cm before end with 1.5s remaining. No ramp up/down.
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <RobojaxBTS7960.h>
#include <math.h>

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
#define ENCA 2
#define ENCB 3
#define DialCLK 5
#define DialDT 4
#define StartButtonPin 6
#define SetButtonPin 7
#define DialButtonPin A0

volatile unsigned long counter = 0;
int pos = 2;
float inc = 1;
int set = -1;
double TargetDistance = 10.000;
double TargetDistanceCM = TargetDistance * 100;
double ArcLength;
double TargetTime = 20.00;
double wheelDiameter = 7.3025;
double wheelCircumfrence = wheelDiameter * 3.14159;

// CONSTANT-SPEED CONSTANTS
const double STOP_CM_BEFORE = 6.0;       // Stop when 6cm remaining
const double TIME_REMAINING_AT_STOP = 0.3;  // 0.3s left when we hit 6cm
const double KP_SPEED = 0.5;            // Power change per cm/s error (% per cm/s)
const double MAX_POWER_CHANGE = 6.0;    // Cap power change per 100ms cycle

double pulsesPerRev = 1200;
bool straightMode = true;
int phase = 0;  // 0=idle, 1=targeting loop, 2=done

double targetEncoderValue;
double arriveEncoder;
unsigned long startTime = 0;
unsigned long lastSpeedTime = 0;
unsigned long lastCounter = 0;
double currentMotorPower = 40;  // Start at 40%, loop will adjust
double currentSpeed = 0;
bool reachedTargetDistance = false;
double finalDist;

void setup() {
  Serial.begin(9600);
  motor.begin();
  set = -1; pos = 2; inc = 1;
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0); lcd.print("Select Mode:    ");
  lcd.setCursor(0,1); lcd.print("Mode: STRAIGHT  ");
  pinMode(SetButtonPin, INPUT); digitalWrite(SetButtonPin, HIGH);
  pinMode(StartButtonPin, INPUT); digitalWrite(StartButtonPin, HIGH);
  pinMode(DialCLK, INPUT); pinMode(DialDT, INPUT);
  digitalWrite(DialCLK, HIGH); digitalWrite(DialDT, HIGH);
  pinMode(ENCA, INPUT); pinMode(ENCB, INPUT);
  digitalWrite(ENCA, HIGH); digitalWrite(ENCB, HIGH);
  attachInterrupt(0, ai0, RISING);
  attachInterrupt(1, ai1, RISING);
}

void loop() {
  if (set == -1) {
    if (digitalRead(DialCLK) == LOW || digitalRead(DialDT) == LOW) {
      straightMode = !straightMode;
      lcd.setCursor(0,1);
      lcd.print(straightMode ? "Mode: STRAIGHT  " : "Mode: ARC       ");
      delay(300);
    }
    if (digitalRead(SetButtonPin) == LOW) {
      lcd.setCursor(0,0); lcd.print("Tgt Dist:      m");
      lcd.setCursor(9, 0); lcd.print(TargetDistance);
      lcd.setCursor(0,1); lcd.print("Increment: "); lcd.print(inc);
      set = 0;
      delay(300);
    }
  }

  if (set == 0) {
    if (digitalRead(SetButtonPin) == LOW) {
      TargetDistanceCM = TargetDistance * 100;
      ArcLength = straightMode ? TargetDistanceCM : getArcLength(TargetDistanceCM);
      targetEncoderValue = getEncoderValue(ArcLength, wheelDiameter);
      arriveEncoder = getEncoderValue(ArcLength - STOP_CM_BEFORE, wheelDiameter);
      lcd.setCursor(0,0); lcd.print("Tgt Time:      s");
      lcd.setCursor(9, 0); lcd.print(TargetTime, 3);
      inc = 5; pos = 2;
      lcd.setCursor(11, 1); lcd.print("     ");
      lcd.setCursor(11, 1); lcd.print(inc);
      set = 1;
      delay(300);
    }
    if (analogRead(DialButtonPin) == 0) {
      if (pos == 1) { inc = 1; pos++; } else if (pos == 2) { inc = 0.5; pos++; }
      else if (pos == 3) { inc = 0.1; pos++; } else if (pos == 4) { inc = 0.01; pos++; }
      else if (pos == 5) { inc = 0.001; pos = 1; }
      lcd.setCursor(11, 1); lcd.print("    "); lcd.setCursor(11, 1); lcd.print(inc, 3);
      delay(400);
    }
    if (digitalRead(DialDT) == LOW) {
      TargetDistance -= inc;
      lcd.setCursor(9, 0); lcd.print("      "); lcd.setCursor(9, 0); lcd.print(TargetDistance, 3);
      delay(250);
    }
    if (digitalRead(DialCLK) == LOW) {
      TargetDistance += inc;
      lcd.setCursor(9, 0); lcd.print("      "); lcd.setCursor(9, 0); lcd.print(TargetDistance, 3);
      delay(250);
    }
  }

  if (set == 1) {
    if (digitalRead(SetButtonPin) == LOW) {
      lcd.setCursor(0,0); lcd.print("Tgt Dist:      m");
      lcd.setCursor(9, 0); lcd.print(TargetDistance, 3);
      lcd.setCursor(0,1); lcd.print("Tgt Time:      s");
      lcd.setCursor(9, 1); lcd.print(TargetTime, 3);
      set = 2;
      delay(300);
    }
    if (analogRead(DialButtonPin) == 0) {
      if (pos == 1) { inc = 5; pos++; } else if (pos == 2) { inc = 1; pos++; }
      else if (pos == 3) { inc = 0.5; pos++; } else if (pos == 4) { inc = 0.1; pos++; }
      else if (pos == 5) { inc = 0.01; pos = 1; }
      lcd.setCursor(11, 1); lcd.print("    "); lcd.setCursor(11, 1); lcd.print(inc, 3);
      delay(400);
    }
    if (digitalRead(DialDT) == LOW) {
      TargetTime -= inc;
      lcd.setCursor(9, 1); lcd.print("      "); lcd.setCursor(9, 1); lcd.print(TargetTime, 3);
      delay(250);
    }
    if (digitalRead(DialCLK) == LOW) {
      TargetTime += inc;
      lcd.setCursor(9, 1); lcd.print("      "); lcd.setCursor(9, 1); lcd.print(TargetTime, 3);
      delay(250);
    }
  }

  if (set == 2) {
    if (digitalRead(SetButtonPin) == LOW) {
      inc = 1; pos = 2;
      lcd.setCursor(0,0); lcd.print("Select Mode:    ");
      lcd.setCursor(0,1); lcd.print(straightMode ? "Mode: STRAIGHT  " : "Mode: ARC       ");
      set = -1;
      delay(300);
    }

    if (digitalRead(StartButtonPin) == LOW && phase == 0) {
      startTime = millis();
      lastSpeedTime = millis();
      lastCounter = counter;
      currentMotorPower = 40;
      phase = 1;
      motor.stop();
      delay(100);
    }

    // ----- TARGETING LOOP: adjust power to reach 40cm-before with 1.5s remaining -----
    if (phase == 1) {
      double distanceTraveled = (counter / pulsesPerRev) * wheelCircumfrence;
      double distanceRemaining = ArcLength - distanceTraveled;
      double elapsed = (millis() - startTime) / 1000.0;
      double timeLeft = TargetTime - elapsed;

      if (distanceRemaining <= STOP_CM_BEFORE) {
        motor.stop();
        phase = 2;
        reachedTargetDistance = true;
        Serial.println("Reached 6cm before target - STOP");
      } else {
        // Update speed estimate every 100ms
        unsigned long now = millis();
        if (now - lastSpeedTime >= 100) {
          double dt = (now - lastSpeedTime) / 1000.0;
          double dCount = counter - lastCounter;
          currentSpeed = (dCount / pulsesPerRev) * wheelCircumfrence / dt;
          lastCounter = counter;
          lastSpeedTime = now;

          // Target: reach 6cm with 0.3s remaining
          double distToTarget = distanceRemaining - STOP_CM_BEFORE;
          double timeToTarget = timeLeft - TIME_REMAINING_AT_STOP;
          if (timeToTarget < 0.05) timeToTarget = 0.05;
          double neededSpeed = distToTarget / timeToTarget;
          if (neededSpeed > 150) neededSpeed = 150;
          if (neededSpeed < 5) neededSpeed = 5;
          double speedError = neededSpeed - currentSpeed;
          double powerChange = KP_SPEED * speedError;
          if (powerChange > MAX_POWER_CHANGE) powerChange = MAX_POWER_CHANGE;
          if (powerChange < -MAX_POWER_CHANGE) powerChange = -MAX_POWER_CHANGE;
          currentMotorPower += powerChange;
          currentMotorPower = constrain(currentMotorPower, 25, 75);
        }

        motor.rotate((int)currentMotorPower, CW);
      }
    }

    if (reachedTargetDistance) {
      delay(1000);
      double runTime = (millis() - startTime) / 1000.0;
      double distanceCm = (counter / pulsesPerRev) * wheelCircumfrence;
      finalDist = distanceCm / 100.0;

      lcd.setCursor(0,0); lcd.print("Fin Dist:      m");
      lcd.setCursor(9, 0); lcd.print(finalDist, 3);
      lcd.setCursor(0,1); lcd.print("Fin Time:      s");
      lcd.setCursor(9, 1); lcd.print(runTime, 3);

      phase = 0;
      reachedTargetDistance = false;
      counter = 0;
      startTime = 0;
    }
  }
}

void ai0() {
  if (digitalRead(3) == LOW) counter--;
  else counter++;
}
void ai1() {
  if (digitalRead(2) == LOW) counter++;
  else counter--;
}

double getEncoderValue(double TD, double WD) {
  double PPR = 1200;
  double WheelCircumfrence = 3.14159 * WD;
  return (TD / WheelCircumfrence) * PPR;
}

double getArcLength(double TargetDist) {
  double vehicleWidth = 13.00;
  double canBonusError = 2.00;
  double arcHeight = 100.00 - (vehicleWidth + canBonusError) / 2;
  double arcRadius = (arcHeight/2) + (TargetDist*TargetDist) / (8*arcHeight);
  double arcAngle = 2 * asin(TargetDist / (2*arcRadius));
  return arcRadius * arcAngle;
}
