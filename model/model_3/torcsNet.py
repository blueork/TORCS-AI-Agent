import torch
import torch.nn as nn

# Neural Network Model
# Neural Network Model
class TORCSNet(nn.Module):
    def __init__(self, input_size, num_accel_classes, num_brake_classes, num_gear_classes, num_clutch_classes=2):
        super(TORCSNet, self).__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),        
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        self.steering_head = nn.Linear(128, 1)  # Steering (continuous, [-1, 1])
        self.accel_head = nn.Linear(128, num_accel_classes)  # Acceleration (discrete)
        self.brake_head = nn.Linear(128, num_brake_classes)  # Braking (discrete)
        self.gear_head = nn.Linear(128, num_gear_classes)  # Gear (discrete)
        self.clutch_head = nn.Linear(128, num_clutch_classes)  # Clutch (discrete)
        
    def forward(self, x):
        shared = self.shared(x)
        steering_out = torch.tanh(self.steering_head(shared))  # [-1, 1]
        accel_out = self.accel_head(shared)  # Logits
        brake_out = self.brake_head(shared)  # Logits
        gear_out = self.gear_head(shared)  # Logits
        clutch_out = self.clutch_head(shared)  # Logits
        return steering_out, accel_out, brake_out, gear_out, clutch_out