# import sys
# import argparse
# import socket
# import driver
# import time
# import csv
# import re
# from pynput import keyboard

# # Argument Parsing
# parser = argparse.ArgumentParser(description='Python client to connect to the TORCS SCRC server.')
# parser.add_argument('--host', default='localhost', help='Host IP address')
# parser.add_argument('--port', type=int, default=3001, help='Host port number')
# parser.add_argument('--id', default='SCR', help='Bot ID')
# parser.add_argument('--maxEpisodes', type=int, default=1, help='Max learning episodes')
# parser.add_argument('--maxSteps', type=int, default=0, help='Max steps')
# parser.add_argument('--stage', type=int, default=3, help='Stage')
# parser.add_argument('--manual', action='store_true', help='Enable manual control mode')
# args = parser.parse_args()

# # Establish Socket Connection
# print(f'Connecting to {args.host} on port {args.port}')
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.settimeout(1.0)

# shutdownClient = False
# curEpisode = 0

# d = driver.Driver(args.stage)
# manual_mode = args.manual

# manual_state = {"accel": 0.0, "brake": 0.0, "steer": 0.0, "gear": 1}

# def build_send_string(state):
#     return "".join(f"({key} {value})" for key, value in state.items())

# def parse_received_data(buf):
#     buf = buf.strip('()\x00')
#     data = re.findall(r'\(([^)]+)\)', buf)

#     parsed_data = {}
#     for item in data:
#         parts = item.split(' ')  
#         key = parts[0]  
#         values = parts[1:]

#         try:
#             if len(values) == 1:
#                 parsed_data[key] = float(values[0]) if '.' in values[0] else int(values[0])
#             else:
#                 parsed_data[key] = [float(v) if '.' in v else int(v) for v in values]
#         except ValueError:
#             parsed_data[key] = values  

#     return parsed_data

# # Open CSV Files
# sensor_csv = open('sensor_data.csv', mode='w', newline='')
# sensor_writer = csv.writer(sensor_csv)
# sensor_writer.writerow(["angle", "curLapTime", "damage", "distFromStart", "distRaced", "fuel", "gear", "lastLapTime", "racePos", "rpm", "speedX", "speedY", "speedZ", "trackPos", "z"])

# actuator_csv = open('actuator_data.csv', mode='w', newline='')
# actuator_writer = csv.writer(actuator_csv)
# actuator_writer.writerow(["steer", "accel", "brake"])

# def on_press(key):
#     try:
#         if key.char == 'w': manual_state["accel"] = 0.5
#         elif key.char == 's': manual_state["brake"] = 0.5
#         elif key.char == 'a': manual_state["steer"] = -0.1
#         elif key.char == 'd': manual_state["steer"] = 0.1
#     except AttributeError:
#         pass

# def on_release(key):
#     try:
#         if key.char in ['w', 's']: manual_state["accel"] = manual_state["brake"] = 0.0
#         elif key.char in ['a', 'd']: manual_state["steer"] = 0.0
#     except AttributeError:
#         pass

# if manual_mode:
#     listener = keyboard.Listener(on_press=on_press, on_release=on_release)
#     listener.start()

# while not shutdownClient:
#     while True:
#         try:
#             sock.sendto((args.id + d.init()).encode(), (args.host, args.port))
#             buf, _ = sock.recvfrom(1000)
#             if '***identified***' in buf.decode(): break
#         except socket.error:
#             continue
    
#     while True:
#         try:
#             buf, _ = sock.recvfrom(1000)
#             buf = buf.decode()
#         except socket.error:
#             continue
        
#         if '***shutdown***' in buf:
#             d.onShutDown()
#             shutdownClient = True
#             break
#         elif '***restart***' in buf:
#             d.onRestart()
#             break

#         parsed_data = parse_received_data(buf)

#         # Log Sensor Data
#         sensor_writer.writerow([parsed_data.get(k, "0") for k in ["angle", "curLapTime", "damage", "distFromStart", "distRaced", "fuel", "gear", "lastLapTime", "racePos", "rpm", "speedX", "speedY", "speedZ", "trackPos", "z"]])
#         sensor_csv.flush()

