#include <QTRSensors.h>
#include <Encoder.h>
#include <SoftwareSerial.h>
#include <EEPROMex.h>

SoftwareSerial bluetooth(10, 11); // RX, TX

QTRSensors qtr;

const uint8_t SensorCount = 8;
uint16_t sensorValues[SensorCount];

#define Kp                  0.5//0.18
#define Ki               0.0001//0.00005
#define Kd                  2.3//2.4     // experiment to determine this, slowly increase the speeds and adjust this value. ( Note: Kp < Kd) 


#define rightMaxSpeed         90
#define leftMaxSpeed          100
#define rightMinSpeed         50
#define leftMinSpeed          60

bool dval[SensorCount];

int left1       = 4;
int left2       = 5;
int leftEnable  = 8;
int right1      = 6;
int right2      = 7;
int rightEnable = 9;

int LEFT_enc_A = 3;
int LEFT_enc_B = 2;
int RIGHT_enc_A = 21;
int RIGHT_enc_B = 20;

Encoder LEFT_ENC(LEFT_enc_A, LEFT_enc_B);
Encoder RIGHT_ENC(RIGHT_enc_A, RIGHT_enc_B);

#define blackTH 800
#define whiteTH 230

#define BLACK 0
#define WHITE 1
#define LINE  2
uint8_t mode = 0;

int lastError, errorSum;
int B_lastError, B_errorSum;

//EEPROM Addressing for calibration storage
#define addrCalibratedMinimumOn 0
#define addrCalibratedMaximumOn 100


long oldPosition_L  = -999;
long oldPosition_R  = -999;
long newPosition_L = 0;
long newPosition_R = 0;

int error = 0;
boolean received_msg = false;


const byte numChars = 32;
char receivedChars[numChars];   // an array to store the received data
boolean newData = false;


const int counts_per_rev = 1770;   // (4 pairs N-S) * (48:1 gearbox) * (2 falling/rising edges) = 384
const int wheel_d = 70;           // Wheel diameter (mm)
const float wheel_c = PI * wheel_d; // Wheel circumference (mm)
boolean b = 0;

void setup() {
  qtr.setTypeRC();
  qtr.setSensorPins((const uint8_t[]) {
    22, 24, 26, 28, 30, 32, 34, 36
  }, SensorCount);
  qtr.setEmitterPin(38);

  pinMode(left1, OUTPUT);
  pinMode(left2, OUTPUT);
  pinMode(leftEnable, OUTPUT);
  pinMode(right1, OUTPUT);
  pinMode(right2, OUTPUT);
  pinMode(rightEnable, OUTPUT);

  pinMode(13, OUTPUT);

  pinMode(40, OUTPUT);
  digitalWrite(40, HIGH);
  pinMode(12, OUTPUT);
  digitalWrite(12, LOW);

  Serial.begin(9600);
  bluetooth.begin(9600);
  //bluetooth.println("Hello, world?");

  digitalWrite(13, HIGH);
  delay(1000);

  for (uint16_t i = 0; i < 400; i++)
  {
    qtr.calibrate();
  }
  storeQTR();
  digitalWrite(13, LOW);
  recallQTR();
  delay(5000);
  
  while(mode != LINE){
    qtrRead();
    forward(75, 1); 
  }
  brake();
}

void loop() {
  recvWithEndMarker();
  if (newData == true && strcmp(receivedChars, "BOX") == 0) {
    Serial.println(receivedChars);
    
    digitalWrite(13, HIGH);
    newData = false;

    bluetooth.write("ACK\n");
    delay(100);
    
    if(b == 0){
      brake();
      b = 1;
    }
    stop();
    Serial.println("Stopped the robot");
    send_encoder_val();
    Serial.println("Finished");

    delay(500);
  } else {
    digitalWrite(13, LOW);
    line_follow();
    //Serial.println("line following");
    b = 0;

  }
}

void line_follow(){
  uint16_t u = qtrRead();
  //Serial.println(mode);
  
  if(mode == BLACK){
    driveStraight_cm(17, 30);
    stop();
    bluetooth.println("STOP");
    delay(100);
    while(1);  // stop forever.
    
  }else if(mode == WHITE){
    driveStraight_cm(5, 30);
    turn_back();
  }else{
    PID_line_follow(10, u);
  }
}


void send_encoder_val() {
  newPosition_L = LEFT_ENC.read();
  newPosition_R = RIGHT_ENC.read();
  if (newPosition_L != oldPosition_L) {
    oldPosition_L = newPosition_L;
    //Serial.println(newPosition_L);
  }

  if (newPosition_R != oldPosition_R) {
    oldPosition_R = newPosition_R;
    //Serial.println(newPosition_R);
  }

  long pos = (newPosition_L + newPosition_R) / 2;
  pos = (pos / counts_per_rev) * wheel_c;
  pos = pos / 10; // to convert to cm

  bluetooth.println(pos);
  delay(100);
  Serial.print("send enc : ");
  Serial.println(pos);
}


