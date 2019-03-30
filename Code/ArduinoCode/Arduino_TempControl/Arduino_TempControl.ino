#include <Adafruit_MAX31856.h>
// Heating control relay locations
#define RELAY_ONE 2 // relay one is connected to digital pin 2
#define RELAY_TWO 3 // relay two is connected to digital pin 3
#define RELAY_THREE 4 // relay three is connected to digital pin 4
// Used to determine heating control
#define OFF_HEAT 0
#define LOW_HEAT 1
#define MEDIUM_HEAT 2
#define HIGH_HEAT 3

// Include heating function
void HeatControl(int ControlStatus);

// If you want to connect multiple MAX31856's to one microcontroller, have them share the SDI, SDO and SCK pins. Then assign each one a unique CS pin.
// To read a particular max 31856 you will need to make that chip select line low
int ThermoCLK = 13; 
int ThermoSDO = 12;
int ThermoSDI = 11;
int Thermo1CS = 10; // This is the upside down thermocouple amplifier
int Thermo2CS = 9; // This is the most recent thermocouple amplifier
char TempChar;
char STATE = 'S';

// Declare the MAX31856 chips
Adafruit_MAX31856 max1 = Adafruit_MAX31856(Thermo1CS, ThermoSDI, ThermoSDO, ThermoCLK);
Adafruit_MAX31856 max2 = Adafruit_MAX31856(Thermo2CS, ThermoSDI, ThermoSDO, ThermoCLK);

// Summary: Runs once on powerup
void setup() {
    pinMode(RELAY_ONE,OUTPUT); // ON or OFF
    pinMode(RELAY_TWO,OUTPUT); // 20 Ohm control
    pinMode(RELAY_THREE,OUTPUT); // 20=7 Ohm control
    HeatControl(OFF_HEAT);
    max1.begin();
    max1.setThermocoupleType(MAX31856_TCTYPE_K); // Ktype thermocouple
    max2.begin();
    max2.setThermocoupleType(MAX31856_TCTYPE_K); // Ktype thermocouple
    Serial.begin(9600);
    Serial.println("Starting");
    delay(500);
    //Serial.println("STATE,MAX 1 CJ,MAX 1 Thermo,MAX 2 CJ, MAX 2 Thermo");
} // End function

// Summary: The main loop
void loop() {
  if (Serial.available() > 0) {
    TempChar = Serial.read();
    if(TempChar == 'S') { // Stop heating
      HeatControl(OFF_HEAT);
      STATE = 'S';
    } else if (TempChar == 'L'){ // Start low heating
      HeatControl(LOW_HEAT);
      STATE = 'L';
    } else if (TempChar == 'M') { // Start medium heating
      HeatControl(MEDIUM_HEAT);
      STATE = 'M';
    } else if (TempChar == 'H') { // Start high heating
      HeatControl(HIGH_HEAT);
      STATE = 'H';
    }
  }
  Serial.print(STATE);
  Serial.print(",");
  Serial.print(max1.readCJTemperature());
  Serial.print(",");
  Serial.print(max1.readThermocoupleTemperature());
  Serial.print(",");
  Serial.print(max2.readCJTemperature());
  Serial.print(",");
  Serial.println(max2.readThermocoupleTemperature());
} // End function

// Summary: Used to control the temperature of the insulation chamber
// Input[ControlStatus]: 
void HeatControl(int ControlStatus){
  switch(ControlStatus){
    case LOW_HEAT:
      digitalWrite(RELAY_ONE,HIGH); // Switch on to turn on circuit
      digitalWrite(RELAY_TWO,LOW); // Switch off to prevent short from first resistor
      digitalWrite(RELAY_THREE,LOW); // Switch off to prevent short from second resistor
      break;
    case MEDIUM_HEAT:
      digitalWrite(RELAY_ONE,HIGH); // Switch on to turn on circuit
      digitalWrite(RELAY_TWO,LOW); // Switch off to prevent short from first resistor
      digitalWrite(RELAY_THREE,HIGH); // Switch on to short second resistor
      break;
    case HIGH_HEAT:
      digitalWrite(RELAY_ONE,HIGH); // Switch on to turn on circuit
      digitalWrite(RELAY_TWO,HIGH); // Switch on to short heating circuit
      //digitalWrite(RELAY_THREE,HIGH); // Has no effect
      break;
    case OFF_HEAT:
    default:
      digitalWrite(RELAY_ONE,LOW); // Switch off to open circuit 
      //digitalWrite(RELAY_TWO,HIGH); // Has no effect
      //digitalWrite(RELAY_THREE,); // Has no effect
      break;
  }
} // End function
