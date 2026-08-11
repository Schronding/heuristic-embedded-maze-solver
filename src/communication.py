import serial
import time
import sys

ARDUINO_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

def handle_arduino_communication(results_ranking):
    if not results_ranking:
        print("No paths found to send to Arduino.")
        return

    print("\n--- ARDUINO COMMUNICATION MODE ---")
    print(f"Attempting to connect to Arduino on port: {ARDUINO_PORT}")

    try:
        with serial.Serial(port=ARDUINO_PORT, baudrate=BAUD_RATE, timeout=2) as arduino:
            print(f"Successful connection with {arduino.name}!")
            print("Waiting 2 seconds for Arduino to initialize...")
            time.sleep(2)

            while arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"Arduino (startup message): {line}")

            while True:
                print("\n--- ARDUINO COMMAND MENU ---")
                prompt_message = (
                    f"  - Ranking (0 to {len(results_ranking)-1}) or '!S<ranking>' (e.g., !S0) -> SAVE and Execute\n"
                    f"  - '!E' -> EXECUTE from EEPROM\n"
                    f"  - '!C' -> CLEAR EEPROM\n"
                    f"  - 's' -> EXIT sending mode\n"
                    "Enter your command: "
                )
                user_command = input(prompt_message).strip()
                
                if user_command.lower() == 's':
                    print("Exiting communication mode.")
                    break

                instructions_to_send = ""

                if user_command.upper() in ['!E', '!C']:
                    instructions_to_send = user_command.upper()
                
                elif user_command.upper().startswith("!S"):
                    try:
                        rank_str = user_command[2:]
                        rank_idx = int(rank_str)
                        if 0 <= rank_idx < len(results_ranking):
                            algo_name, data = results_ranking[rank_idx]
                            instructions_to_send = "!S" + data['instructions']
                        else:
                            print(f"Error: Ranking '{rank_idx}' out of range.")
                            continue
                    except (ValueError, IndexError):
                        print(f"Error: Invalid command '{user_command}'. Use format like '!S0'.")
                        continue
                else:
                    try:
                        rank_idx = int(user_command)
                        if 0 <= rank_idx < len(results_ranking):
                            algo_name, data = results_ranking[rank_idx]
                            instructions_to_send = "!S" + data['instructions']
                        else:
                            print(f"Error: Ranking '{rank_idx}' out of range.")
                            continue
                    except ValueError:
                        print(f"Error: Unrecognized command '{user_command}'.")
                        continue
                
                if instructions_to_send:
                    print(f"Sending to Arduino: \"{instructions_to_send}\"")
                    arduino.write((instructions_to_send + '\n').encode('utf-8'))
                    
                    time.sleep(0.5)
                    while arduino.in_waiting > 0:
                        response = arduino.readline().decode('utf-8', errors='ignore').strip()
                        if response:
                            print(f"Arduino says: {response}")

    except serial.SerialException as e:
        print(f"*** CONNECTION ERROR ***")
        print(f"Could not connect to port '{ARDUINO_PORT}'.")
        print(f"Details: {e}")
        print("Please verify the Arduino is connected and no other program is using the port.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")