void recvWithEndMarker() {
  static byte ndx = 0;
  char endMarker = '\n';
  char rc;

  while (bluetooth.available() > 0 && newData == false) {
    rc = bluetooth.read();

    if (rc != endMarker) {
      receivedChars[ndx] = rc;
      ndx++;
      if (ndx >= numChars) {
        ndx = numChars - 1;
      }
    }
    else {
      receivedChars[ndx] = '\0'; // terminate the string
      ndx = 0;
      newData = true;
    }
  }
}


void showNewData() {
  if (newData == true) {
    Serial.println(receivedChars);
    newData = false;
  }
}


uint16_t qtrRead() {
  uint16_t position = qtr.readLineBlack(sensorValues);
  for (uint8_t i = 0; i < SensorCount ; i++ )
  {
    if (sensorValues[i] > blackTH) dval[i] = 0;
    else if (sensorValues[i] < whiteTH) dval[i] = 1;
    //      dval == 1 >>>> WHITE
    //      dval == 0 >>>> BLACK
  }

  if (dval[0] == 0 && dval[1] == 0 && dval[2] == 0 &&
      dval[3] == 0 && dval[4] == 0 && dval[5] == 0 &&
      dval[6] == 0 && dval[7] == 0 ) {
    mode = BLACK;

  } else if (dval[0] == 1 && dval[1] == 1 && dval[2] == 1 &&
             dval[3] == 1 && dval[4] == 1 && dval[5] == 1 &&
             dval[6] == 1 && dval[7] == 1  ) {
    mode = WHITE;

  } else {
    mode = LINE;
  }
  return position;
}


void PID_line_follow(int base_speed, uint16_t position) {
  //int position = qtr.readLineBlack(sensorValues); // get calibrated readings along with the line position, refer to the QTR Sensors Arduino Library for more details on line position.
  int error = position - 3500;

  errorSum += error * Ki;

  int motorSpeed = Kp * error + Kd * (error - lastError) + errorSum;
  lastError = error;

  int rightMotorSpeed = base_speed + motorSpeed;
  int leftMotorSpeed = base_speed - motorSpeed;

  if (rightMotorSpeed > rightMaxSpeed ) rightMotorSpeed = rightMaxSpeed; // prevent the motor from going beyond max speed
  if (leftMotorSpeed > leftMaxSpeed ) leftMotorSpeed = leftMaxSpeed; // prevent the motor from going beyond max speed
  if (rightMotorSpeed < 0) rightMotorSpeed = rightMinSpeed; // keep the motor speed positive
  if (leftMotorSpeed < 0) leftMotorSpeed = leftMinSpeed; // keep the motor speed positive
  {
    digitalWrite(right1, HIGH);
    digitalWrite(right2, LOW);
    analogWrite(rightEnable, rightMotorSpeed);
    digitalWrite(left1, HIGH);
    digitalWrite(left2, LOW);
    analogWrite(leftEnable, leftMotorSpeed);
  }
}

void forward(int speed, int delay_time) {
  digitalWrite(right1, HIGH);
  digitalWrite(right2, LOW);
  analogWrite(rightEnable, speed);
  digitalWrite(left1, HIGH);
  digitalWrite(left2, LOW);
  analogWrite(leftEnable, speed+10);
  delay(delay_time);
}

void backward(int speed, int delay_time) {
  digitalWrite(right1, LOW);
  digitalWrite(right2, HIGH);
  analogWrite(rightEnable, speed);
  digitalWrite(left1, LOW);
  digitalWrite(left2, HIGH);
  analogWrite(leftEnable, speed+10);
  delay(delay_time);
}

void stop() {
  digitalWrite(right1, LOW);
  digitalWrite(right2, LOW);
  analogWrite(rightEnable, 0);
  digitalWrite(left1, LOW);
  digitalWrite(left2, LOW);
  analogWrite(leftEnable, 0);
}

void brake() {
  digitalWrite(right1, LOW);
  digitalWrite(right2, HIGH);
  analogWrite(rightEnable, 200);
  digitalWrite(left1, LOW);
  digitalWrite(left2, HIGH);
  analogWrite(leftEnable, 210);
  delay(30);

  stop();
}




