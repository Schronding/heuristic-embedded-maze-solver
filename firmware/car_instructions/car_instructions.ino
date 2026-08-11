#include <EEPROM.h>

const int ENA = 3; 
const int IN1 = 4; 
const int IN2 = 5;
const int ENB = 11;
const int IN3 = 12;
const int IN4 = 13;

const int FORWARD_SPEED = 150;
const int TURN_SPEED = 130;
const int TIME_TURN_90_DEGREES = 1900;
const int TIME_FORWARD_F = 4300;
const int PAUSE_BETWEEN_COMMANDS = 200;
bool leftMotorTurnFirst = true;

const int EEPROM_ADDR_FLAG = 0;
const int EEPROM_ADDR_LENGTH = 1;
const int EEPROM_ADDR_STRING_START = 2;
const int MAX_COMMAND_LENGTH = 50;

String commandsToExecuteRAM = "";

void moveForward(int speed) {
    if (leftMotorTurnFirst) {
        digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); analogWrite(ENA, speed);
        digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH); analogWrite(ENB, speed);
    } else {
        digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH); analogWrite(ENB, speed);
        digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); analogWrite(ENA, speed);
    }
    
    leftMotorTurnFirst = !leftMotorTurnFirst; 
    
    Serial.println("Moving Forward");
}

void turnLeft(int speed) {
    digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);  analogWrite(ENA, speed);   
    digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH); analogWrite(ENB, speed);  
    Serial.println("Turning Right (on axis)");
}

void turnRight(int speed) {
    digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH); analogWrite(ENA, speed); 
    digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);  analogWrite(ENB, speed); 
    Serial.println("Turning Left (on axis)");
}

void stopMotors() {
    digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); analogWrite(ENA, 0);
    digitalWrite(IN3, LOW); digitalWrite(IN4, LOW); analogWrite(ENB, 0);
    Serial.println("Motors Stopped");
}

void executeInstructions(String instructions) {
    if (instructions.length() == 0) {
        Serial.println("No instructions to execute.");
        return;
    }
    Serial.print("Executing sequence: "); Serial.println(instructions);
    for (int i = 0; i < instructions.length(); i++) {
        char instruction = instructions.charAt(i);
        Serial.print("Processing: "); Serial.println(instruction);

        switch (instruction) {
            case 'F':
                moveForward(FORWARD_SPEED);
                delay(TIME_FORWARD_F);
                stopMotors();
                break;
            case 'R':
                turnRight(TURN_SPEED);
                delay(TIME_TURN_90_DEGREES);
                stopMotors();
                break;
            case 'L':
                turnLeft(TURN_SPEED);
                delay(TIME_TURN_90_DEGREES);
                stopMotors();
                break;
            default:
                Serial.print("Unknown instruction: '"); Serial.print(instruction); Serial.println("'");
                break;
        }
        
        if (i < instructions.length() - 1) {
             delay(PAUSE_BETWEEN_COMMANDS);
        }
    }
    Serial.println("Instruction sequence completed.");
}

void saveStringToEEPROM(const String& str) {
    if (str.length() == 0 || str.length() > MAX_COMMAND_LENGTH) {
        Serial.println("Error: String empty or too long for EEPROM.");
        EEPROM.write(EEPROM_ADDR_FLAG, 0);
        return;
    }
    EEPROM.write(EEPROM_ADDR_FLAG, 'V');
    EEPROM.write(EEPROM_ADDR_LENGTH, str.length());
    for (int i = 0; i < str.length(); i++) {
        EEPROM.write(EEPROM_ADDR_STRING_START + i, str.charAt(i));
    }
    Serial.print("Saved to EEPROM: "); Serial.println(str);
}

String readStringFromEEPROM() {
    if (EEPROM.read(EEPROM_ADDR_FLAG) != 'V') {
        return ""; 
    }
    int len = EEPROM.read(EEPROM_ADDR_LENGTH);
    if (len == 0 || len > MAX_COMMAND_LENGTH) {
      return "";
    }
    char data[len + 1];
    for (int i = 0; i < len; i++) {
        data[i] = EEPROM.read(EEPROM_ADDR_STRING_START + i);
    }
    data[len] = '\0';
    return String(data);
}

void clearEEPROMCommands() {
    EEPROM.write(EEPROM_ADDR_FLAG, 0);
    EEPROM.write(EEPROM_ADDR_LENGTH, 0);
    Serial.println("Commands cleared from EEPROM.");
}

void setup() {
    Serial.begin(9600);

    pinMode(ENA, OUTPUT);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(ENB, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);
    
    stopMotors();
    
    Serial.println("-------------------------------------");
    Serial.println("Car System with EEPROM Initialized");
    Serial.println("Available Serial commands:");
    Serial.println("  'sequence' (e.g.: FFRFLF) -> Execute");
    Serial.println("  '!Ssequence' (e.g.: !SFFRFLF) -> SAVE and execute");
    Serial.println("  '!E' -> Execute from EEPROM");
    Serial.println("  '!C' -> Clear EEPROM");
    Serial.println("-------------------------------------");

    String savedCommands = readStringFromEEPROM();
    if (savedCommands.length() > 0) {
        Serial.print("Commands found in EEPROM: "); Serial.println(savedCommands);
        int startDelaySeconds = 5;
        Serial.print("Waiting "); Serial.print(startDelaySeconds); Serial.println(" seconds before automatic execution...");
        delay(startDelaySeconds * 1000);
        
        Serial.println("Executing automatically from EEPROM...");
        executeInstructions(savedCommands);
    } else {
        Serial.println("No commands in EEPROM for automatic execution at startup.");
    }
    Serial.println("Waiting for new commands via Serial...");
}

void loop() {
    if (Serial.available() > 0) {
        String incomingCommand = Serial.readStringUntil('\n');
        incomingCommand.trim();
        
        if (incomingCommand.length() > 0) {
            Serial.print("Command received via Serial: "); Serial.println(incomingCommand);

            if (incomingCommand.startsWith("!S")) { 
                String sequenceToSave = incomingCommand.substring(2);
                if (sequenceToSave.length() > 0) {
                    saveStringToEEPROM(sequenceToSave);
                    commandsToExecuteRAM = sequenceToSave;
                    executeInstructions(commandsToExecuteRAM);
                } else {
                    Serial.println("!S command without sequence to save.");
                }
            } else if (incomingCommand.equalsIgnoreCase("!E")) { 
                String eepromCommands = readStringFromEEPROM();
                if (eepromCommands.length() > 0) {
                    executeInstructions(eepromCommands);
                } else {
                     Serial.println("Nothing in EEPROM to execute with !E.");
                }
            } else if (incomingCommand.equalsIgnoreCase("!C")) { 
                clearEEPROMCommands();
            } else { 
                commandsToExecuteRAM = incomingCommand;
                executeInstructions(commandsToExecuteRAM);
            }
             Serial.println("Waiting for new commands via Serial...");
        }
    }
}