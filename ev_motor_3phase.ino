/*
UNPHAYZED ELECTRIC CHAMPION KIT 2025-2026
3-PHASE MOTOR CONTROL
Phase 1: Ramp 0→40% over ~2s
Phase 2: Target 1m left with 4s remaining (adjust power in loop)
Phase 3: Creep slowly until 2cm from target, stop
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <RobojaxBTS7960.h>
#include <math.h>

//LCD SETUP------------------------------------
LiquidCrystal_I2C lcd(0x27, 16, 2);

//MOTOR DRIVER PINS+SETUP------------------------------------
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

//ENCODER PINS------------------------------------
#define ENCA 2
#define ENCB 3
#define DialCLK 5
#define DialDT 4

//PUSH BUTTON PINS------------------------------------
#define StartButtonPin 6
#define SetButtonPin 7
#define DialButtonPin A0

//ENCODER VARIABLES------------------------------------
volatile unsigned long counter = 0;

//LCD VARIABLES------------------------------------
int pos = 2;
float inc = 1;
int set = -1;

//MOVEMENT VARIABLES------------------------------------
double TargetDistance = 10.000;
double TargetDistanceCM = TargetDistance * 100;
double ArcLength;
double TargetTime = 20.00;
double wheelDiameter = 7.3025;
double wheelCircumfrence = wheelDiameter * 3.14159;

// 3-PHASE CONSTANTS
const double RAMP_DURATION_SEC = 2.0;       // Phase 1: ramp over 2 seconds
const double RAMP_END_POWER = 40.0;          // End Phase 1 at 40% power
const double TARGET_POINT_CM = 100.0;        // Phase 2 goal: 1m (100cm) left
const double ARRIVE_WITH_TIME_REMAINING = 4.0;  // 4 seconds remaining when hitting 1m
const double FINAL_STOP_CM = 2.0;           // Phase 3: stop 2cm before target
const int CREEP_POWER = 8;                  // Phase 3 creep power (%)

double pulsesPerRev = 1200;

bool straightMode = true;

// Phase states: 0=idle, 1=ramp, 2=targeting, 3=creep, 4=done
int phase = 0;

double targetEncoderValue;
double targetPointEncoder;   // Encoder when 100cm left
double finalStopEncoder;     // Encoder when 2cm before target
double maxEncoderValue;

unsigned long startTime = 0;
unsigned long rampStartTime = 0;
unsigned long lastSpeedTime = 0;
unsigned long lastCounter = 0;
double currentMotorPower = 0;
double currentSpeed = 0;     // cm/s
bool reachedTargetDistance = false;
double finalDist;

void setup() {
  Serial.begin(9600);
  motor.begin();
  set = -1; pos = 2; inc = 1;

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("Select Mode:    ");
  lcd.setCursor(0,1);
  lcd.print("Mode: STRAIGHT  ");

  pinMode(SetButtonPin, INPUT);
  digitalWrite(SetButtonPin, HIGH);
  pinMode(StartButtonPin, INPUT);
  digitalWrite(StartButtonPin, HIGH);
  pinMode(DialCLK, INPUT);
  pinMode(DialDT, INPUT);
  digitalWrite(DialCLK, HIGH);
  digitalWrite(DialDT, HIGH);
  pinMode(ENCA, INPUT);
  pinMode(ENCB, INPUT);
  digitalWrite(ENCA, HIGH);
  digitalWrite(ENCB, HIGH);

  attachInterrupt(0, ai0, RISING);
  attachInterrupt(1, ai1, RISING);

  Serial.println("Setup Complete");
}

void loop() {
  // MODE SELECTION (set == -1)
  if (set == -1) {
    if (digitalRead(DialCLK) == LOW || digitalRead(DialDT) == LOW) {
      straightMode = !straightMode;
      lcd.setCursor(0,1);
      lcd.print(straightMode ? "Mode: STRAIGHT  " : "Mode: ARC       ");
      delay(300);
    }
    if (digitalRead(SetButtonPin) == LOW) {
      lcd.setCursor(0,0);
      lcd.print("Tgt Dist:      m");
      lcd.setCursor(9, 0);
      lcd.print(TargetDistance);
      lcd.setCursor(0,1);
      lcd.print("Increment: ");
      lcd.print(inc);
      set = 0;
      delay(300);
    }
  }

  // DISTANCE ENTRY (set == 0)
  if (set == 0) {
    if (digitalRead(SetButtonPin) == LOW) {
      TargetDistanceCM = TargetDistance * 100;
      ArcLength = straightMode ? TargetDistanceCM : getArcLength(TargetDistanceCM);

      targetEncoderValue = getEncoderValue(ArcLength, wheelDiameter);
      targetPointEncoder = getEncoderValue(ArcLength - TARGET_POINT_CM, wheelDiameter);
      finalStopEncoder = getEncoderValue(ArcLength - FINAL_STOP_CM, wheelDiameter);
      maxEncoderValue = getEncoderValue(ArcLength * 2, wheelDiameter);

      Serial.print("ArcLength: "); Serial.println(ArcLength);
      Serial.print("Target point (1m left) encoder: "); Serial.println(targetPointEncoder);
      Serial.print("Final stop (2cm before) encoder: "); Serial.println(finalStopEncoder);

      lcd.setCursor(0,0);
      lcd.print("Tgt Time:      s");
      lcd.setCursor(9, 0);
      lcd.print(TargetTime, 3);
      inc = 5; pos = 2;
      lcd.setCursor(11, 1);
      lcd.print("     ");
      lcd.setCursor(11, 1);
      lcd.print(inc);
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

  // TIME ENTRY (set == 1)
  if (set == 1) {
    if (digitalRead(SetButtonPin) == LOW) {
      lcd.setCursor(0,0);
      lcd.print("Tgt Dist:      m");
      lcd.setCursor(9, 0);
      lcd.print(TargetDistance, 3);
      lcd.setCursor(0,1);
      lcd.print("Tgt Time:      s");
      lcd.setCursor(9, 1);
      lcd.print(TargetTime, 3);
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

  // READY TO RUN (set == 2)
  if (set == 2) {
    if (digitalRead(SetButtonPin) == LOW) {
      inc = 1; pos = 2;
      lcd.setCursor(0,0);
      lcd.print("Select Mode:    ");
      lcd.setCursor(0,1);
      lcd.print(straightMode ? "Mode: STRAIGHT  " : "Mode: ARC       ");
      set = -1;
      delay(300);
    }

    // START button: begin 3-phase run
    if (digitalRead(StartButtonPin) == LOW && phase == 0) {
      startTime = millis();
      rampStartTime = millis();
      lastSpeedTime = millis();
      lastCounter = counter;
      phase = 1;
      currentMotorPower = 0;
      Serial.println("=== 3-PHASE RUN STARTED ===");
      motor.stop();
      delay(100);
    }

    // ----- PHASE 1: Ramp 0→40% over ~2s -----
    if (phase == 1) {
      double rampElapsed = (millis() - rampStartTime) / 1000.0;
      if (rampElapsed >= RAMP_DURATION_SEC) {
        currentMotorPower = RAMP_END_POWER;
        phase = 2;
        lastSpeedTime = millis();
        lastCounter = counter;
        Serial.println("Phase 2: Targeting loop");
      } else {
        currentMotorPower = RAMP_END_POWER * (rampElapsed / RAMP_DURATION_SEC);
      }
      motor.rotate((int)currentMotorPower, CW);
    }

    // ----- PHASE 2: Target 1m left with 4s remaining -----
    if (phase == 2) {
      double distanceTraveled = (counter / pulsesPerRev) * wheelCircumfrence;
      double distanceRemaining = ArcLength - distanceTraveled;
      double elapsed = (millis() - startTime) / 1000.0;
      double timeLeft = TargetTime - elapsed;

      if (distanceRemaining <= TARGET_POINT_CM) {
        phase = 3;
        currentMotorPower = CREEP_POWER;
        Serial.println("Phase 3: Creep to 2cm");
      } else {
        // Update speed estimate every 100ms
        unsigned long now = millis();
        if (now - lastSpeedTime >= 100) {
          double dt = (now - lastSpeedTime) / 1000.0;
          double dCount = counter - lastCounter;
          currentSpeed = (dCount / pulsesPerRev) * wheelCircumfrence / dt;
          lastCounter = counter;
          lastSpeedTime = now;
        }

        double neededSpeed = distanceRemaining / timeLeft;
        if (neededSpeed > 150) neededSpeed = 150;
        if (neededSpeed < 5) neededSpeed = 5;

        // Adjust power: too slow → increase, too fast → decrease
        double speedError = neededSpeed - currentSpeed;
        if (speedError > 5) currentMotorPower += 2;
        else if (speedError < -5) currentMotorPower -= 2;
        currentMotorPower = constrain(currentMotorPower, 25, 60);

        motor.rotate((int)currentMotorPower, CW);
      }
    }

    // ----- PHASE 3: Creep until 2cm from target -----
    if (phase == 3) {
      motor.rotate(CREEP_POWER, CW);
      if (counter >= finalStopEncoder) {
        motor.stop();
        phase = 4;
        reachedTargetDistance = true;
        Serial.println("Reached 2cm before target - STOP");
      }
    }

    // ----- Run complete -----
    if (reachedTargetDistance) {
      delay(1000);
      double runTime = (millis() - startTime) / 1000.0;
      finalDist = (ArcLength - FINAL_STOP_CM) / 100.0;

      lcd.setCursor(0,0);
      lcd.print("Fin Dist:      m");
      lcd.setCursor(9, 0);
      lcd.print(finalDist, 3);
      lcd.setCursor(0,1);
      lcd.print("Fin Time:      s");
      lcd.setCursor(9, 1);
      lcd.print(runTime, 3);

      Serial.println("=== RUN COMPLETE ===");
      Serial.print("Final counter: "); Serial.println(counter);
      Serial.print("Target encoder: "); Serial.println(finalStopEncoder);

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
