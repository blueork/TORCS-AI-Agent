import sys

sys.path.insert(1, '../model_1/')

import argparse
import socket
import driver
import time
import csv
from pynput import keyboard
from pathlib import Path
import torch
import torch.nn as nn
import numpy as np
import joblib
from torcsNet import TORCSNet

parser = argparse.ArgumentParser(description='Python client to connect to the TORCS SCRC server.')
parser.add_argument('--host', action='store', dest='host_ip', default='localhost', help='Host IP address')
parser.add_argument('--port', action='store', type=int, dest='host_port', default=3001, help='Host port number')
parser.add_argument('--id', action='store', dest='id', default='SCR', help='Bot ID')
parser.add_argument('--maxEpisodes', action='store', dest='max_episodes', type=int, default=1, help='Max learning episodes')
parser.add_argument('--maxSteps', action='store', dest='max_steps', type=int, default=0, help='Max steps')
parser.add_argument('--track', action='store', dest='track', default=None, help='Track name')
parser.add_argument('--stage', action='store', dest='stage', type=int, default=3, help='Stage')
parser.add_argument('--manual', action='store_true', dest='manual', help='Enable manual control mode')
arguments = parser.parse_args()

print(f'Connecting to {arguments.host_ip} on port {arguments.host_port}')

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1.0)
    print('Connected to WTORCS')
except socket.error:
    print('Socket creation failed')
    sys.exit(-1)

shutdownClient = False
curEpisode = 0
verbose = True

d = driver.Driver(arguments.stage)
manual_mode = arguments.manual

manual_state = {"accel": 0.0, "brake": 0.0, "gear": 1, "steer": 0.0, "clutch": 0.0, "focus": 0, "meta": 0}

def build_send_string(state):
    return "".join(f"({key} {value})" for key, value in state.items())

import re

def parse_received_data(buf):
    buf = buf.strip()  # Trim whitespace
    buf = buf.strip('()\x00')  # Remove outer parentheses and null character
    data = re.findall(r'\(([^)]+)\)', buf)  # Extract key-value pairs

    parsed_data = {}
    for item in data:
        parts = item.split(' ')  # Split key and values
        key = parts[0]  # First part is the key
        values = parts[1:]  # Remaining parts are values

        # Convert to appropriate types
        try:
            if len(values) == 1:
                parsed_data[key] = float(values[0]) if '.' in values[0] else int(values[0])
            else:
                parsed_data[key] = [float(v) if '.' in v else int(v) for v in values]
        except ValueError:
            parsed_data[key] = values  # Keep as list of strings if conversion fails

    return parsed_data

# check if the specified file exists or not
my_file = Path("./torcs_sensor_data.csv")
# if it exists we do not need to add column headers
if my_file.is_file():
    print("File already exists")
    add_column_header = False
else:
    add_column_header = True

csv_file = open('torcs_sensor_data.csv', mode='a', newline='')
csv_writer = csv.writer(csv_file)
if add_column_header == True:
    csv_writer.writerow(["angle", "curLapTime", "damage", "distFromStart", "distRaced", "focus",
                         "fuel", "gear", "lastLapTime", "opponents", "racePos", "rpm", "speedX", 
                        "speedY", "speedZ", "track", "trackPos", "wheelSpinVel", "z"])


# check if the specified file exists or not
my_file = Path("./torcs_actuator_data.csv")
# if it exists we do not need to add column headers
if my_file.is_file():
    print("File already exists")
    add_column_header = False
else:
    add_column_header = True

csv_file_2 = open('torcs_actuator_data.csv', mode='a', newline = '')
csv_writer_2 = csv.writer(csv_file_2)
if add_column_header == True:
    csv_writer_2.writerow(["accel", "brake", "gear", "steer", "clutch", "focus" , "meta"])

def on_press(key):
    try:
        if key.char == 'w': manual_state["accel"] = 0.5
        elif key.char == 's': manual_state["brake"] = 0.5
        elif key.char == 'a': manual_state["steer"] = -0.1
        elif key.char == 'd': manual_state["steer"] = 0.1
        elif key.char == 'u': manual_state["gear"] = max(manual_state["gear"] - 1, 0)
        elif key.char == 'i': manual_state["gear"] = min(manual_state["gear"] + 1, 6)
        elif key.char == 'c': manual_state["clutch"] = 1
    except AttributeError:
        pass

