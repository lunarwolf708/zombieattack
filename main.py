import time
import machine
import Tufts_ble
import display
import ssd1306

# Initialize the Sniff and Yell classes from your Tufts_ble module
sniffer = Tufts_ble.Sniff(discriminator='!', verbose=True, rssi_range=(-80, 0))
yeller = Tufts_ble.Yell()

# Dictionary to keep track of hits for each team
message_counter = {}
last_message = None
last_time = 0
continuous_duration = 3  # seconds to consider for one hit
human = True
zombie_team = None  # Start as a human, so no zombie team yet


# Initialize breathing LED on pin 0
f = machine.PWM(machine.Pin(0))  
f.freq(50)  # frequency of LED 

# Function to simulate broadcasting a zombie message to nearby humans
def broadcast_zombie_message(team_number):
    message = f"!{team_number}"
    yeller.advertise(name=message)  # Broadcast the team message via BLE
    print(f"Broadcasting message: {message} (You are a zombie for Team {team_number})")
# Set up the buzzer pin
buzzer = machine.PWM(machine.Pin(18))  # Change 18 to your buzzer pin if needed

# Frequencies for the Minecraft zombie noise
frequencies = [120, 100, 80, 150, 120]  # Example frequencies in Hz
durations = [0.3, 0.3, 0.5, 0.5, 0.3]   # Corresponding durations in seconds

def play_zombie_noise():
    for freq, duration in zip(frequencies, durations):
        buzzer.freq(freq)          # Set the frequency
        buzzer.duty_u16(1000)     # Set the duty cycle (adjust as needed)
        time.sleep(duration)       # Wait for the duration
    buzzer.duty_u16(0)  # Turn off the buzzer

# Main loop: sniff for zombie messages while you're human, then broadcast when you're a zombie
while True:
    if human:
        # Breathe an LED so I can test wireless connection on Pico 
        for i in range(0, 65535, 500):  # Increase brightness
            f.duty_u16(i)  # Set duty cycle (brightness)
            time.sleep(0.01)  # Adjust timing for smoothness
            
        for i in range(65535, 0, -500):  # Decrease brightness
            f.duty_u16(i)
            time.sleep(0.01)

        # Scan for nearby Bluetooth messages using the Sniff class
        sniffer.scan(duration=2000)  # Scan for 2 seconds
        message = sniffer.last  # Get the last received message
        
        if message:  # If we received a message
            team_number = message[2:]  # Extract the team number (e.g., !4 becomes "4")

            if message == last_message:
                # Check if we have received the same message for the required duration
                if time.time() - last_time >= continuous_duration:
                    # Increment the hit count for this team
                    if team_number not in message_counter:
                        message_counter[team_number] = 0
                    
                    message_counter[team_number] += 1
                    print(f"Hit for Team {team_number}! Total hits: {message_counter[team_number]}")

                    # Update the display with the new hit count
                    update_display(team_number, message_counter[team_number])

                    # Reset the timer for the next count
                    last_time = time.time()
            else:
                # Reset if a new message is received
                last_message = message
                last_time = time.time()

            # Check if we've reached 3 hits to become a zombie
            if team_number in message_counter and message_counter[team_number] >= 3:
                print(f"You are now a zombie for Team {team_number}!")
                human = False  # You're no longer human
                zombie_team = team_number  # Set your zombie team
        else:
            print("No valid zombie messages received.")
    else:
        # If you're a zombie, start broadcasting your team message
        broadcast_zombie_message(zombie_team)
        play_zombie_noise()

    time.sleep(1)  # Add a slight delay before the next loop