#         # Determine Actuator Values
#         if manual_mode:
#             steer, accel, brake = manual_state["steer"], manual_state["accel"], manual_state["brake"]
#         else:
#             steer = parsed_data.get("steer", 0.0)
#             accel = parsed_data.get("accel", 0.0)
#             brake = parsed_data.get("brake", 0.0)

#         # Log Actuator Data
#         actuator_writer.writerow([steer, accel, brake])
#         actuator_csv.flush()

#         # Send Actuator Commands
#         response = build_send_string(manual_state) if manual_mode else d.drive(buf)
#         sock.sendto(response.encode(), (args.host, args.port))
    
#     curEpisode += 1
#     if curEpisode == args.maxEpisodes:
#         shutdownClient = True

# sock.close()
# sensor_csv.close()
# actuator_csv.close()
# if manual_mode: listener.stop()


# import sys
# import argparse
# import socket
# import driver
# import time
# import csv
# import re
# from pynput import keyboard

# # Argument Parsing
# parser = argparse.ArgumentParser(description='Python client to connect to the TORCS SCRC server.')
# parser.add_argument('--host', action='store', dest='host_ip', default='localhost', help='Host IP address')
# parser.add_argument('--port', action='store', type=int, dest='host_port', default=3001, help='Host port number')
# parser.add_argument('--id', action='store', dest='id', default='SCR', help='Bot ID')
# parser.add_argument('--maxEpisodes', action='store', dest='max_episodes', type=int, default=1, help='Max learning episodes')
# parser.add_argument('--maxSteps', action='store', dest='max_steps', type=int, default=0, help='Max steps')
# parser.add_argument('--track', action='store', dest='track', default=None, help='Track name')
# parser.add_argument('--stage', action='store', dest='stage', type=int, default=3, help='Stage')
# parser.add_argument('--manual', action='store_true', dest='manual', help='Enable manual control mode')
# arguments = parser.parse_args()

# # Establish Socket Connection
# print(f'Connecting to {arguments.host_ip} on port {arguments.host_port}')
# try:
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.settimeout(1.0)
# except socket.error:
#     print('Socket creation failed')
#     sys.exit(-1)

# shutdownClient = False
# curEpisode = 0
# verbose = True

# d = driver.Driver(arguments.stage)
# manual_mode = arguments.manual

# # Manual Control State
# manual_state = {"accel": 0.0, "brake": 0.0, "gear": 1, "steer": 0.0, "clutch": 0.0, "focus": 0, "meta": 0}

# def build_send_string(state):
#     return "".join(f"({key} {value})" for key, value in state.items())

# def parse_received_data(buf):
#     buf = buf.strip('()\x00')  # Clean received string
#     data = re.findall(r'\(([^)]+)\)', buf)  # Extract key-value pairs

#     parsed_data = {}
#     for item in data:
#         parts = item.split(' ')  
#         key = parts[0]  
#         values = parts[1:]  

#         # Convert to appropriate types
#         try:
#             if len(values) == 1:
#                 parsed_data[key] = float(values[0]) if '.' in values[0] else int(values[0])
#             else:
#                 parsed_data[key] = [float(v) if '.' in v else int(v) for v in values]
#         except ValueError:
#             parsed_data[key] = values  

#     return parsed_data

# # Open CSV Files
# sensor_csv = open('sensor_data.csv', mode='w', newline='')
# sensor_writer = csv.writer(sensor_csv)
# sensor_writer.writerow(["angle", "curLapTime", "damage", "distFromStart", "distRaced", "fuel", "gear", "lastLapTime", "racePos", "rpm", "speedX", "speedY", "speedZ", "trackPos", "z"])

# actuator_csv = open('actuator_data.csv', mode='w', newline='')
# actuator_writer = csv.writer(actuator_csv)
# actuator_writer.writerow(["steer", "accel", "brake"])

# # Manual Mode Keyboard Controls
# def on_press(key):
#     try:
#         if key.char == 'w': manual_state["accel"] = 0.5
#         elif key.char == 's': manual_state["brake"] = 0.5
#         elif key.char == 'a': manual_state["steer"] = -0.1
#         elif key.char == 'd': manual_state["steer"] = 0.1
#         elif key.char == 'q': manual_state["gear"] = max(manual_state["gear"] - 1, 1)
#         elif key.char == 'e': manual_state["gear"] += 1
#     except AttributeError:
#         pass