void driveStraight_cm(float dist, int power) {

  unsigned long num_ticks_l;
  unsigned long num_ticks_r;

  // Set initial motor power
  int power_l = 110;
  int power_r = 80;

  // Used to determine which way to turn to adjust
  unsigned long diff_l;
  unsigned long diff_r;

  // Reset encoder counts
  newPosition_L = LEFT_ENC.read();
  newPosition_R = RIGHT_ENC.read();

  // Remember previous encoder counts
  unsigned long enc_l_prev = newPosition_L;
  unsigned long enc_r_prev = newPosition_R;

  unsigned long enc_l = 0;
  unsigned long enc_r = 0;

  const unsigned long enc_l_init = newPosition_L;
  const unsigned long enc_r_init = newPosition_R;
  
  // Calculate target number of ticks
  float num_rev = (dist * 10) / wheel_c;  // Convert to mm
  unsigned long target_count = num_rev * counts_per_rev;
  
  // Debug
//  Serial.print("Driving for ");
//  Serial.print(dist);
//  Serial.print(" cm (");
//  Serial.print(target_count);
//  Serial.print(" ticks) at ");
//  Serial.print(power);
//  Serial.println(" motor power");

  // Drive until one of the encoders reaches desired count
  while ( (enc_l < target_count) && (enc_r < target_count) ) {
    enc_l = LEFT_ENC.read() - enc_l_init;
    enc_r = RIGHT_ENC.read() - enc_r_init;
  
    if (newPosition_L != oldPosition_L) {
      oldPosition_L = newPosition_L;
      num_ticks_l = newPosition_L;
      //Serial.println(newPosition_L);
    }
  
    if (newPosition_R != oldPosition_R) {
      oldPosition_R = newPosition_R;
      num_ticks_r = newPosition_R;
      //Serial.println(newPosition_R);
    }    
   
    // Print out current number of ticks
//    Serial.print(num_ticks_l);
//    Serial.print("\t");
//    Serial.println(num_ticks_r);

    // Drive
    drive(power_l, power_r);

    // Number of ticks counted since last time
    diff_l = num_ticks_l - enc_l_prev;
    diff_r = num_ticks_r - enc_r_prev;

    // Store current tick counter for next time
    enc_l_prev = num_ticks_l;
    enc_r_prev = num_ticks_r;

    // If left is faster, slow it down and speed up right
    if ( diff_l > diff_r ) {
      power_l -= 10;
      power_r += 10;
    }

    // If right is faster, slow it down and speed up left
    if ( diff_l < diff_r ) {
      power_l += 10;
      power_r -= 10;
    }

    // Brief pause to let motors respond
    delay(10);
  }

  // Brake
  brake();

  if(enc_l > enc_r){
    while (enc_r < enc_l) {
      enc_r = RIGHT_ENC.read() - enc_r_init;
   
      if (newPosition_R != oldPosition_R) {
        oldPosition_R = newPosition_R;
        num_ticks_r = newPosition_R;
      }    
     
      drive(0, power_r);
      delay(10);
    }
    brake();
  }else if(enc_r > enc_l){
    while (enc_l < enc_r) {
      enc_l = LEFT_ENC.read() - enc_l_init;
   
      if (newPosition_L != oldPosition_L) {
        oldPosition_L = newPosition_L;
        num_ticks_l = newPosition_L;
      }    
     
      drive(power_l, 0);
      delay(10);
    }
    brake();
  }else{
    brake();
  }
}

void drive(int power_a, int power_b) {
  // Constrain power to between -255 and 255
  power_a = constrain(power_a, -(rightMaxSpeed-20), rightMaxSpeed-20);
  power_b = constrain(power_b, -(leftMaxSpeed-20), leftMaxSpeed-20);

  // Left motor direction
  if ( power_a < 0 ) {
    digitalWrite(right1, LOW);
    digitalWrite(right2, HIGH);
  } else {
    digitalWrite(right1, HIGH);
    digitalWrite(right2, LOW);
  }

  // Right motor direction
  if ( power_b < 0 ) {
    digitalWrite(left1, LOW);
    digitalWrite(left2, HIGH);
  } else {
    digitalWrite(left1, HIGH);
    digitalWrite(left2, LOW);
  }

  // Set speed
  analogWrite(rightEnable, abs(power_a));
  analogWrite(leftEnable, abs(power_b));
}


void turn_back() {
  
  while(sensorValues[3] < 900 && 
        sensorValues[4] < 900){
    qtr.readLineBlack(sensorValues);
    digitalWrite(right1, HIGH);
    digitalWrite(right2, LOW);
    analogWrite(rightEnable, 60);
    digitalWrite(left1, LOW);
    digitalWrite(left2, HIGH);
    analogWrite(leftEnable, 70);
    delay(20);
  }
  
  digitalWrite(right1, LOW);
  digitalWrite(right2, HIGH);
  analogWrite(rightEnable, 200);
  digitalWrite(left1, HIGH);
  digitalWrite(left2, LOW);
  analogWrite(leftEnable, 210);
  delay(30);

  stop();
}

void storeQTR()
{
  Serial.println();
  Serial.println("Storing Calibration Data into EEPROM...");

  EEPROM.writeBlock<unsigned int>(addrCalibratedMinimumOn, qtr.calibrationOn.minimum, 8);
  EEPROM.writeBlock<unsigned int>(addrCalibratedMaximumOn, qtr.calibrationOn.maximum, 8);

  Serial.println("EEPROM Storage Complete");
}

void recallQTR()
{
  Serial.println();
  Serial.println("Recalling Calibration Data from EEPROM...");

  qtr.calibrate();
  EEPROM.readBlock<unsigned int>(addrCalibratedMinimumOn, qtr.calibrationOn.minimum, 8);
  EEPROM.readBlock<unsigned int>(addrCalibratedMaximumOn, qtr.calibrationOn.maximum, 8);

  Serial.println("EEPROM Recall Complete");
}