def on_release(key):
    if key in [keyboard.Key.esc]: return False
    try:
        if key.char in ['w', 's']: manual_state["accel"] = manual_state["brake"] = 0.0
        elif key.char in ['a', 'd']: manual_state["steer"] = 0.0
        elif key.char in ['c']: manual_state["clutch"] = 0.0
    except AttributeError:
        pass

if manual_mode:
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

# Set random seed for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

input_size = 32
num_accel_classes = 2  # e.g., {0, 1}
num_brake_classes = 2  # e.g., {0, 1}
num_gear_classes = 4 # e.g., {-1, 0, 1, 2, 3, 4, 5, 6}
num_clutch_classes = 2
model = TORCSNet(input_size, num_accel_classes, num_brake_classes, num_gear_classes, num_clutch_classes).to(device)
model.load_state_dict(torch.load('../model_1/best_model_old.pt', map_location=device))
model.eval()
scaler = joblib.load('./scaler.pkl')
game_start = True
cool_down = 700
reverse_engaged = False

while not shutdownClient:
    while True:
        try:
            sock.sendto((arguments.id + d.init()).encode(), (arguments.host_ip, arguments.host_port))
            buf, _ = sock.recvfrom(1000)
            if '***identified***' in buf.decode(): break
        except socket.error:
            continue
    
    while True:
        try:
            buf, _ = sock.recvfrom(1000)
            buf = buf.decode()
        except socket.error:
            continue
        
        if '***shutdown***' in buf:
            d.onShutDown()
            shutdownClient = True
            break
        elif '***restart***' in buf:
            d.onRestart()
            break
        
        

        parsed_data = parse_received_data(buf)

        key = ["angle", "distRaced", "lastLapTime", "rpm", "speedX", 
                "speedY", "speedZ", "track", "trackPos", "wheelSpinVel", "z"]
        input_features = []

        for k in key:
            val = parsed_data.get(k, 0.0)
            if isinstance(val, list):
                input_features.extend(val)
            else:
                input_features.append(val)

        if len(input_features) != 32:
            raise ValueError(f"Expected 32 sensors, got {len(input_features)}")

        try:
            scaled_sensors = scaler.transform([input_features])
        except Exception as e:
            print(f"Scaler error: {e}")
            break

        # Convert to tensor
        inputs = torch.tensor(scaled_sensors, dtype=torch.float32).to(device)

        with torch.no_grad():
            steering_out, accel_out, brake_out, gear_out, clutch_out = model(inputs)

        steering = steering_out.item()  # [-1, 1]
        accel = torch.argmax(accel_out, dim=1).item()  # e.g., 0 or 1
        brake = torch.argmax(brake_out, dim=1).item()  # e.g., 0 or 1
        gear_idx = torch.argmax(gear_out, dim=1).item()  # e.g., 0 to 7
        clutch = torch.argmax(clutch_out, dim=1).item()  # e.g., 0 or 1

        manual_state["steer"] = steering
        manual_state["accel"] = accel
        manual_state["brake"] = brake

        if accel == 1 and brake == 1:
            manual_state["brake"] = 0

        # manual_state["gear_idx"] = gear_idx
        # manual_state["clutch"] == clutch

        print(f"Steering={steering:.4f}, Accel={accel}, Brake={brake}, Gear={gear_idx}, Clutch={clutch}")
        
        # csv_writer.writerow([parsed_data.get(k, "0") for k in ["angle", "curLapTime", "damage", "distFromStart", "distRaced", "focus",
        #                                                      "fuel", "gear", "lastLapTime", "opponents", "racePos", "rpm", "speedX", 
        #                                                      "speedY", "speedZ", "track", "trackPos", "wheelSpinVel", "z"]])
        # steer, brake, accel = continuous_out.squeeze().numpy()
        # gear = torch.argmax(gear_logits, dim=1).item()
        # clutch = torch.argmax(clutch_logits, dim=1).item()

        # print('steer : ' + str(steer))
        # print('brake : ' + str(brake))
        # print('accel : ' + str(accel))

        # Clip to valid ranges
        # manual_state["steer"] = float(np.clip(steer, -1.0, 1.0))
        # manual_state["accel"] = float(np.clip(accel, 0.0, 1.0))
        # manual_state["brake"] = float(np.clip(brake, 0.0, 1.0))
        # manual_state["clutch"] = float(clutch)

        # if manual_state["accel"] == 0:
        #     manual_state["accel"] = 1

        # if manual_state["clutch"] > 0.5:
        #     manual_state["clutch"] = 1

        # print(manual_state) 

        # manual_state['clutch'] = 0
        # print(parsed_data.get('clutch'))
        # if game_start == False and parsed_data.get('distRaced') > 100:
        # # if cool_down <= 0 :
        #     cool_down = 700
        #     current_gear = parsed_data.get('gear')
        #     current_rpm = parsed_data.get('rpm')
        #     current_clutch = 0

        #     if current_rpm >= 8500 :
        #         current_gear = min(current_gear + 1, 6)
        #         current_clutch = 1
        #     elif current_rpm <= 1000 :
        #         current_gear = max(current_gear - 1, -1)
        #         current_clutch = 1
        
        #     manual_state['clutch'] = current_clutch
        #     manual_state['gear'] = current_gear

        manual_state['clutch'] = 0
        clutch_value = 0
        gear_value = manual_state['gear']
        speedX = int(parsed_data.get('speedX'))
        
        # print(speedX)
        # print(parsed_data.get('trackPos'))
        # parsed_data.get('trackPos') >= -1.0 and parsed_data.get('trackPos') <= 1.0

        if speedX == 0 and parsed_data.get('gear') >= 1 and parsed_data.get('distRaced') > 0 and reverse_engaged == False and (parsed_data.get('trackPos') < -1 or parsed_data.get('trackPos') > 1):
            reverse_engaged = True
            clutch_value = 1
            gear_value = -1
            steering = 0
        elif reverse_engaged == True and parsed_data.get('trackPos') >= -1.0 and parsed_data.get('trackPos') <= 1.0:
            # print("Does it come in here?")
            reverse_engaged = False
            gear_value = 1
            clutch_value = 1
        elif speedX <= 50 and gear_value == 2 :
            gear_value = 1
            clutch_value = 1
        elif speedX <= 80 and gear_value == 3 :
            gear_value = 2
            clutch_value = 1
        elif speedX <= 110 and gear_value == 4 :
            gear_value = 3
            clutch_value = 1            
        elif speedX <= 140 and gear_value == 5 :
            gear_value = 4
            clutch_value = 1            
        elif speedX <= 170 and gear_value == 6 :
            gear_value = 5
            clutch_value = 1            
        elif speedX > 50 and gear_value == 1:
            gear_value = 2
            clutch_value = 1
        elif speedX > 80 and gear_value == 2:
            gear_value = 3
            clutch_value = 1
        elif speedX > 110 and gear_value == 3:
            gear_value = 4
            clutch_value = 1            
        elif speedX > 140 and gear_value == 4:
            gear_value = 5
            clutch_value = 1
        elif speedX > 170 and gear_value == 15:
            gear_value = 6
            clutch_value = 1            
        
        manual_state["clutch"] = clutch_value
        manual_state['gear'] = gear_value

        # cool_down -= 1
        print(manual_state) 

        # csv_writer_2.writerow([parsed_data.get(k, "0") for k in ["accel", "brake", "gear", "steer"]])
        if manual_mode:
            actuator_data = [
                manual_state["accel"], manual_state["brake"], manual_state["gear"],
                manual_state["steer"], manual_state["clutch"], manual_state["focus"], manual_state["meta"]
            ]
        else:
            actuator_data = [d.control.getAccel(), d.control.getBrake(), d.control.getGear(),
                     d.control.getSteer(), d.control.getClutch(), d.control.getFocus(), d.control.getMeta()]

        game_start = False

        # Write actuator data to torcs_actuators.csv
        csv_writer_2.writerow(actuator_data)

        response = build_send_string(manual_state) if manual_mode else d.drive(buf)
        sock.sendto(response.encode(), (arguments.host_ip, arguments.host_port))
    
    curEpisode += 1
    if curEpisode == arguments.max_episodes:
        shutdownClient = True

sock.close()
csv_file.close()
csv_file_2.close
if manual_mode: listener.stop()