# def on_release(key):
#     if key in [keyboard.Key.esc]: return False
#     try:
#         if key.char in ['w', 's']: manual_state["accel"] = manual_state["brake"] = 0.0
#         elif key.char in ['a', 'd']: manual_state["steer"] = 0.0
#     except AttributeError:
#         pass

# if manual_mode:
#     listener = keyboard.Listener(on_press=on_press, on_release=on_release)
#     listener.start()

# # Main Communication Loop
# while not shutdownClient:
#     while True:
#         try:
#             sock.sendto((arguments.id + d.init()).encode(), (arguments.host_ip, arguments.host_port))
#             buf, _ = sock.recvfrom(1000)
#             if '***identified***' in buf.decode(): break
#         except socket.error:
#             continue
    
#     while True:
#         try:
#             buf, _ = sock.recvfrom(1000)
#             buf = buf.decode()
#         except socket.error:
#             continue
        
#         if '***shutdown***' in buf:
#             d.onShutDown()
#             shutdownClient = True
#             break
#         elif '***restart***' in buf:
#             d.onRestart()
#             break
        
#         parsed_data = parse_received_data(buf)

#         # Log Sensor Data
#         sensor_writer.writerow([parsed_data.get(k, "0") for k in ["angle", "curLapTime", "damage", "distFromStart", "distRaced", "fuel", "gear", "lastLapTime", "racePos", "rpm", "speedX", "speedY", "speedZ", "trackPos", "z", "opponents"]])


#         # Determine Actuator Values
#         if manual_mode:
#             steer = manual_state["steer"]
#             accel = manual_state["accel"]
#             brake = manual_state["brake"]
#         else:
#             steer = float(re.search(r"\(steer ([\-0-9\.]+)\)", response).group(1)) if re.search(r"\(steer ([\-0-9\.]+)\)", response) else 0.0
#             accel = float(re.search(r"\(accel ([\-0-9\.]+)\)", response).group(1)) if re.search(r"\(accel ([\-0-9\.]+)\)", response) else 0.0
#             brake = float(re.search(r"\(brake ([\-0-9\.]+)\)", response).group(1)) if re.search(r"\(brake ([\-0-9\.]+)\)", response) else 0.0

#         # Log Actuator Data
#         actuator_writer.writerow([steer, accel, brake])

#         # Send Actuator Commands
#         response = build_send_string(manual_state) if manual_mode else d.drive(buf)
#         sock.sendto(response.encode(), (arguments.host_ip, arguments.host_port))
    
#     curEpisode += 1
#     if curEpisode == arguments.max_episodes:
#         shutdownClient = True

# # Close Files and Listener
# sock.close()
# sensor_csv.close()
# actuator_csv.close()
# if manual_mode: listener.stop()



import sys
import argparse
import socket
import driver
import time
import csv
from pynput import keyboard
from pathlib import Path
import torch
import torch.nn as nn
from torcsNet import TORCSNet
import numpy as np

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
    print('Connected')
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

model = TORCSNet(input_size=37, hidden_size=512, num_gear_classes=4, num_clutch_classes=2)
model.load_state_dict(torch.load("best_model.pt", map_location=torch.device('cpu')))
model.eval()

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

# sensor_cols = ['Angle', ' CurrentLapTime', ' Damage', ' DistanceFromStart', ' DistanceCovered', 
#                 ' FuelLevel', ' LastLapTime', 'RacePosition', ' RPM', 
#                ' SpeedX', ' SpeedY', ' SpeedZ', ' Track_1', 'Track_2', 'Track_3', 
#                'Track_4', 'Track_5', 'Track_6', 'Track_7', 'Track_8', 'Track_9', 
#                'Track_10', 'Track_11', 'Track_12', 'Track_13', 'Track_14', 'Track_15', 
#                'Track_16', 'Track_17', 'Track_18', 'Track_19', 'TrackPosition', 
#                 ' WheelSpinVelocity_1', 'WheelSpinVelocity_2', 'WheelSpinVelocity_3', 
#                'WheelSpinVelocity_4', 'Z']
        # input_features = [
        #     parsed_data.get("angle", 0.0), parsed_data.get("currLapTime", 0.0), parsed_data.get("damage", 0.0),
        #     parsed_data.get("distFromStart", 0.0), parsed_data.get("distRaced", 0.0), parsed_data.get("focus", 0.0),
        #     parsed_data.get("fuel", 0.0), parsed_data.get("lastLapTime", 0.0), parsed_data.get("racePos", 0.0), 
        #     parsed_data.get("rpm", 0.0),
        #     parsed_data.get("speedX", 0.0), parsed_data.get("speedY", 0.0), parsed_data.get("speedZ", 0.0),
        #     parsed_data.get("track", [0.0]*19), parsed_data.get("trackPos", 0.0),
        #     parsed_data.get("wheelSpinVel", [0.0]*4)[0], parsed_data.get("z", 0.0)
        #     # parsed.get("angle", 0.0), parsed.get("trackPos", 0.0),
            
        #     # parsed.get("rpm", 0.0), parsed.get("fuel", 0.0),
        #     # parsed_data.get("wheelSpinVel", [0.0]*4)[0],  # optionally use avg or max
        #     # parsed_data.get("wheelSpinVel", [0.0]*4)[1],
        #     # parsed_data.get("wheelSpinVel", [0.0]*4)[2],
        #     # parsed_data.get("wheelSpinVel", [0.0]*4)[3],
        # ]
        key = ["angle", "curLapTime", "damage", "distFromStart", "distRaced",
                "fuel", "lastLapTime", "racePos", "rpm", "speedX", 
                "speedY", "speedZ", "track", "trackPos", "wheelSpinVel", "z"]
        input_features = []

        # for k in key:
        #     val = parsed_data.get(k, 0.0)
        #     if isinstance(val, list):
        #         input_features.extend(val)
        #     else:
        #         input_features.append(val)
        normalized = []

        for k in key:
            val = parsed_data.get(k, 0.0)
            if isinstance(val, list):
                # Example: track sensors range from 0 to 200
                norm_vals = [min(1.0, v / 200.0) for v in val]
                normalized.extend(norm_vals)
            else:
                if k == "speedX":
                    normalized.append(val / 300.0)  # Assuming 300 km/h max
                elif k == "speedY":
                    normalized.append(val / 100.0)  # Side speed
                elif k == "angle":
                    normalized.append(val / 3.1415)  # Normalize between -1 and 1
                elif k == "rpm":
                    normalized.append(val / 10000.0)  # Scale based on max RPM
                else:
                    normalized.append(val)

        input_tensor = torch.tensor(normalized, dtype=torch.float32).unsqueeze(0)

        # Predict using model
        with torch.no_grad():
            shared_out = model.shared(input_tensor)
            continuous_out = model.continuous_head(shared_out)
            gear_logits = model.gear_head(shared_out)
            clutch_logits = model.clutch_head(shared_out)

        csv_writer.writerow([parsed_data.get(k, "0") for k in ["angle", "curLapTime", "damage", "distFromStart", "distRaced", "focus",
                                                             "fuel", "gear", "lastLapTime", "opponents", "racePos", "rpm", "speedX", 
                                                             "speedY", "speedZ", "track", "trackPos", "wheelSpinVel", "z"]])
        steer, brake, accel = continuous_out.squeeze().numpy()
        gear = torch.argmax(gear_logits, dim=1).item()
        clutch = torch.argmax(clutch_logits, dim=1).item()

        # print('steer : ' + str(steer))
        # print('brake : ' + str(brake))
        # print('accel : ' + str(accel))

        # Clip to valid ranges
        manual_state["steer"] = float(np.clip(steer, -1.0, 1.0))
        manual_state["accel"] = float(np.clip(accel, 0.0, 1.0))
        manual_state["brake"] = float(np.clip(brake, 0.0, 1.0))
        manual_state["clutch"] = float(clutch)

        if manual_state["accel"] == 0:
            manual_state["accel"] = 1

        if manual_state["clutch"] > 0.5:
            manual_state["clutch"] = 1

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